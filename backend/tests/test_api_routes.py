import backend.app.models  # noqa: F401
import pytest
from backend.app.core.security import get_current_user
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
    app.dependency_overrides[get_current_user] = lambda: None
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


def test_camera_can_be_updated_and_deleted(client: TestClient) -> None:
    camera = client.post(
        "/api/v1/cameras",
        json={"name": "Lifecycle Camera", "stream_url": "rtsp://camera-lifecycle/stream"},
    ).json()

    updated = client.patch(
        f"/api/v1/cameras/{camera['id']}",
        json={"name": "Updated Camera", "status": "offline"},
    )
    assert updated.status_code == 200
    assert updated.json()["name"] == "Updated Camera"
    assert updated.json()["status"] == "offline"

    deleted = client.delete(f"/api/v1/cameras/{camera['id']}")
    assert deleted.status_code == 204
    assert client.get(f"/api/v1/cameras/{camera['id']}").status_code == 404


def test_camera_with_related_data_cannot_be_deleted(client: TestClient) -> None:
    camera = client.post(
        "/api/v1/cameras",
        json={"name": "Referenced Camera", "stream_url": "rtsp://camera-referenced/stream"},
    ).json()
    client.post("/api/v1/detections/demo", params={"camera_id": camera["id"]})

    response = client.delete(f"/api/v1/cameras/{camera['id']}")
    assert response.status_code == 409


def test_detections_endpoint(client: TestClient) -> None:
    camera = client.post(
        "/api/v1/cameras",
        json={"name": "Detection Camera", "stream_url": "rtsp://camera-detection/stream"},
    ).json()
    response = client.post(
        "/api/v1/detections/demo",
        params={"camera_id": camera["id"]},
    )
    assert response.status_code == 201
    assert response.json()[0]["label"] == "person"

    response = client.get("/api/v1/detections", params={"camera_id": camera["id"]})
    assert response.status_code == 200
    payload = response.json()
    assert payload[0]["label"] == "person"
    assert payload[0]["camera_id"] == camera["id"]


def test_detection_requires_existing_camera(client: TestClient) -> None:
    response = client.post(
        "/api/v1/detections",
        json={"camera_id": 999, "label": "person", "confidence": 0.9},
    )
    assert response.status_code == 404


def test_alerts_endpoint(client: TestClient) -> None:
    camera = client.post(
        "/api/v1/cameras",
        json={"name": "Alert Camera", "stream_url": "rtsp://camera-alert/stream"},
    ).json()
    event = client.post(
        "/api/v1/events",
        json={
            "camera_id": camera["id"],
            "event_type": "person_detected",
            "confidence": 0.94,
            "metadata": {"zone": "entrance"},
        },
    ).json()
    created = client.post(
        "/api/v1/alerts",
        json={"event_id": event["id"], "message": "Person detected."},
    )
    assert created.status_code == 201
    assert created.json()["acknowledged"] is False

    acknowledged = client.post(f"/api/v1/alerts/{created.json()['id']}/acknowledge")
    assert acknowledged.status_code == 200
    assert acknowledged.json()["acknowledged"] is True

    response = client.get("/api/v1/alerts")
    assert response.status_code == 200
    assert response.json()[0]["level"] == "medium"


def test_event_requires_existing_camera(client: TestClient) -> None:
    response = client.post(
        "/api/v1/events",
        json={"camera_id": 999, "event_type": "person_detected"},
    )
    assert response.status_code == 404


def test_auth_register_and_login(client: TestClient) -> None:
    registration = client.post(
        "/api/v1/auth/register",
        json={
            "username": "operator",
            "email": "operator@example.com",
            "password": "correct horse battery staple",
        },
    )
    assert registration.status_code == 201
    assert registration.json()["token_type"] == "bearer"
    assert registration.json()["access_token"]

    login = client.post(
        "/api/v1/auth/login",
        json={"username": "operator", "password": "correct horse battery staple"},
    )
    assert login.status_code == 200
    assert login.json()["access_token"]

    invalid_login = client.post(
        "/api/v1/auth/login",
        json={"username": "operator", "password": "wrong password"},
    )
    assert invalid_login.status_code == 401

    app.dependency_overrides.pop(get_current_user)
    admin_token = login.json()["access_token"]
    users = client.get("/api/v1/admin/users", headers={"Authorization": f"Bearer {admin_token}"})
    assert users.status_code == 200
    assert users.json()[0]["roles"] == ["admin"]


def test_admin_can_update_user_status_without_deactivating_self(client: TestClient) -> None:
    admin = client.post(
        "/api/v1/auth/register",
        json={
            "username": "admin-status",
            "email": "admin-status@example.com",
            "password": "correct horse battery staple",
        },
    )
    member = client.post(
        "/api/v1/auth/register",
        json={
            "username": "member-status",
            "email": "member-status@example.com",
            "password": "correct horse battery staple",
        },
    )
    assert admin.status_code == 201
    assert member.status_code == 201

    app.dependency_overrides.pop(get_current_user)
    admin_token = admin.json()["access_token"]
    member_id = client.get(
        "/api/v1/admin/users",
        headers={"Authorization": f"Bearer {admin_token}"},
    ).json()[1]["id"]

    disabled = client.patch(
        f"/api/v1/admin/users/{member_id}/status",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"is_active": False},
    )
    assert disabled.status_code == 200
    assert disabled.json()["is_active"] is False

    self_disable = client.patch(
        "/api/v1/admin/users/1/status",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"is_active": False},
    )
    assert self_disable.status_code == 400


def test_camera_creation_requires_authentication(client: TestClient) -> None:
    app.dependency_overrides.pop(get_current_user)
    response = client.post(
        "/api/v1/cameras",
        json={"name": "Protected Camera", "stream_url": "rtsp://camera-protected/stream"},
    )
    assert response.status_code == 401


def test_tracks_can_be_created_filtered_and_closed(client: TestClient) -> None:
    camera = client.post(
        "/api/v1/cameras",
        json={"name": "Tracking Camera", "stream_url": "rtsp://camera-track/stream"},
    ).json()
    created = client.post(
        "/api/v1/tracks",
        json={
            "camera_id": camera["id"],
            "track_id": "track-001",
            "label": "person",
        },
    )
    assert created.status_code == 201
    assert created.json()["status"] == "active"

    active = client.get("/api/v1/tracks", params={"active_only": True})
    assert active.status_code == 200
    assert len(active.json()) == 1

    closed = client.post("/api/v1/tracks/track-001/close")
    assert closed.status_code == 200
    assert closed.json()["status"] == "closed"
    assert closed.json()["ended_at"] is not None
