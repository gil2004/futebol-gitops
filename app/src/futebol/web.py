"""Aplicação web (FastAPI)."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from futebol.config import get_settings
from futebol.db import database_is_up


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    """Corre uma vez no arranque: valida a configuração (fail fast)."""
    get_settings()
    yield


app = FastAPI(title="Futebol", version="0.1.0", lifespan=lifespan)


@app.get("/healthz")
def healthz() -> dict[str, str]:
    """Liveness: o processo está vivo? Não verifica a BD de propósito."""
    return {"status": "ok"}


@app.get("/readyz")
def readyz() -> JSONResponse:
    """Readiness: a app consegue trabalhar? Verifica a ligação à BD."""
    if database_is_up():
        return JSONResponse({"status": "ok"})
    return JSONResponse({"status": "database unavailable"}, status_code=503)
