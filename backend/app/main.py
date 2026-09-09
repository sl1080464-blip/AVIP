from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.v1.alerts import router as alerts_router
from backend.app.api.v1.auth import router as auth_router
from backend.app.api.v1.cameras import router as cameras_router
from backend.app.api.v1.detections import router as detections_router
from backend.app.api.v1.events import router as events_router
from backend.app.api.v1.health import router as health_router
from backend.app.api.v1.tracks import router as tracks_router
from backend.app.core.config import get_settings

app = FastAPI(
    title="AVIP API",
    description="AI Vision Intelligence Platform backend foundation.",
    version="0.1.0",
)

settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.CORS_ORIGINS.split(",") if origin.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")
app.include_router(cameras_router, prefix="/api/v1")
app.include_router(detections_router, prefix="/api/v1")
app.include_router(events_router, prefix="/api/v1")
app.include_router(alerts_router, prefix="/api/v1")
app.include_router(tracks_router, prefix="/api/v1")


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "AVIP backend is running"}
