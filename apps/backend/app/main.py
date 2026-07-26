import logging
import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import OperationalError

from app.api.router import api_router
from app.core.config import settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)

logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    docs_url="/docs" if settings.enable_openapi else None,
    openapi_url="/openapi.json" if settings.enable_openapi else None,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def request_limits(request: Request, call_next):
    if request.method in {"POST", "PUT", "PATCH"}:
        length = request.headers.get("content-length")
        if length and int(length) > settings.max_request_body_bytes:
            return JSONResponse(
                status_code=413,
                content={"error": {"code": "request_too_large", "message": "Request body too large"}},
            )
    started = time.monotonic()
    response = await call_next(request)
    response.headers["X-Process-Time"] = f"{time.monotonic() - started:.4f}"
    return response

@app.exception_handler(OperationalError)
async def database_error(request: Request, exc: OperationalError):
    logger.exception("database_unavailable")
    return JSONResponse(
        status_code=503,
        content={"error": {
            "code": "database_unavailable",
            "message": "Database temporarily unavailable",
        }},
    )

app.include_router(api_router, prefix="/api/v1")
