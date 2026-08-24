from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from app.api import router as api_router
from app.logging import setup_logging
from app.db import init_db, seed_db
from app.core.constants import (
    API_TITLE,
    API_VERSION,
    CORS_ALLOW_ORIGINS,
    CORS_ALLOW_CREDENTIALS,
    CORS_ALLOW_METHODS,
    CORS_ALLOW_HEADERS,
    GENERIC_ERROR_MESSAGE,
)
import logging

load_dotenv()
setup_logging()
logger = logging.getLogger("main")


# Lifespan handler that initializes the database on app startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    seed_db()
    logger.info("Database initialized and seeded")
    yield


# Main FastAPI application instance
app = FastAPI(title=API_TITLE, version=API_VERSION, lifespan=lifespan)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger = logging.getLogger("main")
    logger.error("Unhandled exception: %s", exc, exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": GENERIC_ERROR_MESSAGE},
    )


app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ALLOW_ORIGINS,
    allow_credentials=CORS_ALLOW_CREDENTIALS,
    allow_methods=CORS_ALLOW_METHODS,
    allow_headers=CORS_ALLOW_HEADERS,
)

app.include_router(api_router)
