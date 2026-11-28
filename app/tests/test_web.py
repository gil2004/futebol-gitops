import pytest
from fastapi.testclient import TestClient

from futebol.web import app

client = TestClient(app)


def test_healthz_responde_ok() -> None:
    response = client.get("/healthz")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_readyz_ok_quando_bd_responde(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("futebol.web.database_is_up", lambda: True)

    response = client.get("/readyz")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_readyz_503_quando_bd_em_baixo(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("futebol.web.database_is_up", lambda: False)

    response = client.get("/readyz")

    assert response.status_code == 503
