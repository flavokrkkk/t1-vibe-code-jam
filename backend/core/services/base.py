from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

class BaseDbModelService[ModelType]:
    def __init__(
        self, session: AsyncSession,
    ):
        self.session = session
