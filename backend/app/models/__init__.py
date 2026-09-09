from backend.app.models.alert import Alert
from backend.app.models.camera import Camera
from backend.app.models.detection import Detection
from backend.app.models.event import Event
from backend.app.models.model_version import ModelVersion
from backend.app.models.permission import Permission
from backend.app.models.role import Role
from backend.app.models.track import Track
from backend.app.models.user import User
from backend.app.models.zone import Zone

__all__ = [
    "Alert",
    "Camera",
    "Detection",
    "Event",
    "ModelVersion",
    "Track",
    "Zone",
    "User",
    "Role",
    "Permission",
]
