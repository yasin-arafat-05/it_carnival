"""
====================================================================
Simple LangGraph Workflow Template (with Tools + HITL) - Boilerplate
====================================================================
Generic starter workflow. Follows the same pattern as your
nearby_product_finder_wkf, but adds a Human-In-The-Loop (HITL)
approval step before a "sensitive" tool call (place_order).

Pattern:
    AgentState -> agent (LLM + tools bind) -> conditional edge
        -> normal tool needed        -> tools node -> back to agent
        -> sensitive tool needed     -> human_approval node (interrupt)
              -> approved   -> tools node -> back to agent
              -> rejected   -> END (cancelled message)
        -> no tool needed            -> END
"""

import os
from typing import List, Optional, Union
from uuid import UUID
from pydantic import BaseModel

from langchain_core.tools import tool
from langchain_core.messages import (
    HumanMessage, SystemMessage, AIMessage, ToolMessage, BaseMessage
)
from langchain_groq import ChatGroq

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import interrupt, Command
from typing_extensions import Annotated

from app.core.config import CONFIG


# =====================================================================
# 1. STATE DEFINITION
# =====================================================================
# The `messages` field uses LangGraph's special reducer (add_messages),
# which means new messages get APPENDED, not replaced. This is the
# standard pattern for a tool-calling agent.

class AgentState(BaseModel):
    model_config = {"arbitrary_types_allowed": True}

    user_question: str
    current_user_id: Union[str, UUID, int]
    messages: Annotated[List[BaseMessage], add_messages] = []
    final_answer: str = ""
    order_cancelled: bool = False


# =====================================================================
# 2. TOOLS - put your actual business logic tools here
# =====================================================================
# `place_order` is marked as a "sensitive" tool below (see
# SENSITIVE_TOOLS) — it will always go through human approval first.

@tool
def get_weather(city: str) -> str:
    """Given a city name, return current weather info for that city."""
    # Real weather API call would go here
    return f"Weather in {city} is currently sunny, 32°C."


@tool
def search_product(keyword: str) -> str:
    """Search for a product by keyword and return matching product names."""
    # Your real DB query would go here (like your fetch_categories_from_db)
    dummy_db = ["Samsung Phone Case", "Facewash - Himalaya", "Cotton Shirt"]
    matches = [p for p in dummy_db if keyword.lower() in p.lower()]
    return f"Found: {matches}" if matches else "No matching product found."


@tool
def place_order(product_name: str, quantity: int) -> str:
    """Place an order for a product. This is a sensitive action that
    changes real data, so it requires human confirmation first."""
    # Real order-placement DB write would go here
    return f"Order placed: {quantity} x {product_name}."


TOOLS = [get_weather, search_product, place_order]

# Any tool name listed here will trigger a human-approval interrupt
# BEFORE it is executed.
SENSITIVE_TOOLS = {"place_order"}


# =====================================================================
# 3. LLM SETUP + TOOL BINDING
# =====================================================================
model_name = getattr(CONFIG, "LLM_MODEL_NAME", None) or os.getenv("LLM_MODEL_NAME") or "openai/gpt-oss-20b"
groq_api_key = CONFIG.GROQ_API_KEY or os.getenv("GROQ_API_KEY")
llm = ChatGroq(model=model_name, groq_api_key=groq_api_key, temperature=0.3)
llm_with_tools = llm.bind_tools(TOOLS)




# =====================================================================
# 4. NODE DEFINITIONS
# =====================================================================

def agent_node(state: AgentState) -> AgentState:
    """
    Main reasoning node. The LLM decides whether to answer directly
    or call a tool.
    """
    try:
        system_prompt = SystemMessage(content=(
            "You are a helpful AI assistant. Answer the user's question. "
            "Use the given tools (weather / product search / place_order) "
            "when needed. If no tool is needed, answer directly."
        ))

        # On first call, add the user question as a HumanMessage
        if not state.messages:
            state.messages = [HumanMessage(content=state.user_question)]

        response = llm_with_tools.invoke([system_prompt] + state.messages)
        state.messages = state.messages + [response]

        # No tool call -> this is the final answer
        if not getattr(response, "tool_calls", None):
            state.final_answer = response.content

        return state
    except Exception as e:
        print(f"[agent_node] Error: {e}")
        state.final_answer = "Sorry, something went wrong."
        return state


def human_approval_node(state: AgentState) -> AgentState:
    """
    HITL node. Pauses the graph with interrupt() and waits for a human
    decision before letting a sensitive tool (place_order) actually run.

    Resume from the caller side with:
        Command(resume={"approved": True})   # or False
    """
    last_message = state.messages[-1]
    tool_call = last_message.tool_calls[0]

    print("Waiting for human approval... sending interrupt to caller.")
    decision = interrupt({
        "type": "request_approval",
        "message": f"Confirm this action? -> {tool_call['name']}({tool_call['args']})",
        "tool_call_id": tool_call["id"],
    })

    if decision.get("approved"):
        # Approved -> do nothing here, let it flow into the tools node
        return state

    # Rejected -> cancel. We must still answer the pending tool_call
    # with a ToolMessage, otherwise the LLM message history becomes invalid.
    state.messages = state.messages + [
        ToolMessage(
            content="User rejected this action. Order was not placed.",
            tool_call_id=tool_call["id"],
        )
    ]
    state.order_cancelled = True
    state.final_answer = "Okay, I've cancelled that order as you requested."
    return state


# Prebuilt ToolNode - automatically executes any registered tool
tool_node = ToolNode(tools=TOOLS)


# =====================================================================
# 5. ROUTING FUNCTIONS
# =====================================================================

def route_after_agent(state: AgentState) -> str:
    """
    Decide where to go after the agent node:
      - no tool call            -> END
      - sensitive tool call     -> human_approval (needs confirmation)
      - normal tool call        -> tools (run directly)
    """
    last_message = state.messages[-1]
    tool_calls = getattr(last_message, "tool_calls", None)

    if not tool_calls:
        return "end"

    if tool_calls[0]["name"] in SENSITIVE_TOOLS:
        return "needs_approval"

    return "safe_tool"


def route_after_approval(state: AgentState) -> str:
    """After human_approval_node: go to tools if approved, else END."""
    return "end" if state.order_cancelled else "safe_tool"


# =====================================================================
# 6. GRAPH BUILD
# =====================================================================
AGENT = "Agent"
TOOLS_NODE = "Tools"
HUMAN_APPROVAL = "Human_Approval"

workflow = StateGraph(state_schema=AgentState)

workflow.add_node(AGENT, agent_node)
workflow.add_node(TOOLS_NODE, tool_node)
workflow.add_node(HUMAN_APPROVAL, human_approval_node)

workflow.set_entry_point(AGENT)

workflow.add_conditional_edges(
    AGENT,
    route_after_agent,
    {
        "end": END,
        "needs_approval": HUMAN_APPROVAL,
        "safe_tool": TOOLS_NODE,
    },
)

workflow.add_conditional_edges(
    HUMAN_APPROVAL,
    route_after_approval,
    {
        "end": END,
        "safe_tool": TOOLS_NODE,
    },
)

# After a tool runs, go back to the agent (to produce the final answer)
workflow.add_edge(TOOLS_NODE, AGENT)

# Alias graph for worker imports
demo_wkf = workflow



# =====================================================================
# 7. TESTING BLOCK - shows how to trigger and then resume the interrupt
# =====================================================================
if __name__ == "__main__":
    memory = InMemorySaver()
    app = workflow.compile(checkpointer=memory)

    config = {"configurable": {"thread_id": "test_thread_1"}}

    # Step 1: normal call, will pause at human_approval_node
    initial_state = AgentState(
        user_question="Place an order for 2 Cotton Shirts.",
        current_user_id=1,
    )
    result = app.invoke(initial_state, config=config)

    if "__interrupt__" in result:
        interrupt_payload = result["__interrupt__"][0].value
        print("\n--- INTERRUPT RECEIVED ---")
        print(interrupt_payload)

        # Step 2: simulate the user approving the action from frontend
        final_result = app.invoke(
            Command(resume={"approved": True}),
            config=config,
        )
        print("\n--- FINAL ANSWER AFTER APPROVAL ---")
        print(final_result["final_answer"])
    else:
        print("\n--- FINAL ANSWER (no approval needed) ---")
        print(result["final_answer"])