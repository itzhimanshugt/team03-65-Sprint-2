import pytest


@pytest.fixture(autouse=True)
def no_dotenv(monkeypatch):
    """Tests must not depend on a developer's local .env file."""
    monkeypatch.setattr("app.config.load_dotenv", lambda *args, **kwargs: None)
