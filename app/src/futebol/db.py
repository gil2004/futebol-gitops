"""Ligação ao PostgreSQL (SQLAlchemy 2.0)."""

from functools import lru_cache

from sqlalchemy import Engine, create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import DeclarativeBase

from futebol.config import get_settings


class Base(DeclarativeBase):
    """Classe-mãe de todos os modelos (tabelas) — usada no próximo passo."""


@lru_cache
def get_engine() -> Engine:
    """Cria o engine (pool de ligações) uma única vez, só quando é preciso."""
    return create_engine(
        str(get_settings().database_url),
        pool_pre_ping=True,  # testa a ligação antes de a usar (a BD pode ter reiniciado)
        connect_args={"connect_timeout": 3},  # não ficar pendurado se a BD não responder
    )


def database_is_up() -> bool:
    """Readiness: a BD responde a um SELECT 1?"""
    try:
        with get_engine().connect() as connection:
            connection.execute(text("SELECT 1"))
    except SQLAlchemyError:
        return False
    return True
