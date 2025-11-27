from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config.config import settings
from core.config.logging import setup_logging
from infrastructure.database.adapters.pg_connection import DatabaseConnection
from api.v1.routers import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("Starting application...")

    db_connection = DatabaseConnection()
    app.state.db_connection = db_connection
    await db_connection.create_all_tables()
    await db_connection.init_test_data()

    logger.info("Application started successfully")
    yield
    logger.info("Shutting down application...")
    await db_connection.close()
    logger.info("Application shut down")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="AI Interview Assistant Backend API",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)
