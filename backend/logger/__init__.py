__all__ = ["setup_logging", "get_logger", "ColoredFormatter"]

import logging

from settings import settings
from .colored_formatter import ColoredFormatter
from .opensearch_handler import OpenSearchIngestHandler

# TODO: Move to config

LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_LEVEL = "DEBUG"

ENABLE_OS_LOGS = True
SERVICE_NAME = "backend"

OS_INGEST_URL = settings.OS_INGEST_URL

_os_handler: OpenSearchIngestHandler | None = None


def setup_logging() -> None:
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.setLevel(LOG_LEVEL)

    console = logging.StreamHandler()
    console.setFormatter(ColoredFormatter(LOG_FORMAT))
    root_logger.addHandler(console)

    global _os_handler
    if ENABLE_OS_LOGS:
        # TODO: Move to config
        _os_handler = OpenSearchIngestHandler(
            ingest_url=OS_INGEST_URL,
            service_name=SERVICE_NAME,
            level=logging.INFO,
            batch_size=200,
            flush_interval_s=1.0,
            timeout_s=5.0,
            max_connections=20,
            max_keepalive_connections=10,
            keepalive_expiry_s=30.0,
        )
        root_logger.addHandler(_os_handler)


async def start_log_shipping() -> None:
    if _os_handler is not None:
        await _os_handler.start()


async def stop_log_shipping() -> None:
    if _os_handler is not None:
        await _os_handler.aclose()


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
