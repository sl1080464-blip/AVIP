from backend.app.main import app
from fastapi.testclient import TestClient


def test_app_exists() -> None:
    assert app is not None


def test_health_endpoint() -> None:
    response = TestClient(app).get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "avip-backend"}
