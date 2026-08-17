from backend.app.models.alert import Alert
from backend.app.models.camera import Camera
from backend.app.models.detection import Detection
from backend.app.models.event import Event
from backend.app.models.model_version import ModelVersion
from backend.app.models.track import Track
from backend.app.models.zone import Zone


def test_sqlalchemy_domain_models_import() -> None:
    assert Camera.__tablename__ == "cameras"
    assert Zone.__tablename__ == "zones"
    assert Detection.__tablename__ == "detections"
    assert Track.__tablename__ == "tracks"
    assert Event.__tablename__ == "events"
    assert Alert.__tablename__ == "alerts"
    assert ModelVersion.__tablename__ == "model_versions"
