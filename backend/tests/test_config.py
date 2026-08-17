from backend.app.core.config import Settings


def test_default_settings() -> None:
    settings = Settings()
    assert settings.APP_ENV == "development"
    assert settings.API_PORT == 8000
    assert settings.REDIS_URL.startswith("redis://")
