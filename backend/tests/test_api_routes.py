from backend.app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_cameras_endpoint() -> None:
    response = client.get("/api/v1/cameras")
    assert response.status_code == 200
    payload = response.json()
    assert payload[0]["name"] == "North Entrance"


def test_detections_endpoint() -> None:
    response = client.get("/api/v1/detections")
    assert response.status_code == 200
    payload = response.json()
    assert payload[0]["label"] == "person"


def test_alerts_endpoint() -> None:
    response = client.get("/api/v1/alerts")
    assert response.status_code == 200
    payload = response.json()
    assert payload[0]["level"] == "medium"
