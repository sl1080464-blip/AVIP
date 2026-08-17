from fastapi import FastAPI

from backend.app.api.v1.health import router as health_router

app = FastAPI(
    title="AVIP API",
    description="AI Vision Intelligence Platform backend foundation.",
    version="0.1.0",
)

app.include_router(health_router, prefix="/api/v1")


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "AVIP backend is running"}
