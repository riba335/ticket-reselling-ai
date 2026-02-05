from fastapi.testclient import TestClient

from app import main  # noqa: E402


def test_health_endpoint() -> None:
    client = TestClient(main.app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
