import logging
import time

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.utils import configure_logging, elapsed_ms, standard_error_payload, structured_log
from app.routes.analyze import router as analyze_router

from fastapi.middleware.cors import CORSMiddleware

configure_logging(settings.log_level)
logger = logging.getLogger("ai_smart_travel.api")

app = FastAPI(title=settings.app_name, version=settings.app_version)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analyze_router)


@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    request.state.request_started_at = time.perf_counter()
    raw_body = await request.body()
    request.state.request_body = raw_body.decode("utf-8", errors="ignore")
    structured_log(
        logger,
        "info",
        "request_started",
        method=request.method,
        path=request.url.path,
        body=request.state.request_body,
    )
    try:
        response = await call_next(request)
    except Exception:
        response_time_ms = elapsed_ms(request.state.request_started_at)
        structured_log(
            logger,
            "exception",
            "request_failed",
            method=request.method,
            path=request.url.path,
            response_time_ms=response_time_ms,
        )
        raise

    response_time_ms = elapsed_ms(request.state.request_started_at)
    response.headers["X-Response-Time-Ms"] = str(response_time_ms)
    structured_log(
        logger,
        "info",
        "request_completed",
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
        response_time_ms=response_time_ms,
    )
    return response


@app.exception_handler(HTTPException)
async def http_exception_handler(_: Request, exc: HTTPException) -> JSONResponse:
    if isinstance(exc.detail, dict):
        payload = exc.detail
    else:
        payload = standard_error_payload(str(exc.detail))
    return JSONResponse(status_code=exc.status_code, content=payload)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content=standard_error_payload("Invalid request payload.", exc.errors()),
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(_: Request, exc: Exception) -> JSONResponse:
    logger.exception("unhandled_exception")
    return JSONResponse(
        status_code=500,
        content=standard_error_payload("Internal server error.", str(exc)),
    )


@app.get("/")
async def root() -> dict[str, str]:
    return {
        "app": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "docs": "/docs",
        "endpoint": "POST /analyze",
    }


@app.get("/health")
async def health_check() -> dict[str, str | bool]:
    return {"status": "ok", "debug": settings.debug_mode}
