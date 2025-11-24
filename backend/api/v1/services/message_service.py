from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import ChatMessage, MessageSender



class MessageService:
    """Сервис для работы с сообщениями."""

    async def create_chat_message(
        self,
        db: AsyncSession,
        interview_id: str,
        sender: MessageSender,
        text: str,
    ) -> ChatMessage:
        """Создание сообщения чата."""
        message = ChatMessage(
            interview_id=interview_id,
            sender=sender,
            text=text,
        )
        db.add(message)
        await db.flush()
        await db.refresh(message)
        return message

    async def get_chat_messages_for_interview(
        self,
        db: AsyncSession,
        interview_id: str,
    ) -> list[ChatMessage]:
        """Получение всех сообщений для интервью."""
        result = await db.execute(
            select(ChatMessage)
            .where(ChatMessage.interview_id == interview_id)
            .order_by(ChatMessage.timestamp.asc())
        )
        return list(result.scalars().all())

