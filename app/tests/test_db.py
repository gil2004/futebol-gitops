import pytest
from sqlalchemy import create_engine

from futebol import db


def test_bd_disponivel(monkeypatch: pytest.MonkeyPatch) -> None:
    engine = create_engine("sqlite://")  # BD em memória, só para o teste
    monkeypatch.setattr(db, "get_engine", lambda: engine)

    assert db.database_is_up() is True


def test_bd_indisponivel(monkeypatch: pytest.MonkeyPatch) -> None:
    # Porta 1 em localhost: ninguém está a ouvir → ligação recusada logo
    engine = create_engine(
        "postgresql+psycopg://user:pass@127.0.0.1:1/x",
        connect_args={"connect_timeout": 1},
    )
    monkeypatch.setattr(db, "get_engine", lambda: engine)

    assert db.database_is_up() is False
