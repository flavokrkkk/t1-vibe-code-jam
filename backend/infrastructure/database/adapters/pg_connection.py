from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from core.config.config import settings
from infrastructure.database.models.models import Base


class DatabaseConnection:
    def __init__(self):
        self._engine = create_async_engine(
            url=settings.database_url
        )

    async def get_session(self) -> AsyncSession:
        return AsyncSession(bind=self._engine)

    async def close(self):
        await self._engine.dispose()
        
    async def create_all_tables(self):
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
    # async def init_test_db(self):
    #     async with await self.get_session() as session:
    #         await test_db(session)
        
    