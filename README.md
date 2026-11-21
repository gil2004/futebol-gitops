# futebol-gitops
 
Plataforma DevOps de portefólio: uma app de resultados de futebol (Primeira Liga)
usada como carga útil para praticar containers, CI/CD, Infraestrutura como Código,
Kubernetes, GitOps e observabilidade — primeiro num servidor Hetzner, depois na AWS.
 
> O foco do projeto é a plataforma, não a app. A app é pequena, mas feita com cuidado.
 
## Arquitetura local
 
```
browser ──HTTPS:443──► nginx ──HTTP──► web (FastAPI/uvicorn) ──► PostgreSQL
                       (TLS termination)    rede interna do Docker Compose
```
 
- **nginx** é a única porta de entrada: termina o HTTPS e redireciona HTTP → HTTPS.
- **web** e **PostgreSQL** não publicam portas; só são acessíveis dentro da rede do Compose.
- Todos os containers correm **sem root**, com sistema de ficheiros só de leitura e sem capabilities do Linux.
## Stack
 
| Área | Ferramentas |
|---|---|
| App | Python 3.12, FastAPI, Jinja2, SQLAlchemy, PostgreSQL |
| Dependências | uv (`uv.lock` com versões e hashes fixos) |
| Containers | Docker (Dockerfile multi-stage), Docker Compose, nginx, mkcert |
| Próximas fases | GitHub Actions, Trivy, Terraform, Ansible, k3s, Helm, Argo CD, Prometheus, Grafana, AWS |
 
## Correr em local
 
### Requisitos
 
- [Docker](https://docs.docker.com/engine/install/) com Docker Compose v2
- [uv](https://docs.astral.sh/uv/) (só para desenvolver/testar a app fora do Docker)
- [mkcert](https://github.com/FiloSottile/mkcert) — em Ubuntu: `sudo apt install mkcert libnss3-tools`
- Um token gratuito da [football-data.org](https://www.football-data.org/)
### 1. Configuração
 
```bash
cp .env.example .env
```
 
Preenche no `.env` pelo menos `FOOTBALL_DATA_TOKEN` e `POSTGRES_PASSWORD`.
O `.env` está no `.gitignore` e nunca deve ir para o Git.
 
### 2. Certificados HTTPS locais
 
```bash
mkcert -install                      # cria uma CA local, confiável só nesta máquina
mkdir -p nginx/certs
mkcert -cert-file nginx/certs/localhost.pem \
       -key-file  nginx/certs/localhost-key.pem \
       localhost 127.0.0.1 ::1
chmod 644 nginx/certs/localhost-key.pem   # o nginx corre com outro UID e precisa de ler a chave
```
 
A pasta `nginx/certs/` está no `.gitignore`.
 
### 3. Arrancar
 
```bash
docker compose config --quiet && echo "YAML válido"
docker compose up -d --build
docker compose ps                    # todos os serviços devem ficar (healthy)
```
 
### 4. Verificar
 
```bash
curl -s https://localhost/healthz; echo   # {"status":"ok"}
curl -sI http://localhost | head -1       # HTTP/1.1 301 Moved Permanently
```
 
Ou abre <https://localhost/healthz> no browser.
 
### Parar
 
```bash
docker compose down        # para e remove os containers (os dados da BD ficam no volume)
docker compose down -v     # idem, e apaga também os dados da BD
```
 
## Desenvolver a app (sem Docker)
 
```bash
cd app
uv sync                          # cria app/.venv com as dependências + grupo dev
uv run pytest --cov=futebol      # testes com cobertura
uv run ruff check .              # linter
uv run uvicorn futebol.web:app --reload
```
 
## Estrutura
 
```
.
├── compose.yaml          # web + PostgreSQL + nginx
├── nginx/default.conf    # reverse proxy e HTTPS
├── .env.example          # variáveis de ambiente necessárias (sem valores reais)
└── app/
    ├── Dockerfile        # multi-stage: builder (uv) → runtime (python slim, não-root)
    ├── pyproject.toml    # dependências da app + grupo dev
    ├── uv.lock           # versões exatas de todas as dependências
    ├── src/futebol/      # código da app
    └── tests/
```
 
## Decisões de arquitetura
 
As decisões estão registadas como ADRs (Architecture Decision Records):
 
- ADR-0001 — API de dados de futebol (football-data.org)
- ADR-0002 — Docker Compose em local/CI, Kubernetes nos servidores
- ADR-0003 — HTTPS com nginx (mkcert em local, Let's Encrypt nos servidores)
- ADR-0004 — uv para lock file e dependency groups
