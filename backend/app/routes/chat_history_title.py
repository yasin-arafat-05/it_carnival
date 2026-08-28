from fastapi import APIRouter, Depends
from app.core.auth import get_current_user
from app.database.models.user import User
from app.database.models.chat_history import (Conversation,
MessageHistory)

router = APIRouter(tags=["Chat History"])

@router.get("/chatHistory/{conversation_id}")
async def chat_history(conversation_id:int, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    user_id = user.id
    result = await db.execute(select(models.User).where(models.User.id == user_id))
    user_record = result.scalar_one_or_none()
    if not user_record:
        raise HTTPException(status_code=404, detail="User not found")

    result = await db.execute(
            select(models.MessageHistory)
                .where(models.MessageHistory.conversation_id == conversation_id)
                .order_by(models.MessageHistory.created_at.asc())
        )
    
    messages = result.scalars().all()
    chat_messages = []
    for msg in messages:
        chat_messages.append({
            'id': msg.id,
            'workflow_type':msg.workflow_type,
            'conversation_id': msg.conversation_id,
            'thread_id': msg.thread_id,
            'message': msg.message,
            'sender_role': msg.sender_role,
            'created_at': msg.created_at

        })
    return chat_messages


@router.get('/chat/title')
async def chatTitle(user: schemas.User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    user_id = user.id 
    result = await db.execute(select(models.User).where(models.User.id == user_id))
    user_record = result.scalar_one_or_none()
    
    if not user_record:
        raise HTTPException(status_code=404, detail="User not found")

    result = await db.execute(
        select(models.Conversation)
            .where(models.Conversation.user_id == user_id)
            .order_by(models.Conversation.last_updated.desc())
    )
    conversations = result.scalars().all()

    title = []
    for i in conversations:
        title.append({
            'thread_id':i.thread_id,
            'created_at':i.created_at,
            'last_updated':i.last_updated,
            'title':i.title,
            'converation_id':i.id
        })
    return title 

