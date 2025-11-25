from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.database.models.models import ChatMessage, MessageSender
from core.services.base import BaseDbModelService
from core.dto.interview import ChatMessageSchema



class MessageService(BaseDbModelService[ChatMessage]):
    async def create_chat_message(
        self,
        interview_id: str,
        sender: MessageSender,
        text: str,
    ) -> ChatMessage:
        message = ChatMessage(
            interview_id=interview_id,
            sender=sender,
            text=text
        )
        self.session.add(message)
        await self.session.commit()
        await self.session.refresh(message)
        return message

    async def get_chat_messages_for_interview(
        self, interview_id: str
    ) -> list[ChatMessageSchema]:
        result = await self.session.execute(
            select(ChatMessage)
            .where(ChatMessage.interview_id == interview_id)
            .order_by(ChatMessage.created_at.asc())
        )
        return [ChatMessageSchema.model_validate(message) for message in result.scalars().all()]

