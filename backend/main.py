from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from database import db_helper
from logger import (
    setup_logging,
    start_log_shipping,
    stop_log_shipping,
    get_logger,
)
from api import router
from settings import settings


log = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    setup_logging()
    await start_log_shipping()

    log.info("Starting up the FastAPI application...")

    yield

    log.info("Shutting down the FastAPI application...")

    await db_helper.dispose()
    await stop_log_shipping()

    log.info("Application shutdown complete")


main_app = FastAPI(
    lifespan=lifespan,
    default_response_class=ORJSONResponse,
)

main_app.include_router(router)

# CORS
main_app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    # TODO: Move to config
    uvicorn.run(
        "main:main_app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        forwarded_allow_ips="*",
        proxy_headers=True,
    )
