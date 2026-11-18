import pytest
from pydantic import ValidationError

from futebol.config import Settings

DB_URL = "postgresql+psycopg://user:pass@db:5432/futebol"


def test_le_variaveis_de_ambiente(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FOOTBALL_DATA_TOKEN", "token-secreto")
    monkeypatch.setenv("DATABASE_URL", DB_URL)
    monkeypatch.setenv("COMPETITIONS", "ppl, PL")

    settings = Settings(_env_file=None)

    assert settings.competition_codes == ["PPL", "PL"]
    assert "token-secreto" not in repr(settings)  # o segredo não aparece


def test_sem_token_falha(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("FOOTBALL_DATA_TOKEN", raising=False)
    monkeypatch.setenv("DATABASE_URL", DB_URL)

    with pytest.raises(ValidationError):
        Settings(_env_file=None)