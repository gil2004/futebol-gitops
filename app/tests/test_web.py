from fastapi.testclient import TestClient

from futebol.web import app

client = TestClient(app)


def test_healthz_responde_ok() -> None:
    response = client.get("/healthz")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
