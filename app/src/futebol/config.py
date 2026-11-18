"""Configuração da aplicação, lida de variáveis de ambiente (12-Factor App)."""

from functools import lru_cache
from typing import Literal

from pydantic import PostgresDsn, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Todas as definições da app. Falha ao arrancar se faltar alguma obrigatória."""

    model_config = SettingsConfigDict(
        # Em local lê o .env (na raiz ou na pasta app/). Em containers não há .env:
        # as variáveis vêm do docker-compose, do Kubernetes ou do Secrets Manager.
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # SecretStr esconde o valor em logs e mensagens de erro (aparece '**********').
    football_data_token: SecretStr
    database_url: PostgresDsn
    competitions: str = "PPL"
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"

    @property
    def competition_codes(self) -> list[str]:
        """'ppl, PL' -> ['PPL', 'PL']."""
        return [c.strip().upper() for c in self.competitions.split(",") if c.strip()]


@lru_cache
def get_settings() -> Settings:
    """Lê a configuração uma única vez e reutiliza-a no resto da app."""
    return Settings()