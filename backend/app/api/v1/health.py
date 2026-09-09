from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from redis import Redis
from redis.exceptions import RedisError
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from backend.app.core.config import get_settings
from backend.app.db.session import engine

router = APIRouter(tags=["health"])


@router.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok", "service": "avip-backend"}


@router.get("/health/ready")
def readiness_check() -> JSONResponse:
    checks: dict[str, str] = {}

    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        checks["database"] = "ok"
    except SQLAlchemyError:
        checks["database"] = "error"

    try:
        redis_client = Redis.from_url(get_settings().REDIS_URL)
        redis_client.ping()
        redis_client.close()
        checks["redis"] = "ok"
    except RedisError:
        checks["redis"] = "error"

    is_ready = all(value == "ok" for value in checks.values())
    payload = {"status": "ok" if is_ready else "degraded", "checks": checks}
    return JSONResponse(
        status_code=status.HTTP_200_OK if is_ready else status.HTTP_503_SERVICE_UNAVAILABLE,
        content=payload,
    )
