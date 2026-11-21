# syntax=docker/dockerfile:1

# =========================================================
# Estágio 1: builder (instala dependências com o uv)
# =========================================================
FROM python:3.12-slim@sha256:5e2bdb1b0d542d5039cffb8181c65930093949194a65c365dfb1b0fe13a4fa5b AS builder

# Copia o binário do uv da imagem oficial (versão fixa = build reproduzível)
COPY --from=ghcr.io/astral-sh/uv:0.13.9@sha256:d3b601f0c7b118bc1753febf7c41cc80981df678445e0254284eecf84db79a7d /uv /bin/uv

# UV_COMPILE_BYTECODE: gera .pyc já na build (arranque mais rápido)
# UV_LINK_MODE=copy:   copia ficheiros em vez de hardlinks (necessário com cache mounts)
# UV_PYTHON_DOWNLOADS: usa o Python da imagem, nunca descarrega outro
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never

WORKDIR /app

# 1) Só as dependências: esta camada só é refeita quando o uv.lock muda
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-dev --no-install-project

# 2) O código da app, instalado como pacote normal (não editável)
COPY . .
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev --no-editable

# =========================================================
# Estágio 2: runtime (só o necessário para correr)
# =========================================================
FROM python:3.12-slim@sha256:5e2bdb1b0d542d5039cffb8181c65930093949194a65c365dfb1b0fe13a4fa5b AS runtime

# PYTHONUNBUFFERED: logs aparecem logo no "docker logs" (sem buffer)
# PATH: o uvicorn e o python do .venv passam a ser os predefinidos
ENV PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH"

# Utilizador sem privilégios, com UID/GID fixos
RUN groupadd --system --gid 10001 app \
 && useradd --system --uid 10001 --gid app --no-create-home app

# Atualizações de segurança do Debian (a imagem base pode estar atrasada
# em relação às correções publicadas). Corre como root, antes do USER.
RUN apt-get update \
 && apt-get upgrade -y --no-install-recommends \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Só o .venv vem do builder (fica do root: a app não o pode alterar)
COPY --from=builder /app/.venv /app/.venv

USER 10001:10001

EXPOSE 8000

# A slim não tem curl: usamos o próprio Python para testar o /healthz
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/healthz', timeout=2)"]

CMD ["uvicorn", "futebol.web:app", "--host", "0.0.0.0", "--port", "8000"]
