from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import settings
from core.logging import setup_logging
from db.session import engine, Base
from api.v1.router import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения."""
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("Starting application...")

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    logger.info("Application started successfully")
    yield
    # Shutdown
    logger.info("Shutting down application...")
    await engine.dispose()
    logger.info("Application shut down")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="AI Interview Assistant Backend API",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")


@app.get("/")
async def root():
    """Корневой эндпоинт."""
    return {"message": "Hello World!", "version": settings.VERSION}


@app.get("/health")
async def health_check():
    """Health check эндпоинт."""
    return {"status": "healthy", "version": settings.VERSION}
