"""
====================================================================
Digital Wallet Support AI Assistant Workflow (LangGraph)
====================================================================
Official AI Support assistant workflow for Digital Wallet.
Answers user queries on transfer limits, money requests, false transaction
reversals, security, and account audit logs.
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

class AgentState(BaseModel):
    model_config = {"arbitrary_types_allowed": True}

    user_question: str
    current_user_id: Union[str, UUID, int]
    messages: Annotated[List[BaseMessage], add_messages] = []
    final_answer: str = ""
    action_cancelled: bool = False


# =====================================================================
# 2. TOOLS - Wallet Support & FAQ Tools
# =====================================================================

@tool
def get_wallet_faq(topic: str) -> str:
    """Given a query topic (limits, send, request, disputes, reversal, ledger, roles), returns authoritative wallet rules."""
    topic_lower = topic.lower()
    if "limit" in topic_lower or "send" in topic_lower or "transfer" in topic_lower:
        return (
            "Digital Wallet Transfer Rules & Limits:\n"
            "• Single Transaction Maximum: BDT 20,000.00\n"
            "• Daily Transfer Limit: BDT 50,000.00 per user per day\n"
            "• Security Confirmation: All transfers require a 5-second press-and-hold confirmation inside the modal."
        )
    elif "dispute" in topic_lower or "false" in topic_lower or "reversal" in topic_lower or "refund" in topic_lower:
        return (
            "False Transaction Reversal & Dispute Process:\n"
            "1. Open Transaction History ➔ click the completed outgoing transfer ➔ click 'Report False Transaction'.\n"
            "2. The receiver is notified and can Accept ('Confirm & Allow Refund') or Reject ('Deny') the claim.\n"
            "3. The Admin reviews the claim in the Admin Control Center and executes the atomic refund from receiver to sender."
        )
    elif "request" in topic_lower or "ask" in topic_lower:
        return (
            "Money Request Feature:\n"
            "• Navigate to 'Request Money' ➔ enter the payer's username/email and amount.\n"
            "• The payer can review, accept, or decline incoming requests directly from their dashboard."
        )
    elif "admin" in topic_lower or "role" in topic_lower:
        return (
            "Roles & Permissions:\n"
            "• USER role: Financial transactions (Send Money, Request Money, History, Ledger Audit).\n"
            "• ADMIN role: Admin Control Center, System-Wide Transaction Audit, Dispute Reversal Execution, User Admin Promotion."
        )
    elif "ledger" in topic_lower or "audit" in topic_lower:
        return (
            "Double-Entry Ledger System:\n"
            "• Every financial transaction automatically creates DEBIT and CREDIT audit records.\n"
            "• View full audit history under Transaction History ➔ Double-Entry Ledger Audit."
        )
    else:
        return (
            "Digital Wallet Customer Care:\n"
            "We provide secure peer-to-peer transfers with BDT 20,000 single and BDT 50,000 daily limits, "
            "5-second hold confirmation, false transaction reversal disputes, and double-entry audit logging."
        )


@tool
def request_admin_investigation(transaction_reference: str, reason: str) -> str:
    """Submits a request to escalate a transaction dispute to admin for manual investigation."""
    return f"Admin investigation requested for reference '{transaction_reference}'. Reason: {reason}."


TOOLS = [get_wallet_faq, request_admin_investigation]
SENSITIVE_TOOLS = {"request_admin_investigation"}


# =====================================================================
# 3. LLM SETUP + TOOL BINDING (Groq LLM)
# =====================================================================
groq_api_key = (
    getattr(CONFIG, "GROQ_API_KEY", None)
    or os.getenv("GROQ_API_KEY")
    or os.getenv("GROQ_API_TOKEN")
)
model_name = (
    getattr(CONFIG, "LLM_MODEL_NAME", None)
    or os.getenv("LLM_MODEL_NAME")
    or "llama-3.3-70b-versatile"
)

try:
    if groq_api_key:
        llm = ChatGroq(model=model_name, groq_api_key=groq_api_key, temperature=0.3)
        llm_with_tools = llm.bind_tools(TOOLS)
    else:
        llm_with_tools = None
except Exception as err:
    print(f"[demo_workflow] Failed to initialize ChatGroq: {err}")
    llm_with_tools = None


# =====================================================================
# 4. NODE DEFINITIONS
# =====================================================================

def agent_node(state: AgentState) -> AgentState:
    """
    Main reasoning node using Groq LLM or direct tool execution fallback.
    """
    try:
        system_prompt = SystemMessage(content=(
            "You are the official Digital Wallet AI Support Assistant (ডিজিটাল ওয়ালেট এআই অ্যাসিস্ট্যান্ট). "
            "You help users with questions about sending money, transfer limits (BDT 20,000 single / BDT 50,000 daily), "
            "5-second press-and-hold confirmation, requesting money, false transaction reversal disputes, and double-entry ledger audits. "
            "Answer politely and accurately in English or Bengali depending on the user's input language. Use get_wallet_faq when relevant."
        ))

        if not state.messages:
            state.messages = [HumanMessage(content=state.user_question)]

        if llm_with_tools:
            response = llm_with_tools.invoke([system_prompt] + state.messages)
            state.messages = state.messages + [response]

            if not getattr(response, "tool_calls", None):
                state.final_answer = response.content
        else:
            # Direct knowledge lookup fallback if Groq API Key is not set
            answer = get_wallet_faq.invoke(state.user_question)
            state.final_answer = answer

        return state
    except Exception as e:
        print(f"[agent_node] Error: {e}")
        state.final_answer = get_wallet_faq.invoke(state.user_question)
        return state


def human_approval_node(state: AgentState) -> AgentState:
    """HITL approval node for sensitive administrative actions."""
    last_message = state.messages[-1]
    tool_call = last_message.tool_calls[0]

    decision = interrupt({
        "type": "request_approval",
        "message": f"Escalate dispute to admin? -> {tool_call['name']}({tool_call['args']})",
        "tool_call_id": tool_call["id"],
    })

    if decision.get("approved"):
        return state

    state.messages = state.messages + [
        ToolMessage(
            content="User cancelled admin escalation.",
            tool_call_id=tool_call["id"],
        )
    ]
    state.action_cancelled = True
    state.final_answer = "Escalation request cancelled."
    return state


tool_node = ToolNode(tools=TOOLS)


# =====================================================================
# 5. ROUTING & GRAPH BUILD
# =====================================================================

def route_after_agent(state: AgentState) -> str:
    last_message = state.messages[-1]
    tool_calls = getattr(last_message, "tool_calls", None)

    if not tool_calls:
        return "end"

    if tool_calls[0]["name"] in SENSITIVE_TOOLS:
        return "needs_approval"

    return "safe_tool"


def route_after_approval(state: AgentState) -> str:
    return "end" if state.action_cancelled else "safe_tool"


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

workflow.add_edge(TOOLS_NODE, AGENT)
demo_wkf = workflow