from __future__ import annotations

import logging
import sys
from pathlib import Path

from core.config import settings


def setup_logging() -> None:
    """Настройка логирования."""
    log_level = logging.DEBUG if settings.DEBUG else logging.INFO

    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    logging.basicConfig(
        level=log_level,
        format=log_format,
        datefmt=date_format,
        handlers=[
            logging.StreamHandler(sys.stdout),
        ],
    )

    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy.engine").setLevel(
        logging.INFO if not settings.DEBUG else logging.DEBUG
    )
