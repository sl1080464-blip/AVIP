import backend.app.models  # noqa: F401
import pytest
from backend.app.db.base import Base
from backend.app.db.session import get_db
from backend.app.main import app
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool


@pytest.fixture()
def client() -> TestClient:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    def override_get_db():
        db = session_factory()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def test_cameras_endpoint(client: TestClient) -> None:
    create_response = client.post(
        "/api/v1/cameras",
        json={
            "name": "North Entrance",
            "stream_url": "rtsp://camera-01/stream",
        },
    )
    assert create_response.status_code == 201
    assert create_response.json()["id"] == 1

    response = client.get("/api/v1/cameras")
    assert response.status_code == 200
    payload = response.json()
    assert payload[0]["name"] == "North Entrance"
    assert client.get("/api/v1/cameras/999").status_code == 404


def test_duplicate_camera_name_returns_conflict(client: TestClient) -> None:
    payload = {"name": "North Entrance", "stream_url": "rtsp://camera-01/stream"}
    assert client.post("/api/v1/cameras", json=payload).status_code == 201
    response = client.post("/api/v1/cameras", json=payload)
    assert response.status_code == 409


def test_detections_endpoint(client: TestClient) -> None:
    response = client.get("/api/v1/detections")
    assert response.status_code == 200
    payload = response.json()
    assert payload[0]["label"] == "person"


def test_alerts_endpoint(client: TestClient) -> None:
    response = client.get("/api/v1/alerts")
    assert response.status_code == 200
    payload = response.json()
    assert payload[0]["level"] == "medium"
