from fastapi import APIRouter

router = APIRouter(tags=["alerts"])


@router.get("/alerts")
def list_alerts() -> list[dict[str, object]]:
    return [
        {
            "id": "alert-201",
            "level": "medium",
            "message": "Person detected near restricted access zone.",
            "acknowledged": False,
        },
        {
            "id": "alert-202",
            "level": "high",
            "message": "Vehicle stopped for an extended period near the loading bay.",
            "acknowledged": False,
        },
    ]
