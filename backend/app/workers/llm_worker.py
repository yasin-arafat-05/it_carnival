import json
import logging 
import sys
import asyncio
import selectors
from uuid import UUID, uuid4
from typing import Optional, Dict, Any

from celery import Celery
from langgraph.types import Command
from sqlalchemy import select, func 
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from langchain_core.messages import AIMessage
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

from app.core.config import CONFIG
from app.database.models.user import User
from app.database.models.chat_history import Conversation, MessageHistory
from app.database.session import connection_args
from app.redis.redis_setup import redis_sync, redis_async
from app.workflow.demo_workflow import demo_wkf

logger = logging.getLogger(__name__)  

celery_app_llm = Celery(
    'ai_agent',
    broker=CONFIG.REDIS_DB_LLM_URL,
    backend=CONFIG.REDIS_DB_LLM_URL
)

celery_app_llm.conf.update(
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=100,
    result_expires=360,
    broker_connection_retry_on_startup=True,
    broker_connection_retry=True,
    task_default_queue='llm_tasks',
    task_queues={
        'llm_tasks': {
            'exchange': 'llm_tasks',
            'routing_key': 'llm_tasks',
        }
    },
    task_soft_time_limit=600,  
    task_reject_on_worker_lost=True,
    worker_disable_rate_limits=True,
    task_routes={
        'app.workers.llm_worker.process_llm_request_task': {'queue': 'llm_tasks', 'priority': 5}
    }
)

# ===== INTERRUPT CONFIGURATION MAP =====
INTERRUPT_CONFIG = {
    "demo_workflow": {
        "Human_Approval": {
            "type": "request_approval",
            "message": "Human approval required for sensitive action"
        },
    },
}

# Async version of chunking_message
async def chunking_message(chunk):
    if isinstance(chunk, AIMessage):
        return chunk.content
    else:
        raise TypeError(
            f"Object of type: {type(chunk).__name__} is not correctly formatted for serialization"
        )

# Async processing function
async def process_llm_request_internal(
    user_question: str,
    checkpoint_id: str,
    user_id: Any,
    channel_id: str,
    workflow_type: str = "demo_workflow",
    resume_data: Optional[Dict[str, Any]] = None
):
    """
    Creates a dedicated async DB engine per task execution 
    to prevent event-loop conflicts in Celery workers.
    """
    engine = create_async_engine(
        url=CONFIG.DATABASE_URL,
        pool_size=5,
        max_overflow=2,
        pool_pre_ping=True,
        echo=False,
        connect_args=connection_args,
    )
    session_factory = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )
    
    try:
        print("\n\n ----- Processing LLM Request Internal -----\n\n")
        user_uuid = UUID(str(user_id)) if not isinstance(user_id, UUID) else user_id

        async with session_factory() as db:
            # Verify user exists in database to prevent FK violation
            user_exists = (await db.execute(select(User.id).where(User.id == user_uuid))).scalar_one_or_none()
            if not user_exists:
                logger.warning("User ID %s not found in users table.", user_uuid)
                redis_sync.publish(channel_id, json.dumps({
                    "type": "error",
                    "content": "User account not found in database. Please log out and log in again."
                }))
                return

            is_new_conversation = (not checkpoint_id or str(checkpoint_id).strip() == "")

            # Filter out Swagger UI default dummy objects like {"additionalProp1": {}}
            if isinstance(resume_data, dict):
                clean_resume_data = {k: v for k, v in resume_data.items() if k != "additionalProp1"}
                if not clean_resume_data:
                    resume_data = None

            is_resume = (resume_data is not None) and (not is_new_conversation)
            user_checkpoint_id = str(checkpoint_id) if not is_new_conversation else str(uuid4())

            conversation = None

            # ========== Standard New/Existing Request ==========
            if not is_resume:
                # 1. Fresh conversation
                if is_new_conversation:
                    conversation = Conversation(
                        user_id=user_uuid,
                        thread_id=user_checkpoint_id,
                        title=user_question[:50] + "...." if len(user_question) > 50 else user_question
                    )
                    db.add(conversation)
                    await db.commit()
                    await db.refresh(conversation)
                    redis_sync.publish(channel_id, json.dumps({
                        "type": "checkpoint",
                        "checkpoint_id": user_checkpoint_id
                    }))
                # 2. Existing conversation
                else:
                    result = await db.execute(
                        select(Conversation).where(
                            Conversation.thread_id == checkpoint_id,
                            Conversation.user_id == user_uuid
                        )
                    )
                    conversation = result.scalar_one_or_none()
                    if not conversation:
                        redis_sync.publish(channel_id, json.dumps({"type": "error", "content": "Checkpoint not found"}))
                        return
                    conversation.last_update = func.now()
                    db.add(conversation)
                    await db.commit()

                # Save User Message
                user_msg = MessageHistory(
                    conversation_id=conversation.id,
                    message=user_question,
                    sender_role="human",
                )
                db.add(user_msg)
                await db.commit()
                logger.info(f"Saved user message for conversation {conversation.id}")

            # ========== Resuming Paused Graph ==========
            else: 
                result = await db.execute(
                    select(Conversation).where(
                        Conversation.thread_id == checkpoint_id,
                        Conversation.user_id == user_uuid
                    )
                )
                conversation = result.scalar_one_or_none()
                if not conversation:
                    redis_sync.publish(channel_id, json.dumps({"type": "error", "content": "Conversation not found for resume"}))
                    return

            # Stream Events
            ai_content = ""
            config = {"configurable": {"thread_id": conversation.thread_id}}

            # Stream LangGraph events using PostgreSQL checkpointer
            conn_string = CONFIG.DATABASE_URL_CELERY_TASK
            async with AsyncPostgresSaver.from_conn_string(conn_string) as memory:
                await memory.setup()
                # Target workflow graph compilation
                graph = demo_wkf.compile(checkpointer=memory)

                if is_resume:
                    print("Resuming graph execution...")
                    graph_input = Command(resume=resume_data)
                else:

                    graph_input = {
                        "user_question": user_question,
                        "current_user_id": str(user_id),
                    }

                async for event in graph.astream_events(graph_input, config=config, version='v2'):
                    event_type = event["event"]

                    # If error occurs
                    if isinstance(event, dict) and event.get("type") == "function_error":
                        logger.error("Function call failed, payload was: %r", event.get("failed_generation"))
                        redis_sync.publish(channel_id, json.dumps({"type": "error", "content": "Function call failed"}))
                        await db.rollback()
                        return

                    # Chat Model Output Streaming
                    if event_type == "on_chat_model_stream":
                        chunk_content = await chunking_message(event["data"]["chunk"])
                        ai_content += chunk_content
                        safe_content = json.dumps(chunk_content)[1:-1]
                        redis_sync.publish(channel_id, json.dumps({"type": "content", "content": safe_content}))

                    # Node Execution Progress Stream
                    elif event_type == "on_chain_start":
                        node_name = event["name"]
                        if node_name == "Agent":
                            redis_sync.publish(channel_id, json.dumps({"type": "processing", "node": "Reasoning"}))
                        elif node_name == "Tools":
                            redis_sync.publish(channel_id, json.dumps({"type": "processing", "node": "Executing Tools"}))
                        elif node_name == "Human_Approval":
                            redis_sync.publish(channel_id, json.dumps({"type": "processing", "node": "Awaiting Approval"}))
                        else:
                            redis_sync.publish(channel_id, json.dumps({"type": "processing", "node": node_name}))
                    
                    # HITL Interrupt Handling
                    elif event_type == "on_chain_stream":
                        chunk = event.get('data', {}).get('chunk', {})
                        if isinstance(chunk, dict) and "__interrupt__" in chunk:
                            interrupts = chunk["__interrupt__"]
                            interrupt_value = interrupts[0].value if interrupts else {}
                            print(f"Publishing interrupt event: {interrupt_value}")
                            redis_sync.publish(channel_id, json.dumps({
                                **interrupt_value,
                                "checkpoint_id": user_checkpoint_id if is_new_conversation else checkpoint_id,
                            }))
                            redis_sync.publish(channel_id, json.dumps({"type": "end"}))
                            return 

            # Save generated AI response
            if ai_content:
                ai_msg = MessageHistory(
                    conversation_id=conversation.id,
                    message=ai_content,
                    sender_role="ai"
                )
                db.add(ai_msg)
                try:
                    await db.commit()
                    logger.info(f"Saved AI response for user_id {user_id}")
                except Exception as e:
                    await db.rollback()
                    logger.error(f"Failed to save AI message: {e}")
                    redis_sync.publish(channel_id, json.dumps({"type": "error", "content": "Failed to save response"}))
            else:
                logger.warning("No AI content generated")
                
            redis_sync.publish(channel_id, json.dumps({"type": "end"}))

    except Exception as e:
        print(f"Error in process_llm_request_internal: \n {e}")
        logger.error(f"Error in Celery task internal: {e}")
        redis_sync.publish(channel_id, json.dumps({"type": "error", "content": str(e)}))
    finally:
        await engine.dispose()


@celery_app_llm.task(bind=True, name="app.workers.llm_worker.process_llm_request_task")
def process_llm_request_task(
    self,
    user_question: str,
    checkpoint_id: str,
    user_id: Any,
    channel_id: str,
    workflow_type: str = "demo_workflow",
    resume_data: Optional[Dict[str, Any]] = None
):
    if sys.platform == 'win32':
        loop = asyncio.SelectorEventLoop(selectors.SelectSelector())
    else:
        loop = asyncio.new_event_loop()

    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(
            process_llm_request_internal(user_question, checkpoint_id, user_id, channel_id, workflow_type, resume_data)
        )
    except Exception as e:
        print(f"Error in Celery task: {e}")
        async def publish_error():
            await redis_async.publish(channel_id, json.dumps({
                "type": "error",
                "content": "Something went wrong. Please try again."
            }))
        loop.run_until_complete(publish_error())
    finally:
        loop.close()
