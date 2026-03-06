#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

cd "$ROOT_DIR"
docker compose up -d db

cat <<'EOF'
Local Assay development is configured for fast Mac-side edits:

1. Start the backend locally
   python -m venv .venv
   source .venv/bin/activate
   pip install -e ".[dev]"
   export ASSAY_DATABASE_URL=postgresql+asyncpg://assay:assay@localhost:5432/assay
   export ASSAY_BASE_URL=http://localhost:8000
   alembic upgrade head
   uvicorn assay.main:app --reload --host 127.0.0.1 --port 8000

2. Start the frontend locally (new terminal)
   cd frontend
   npm install
   NEXT_PUBLIC_API_URL=http://localhost:8000 npm run dev

3. Open the app
   http://localhost:3000

Only PostgreSQL stays in Docker for local debugging. Production Linux hosting remains unchanged.
EOF
