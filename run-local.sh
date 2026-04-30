#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
API_HOST="${API_HOST:-127.0.0.1}"
API_PORT="${API_PORT:-8000}"
FRONTEND_PORT="${FRONTEND_PORT:-8080}"

cleanup() {
  if [[ -n "${BACKEND_PID:-}" ]]; then
    kill "${BACKEND_PID}" >/dev/null 2>&1 || true
  fi
}

trap cleanup EXIT INT TERM

cd "${ROOT_DIR}/backend"
venv/bin/python -m uvicorn main:app --host "${API_HOST}" --port "${API_PORT}" &
BACKEND_PID=$!

cd "${ROOT_DIR}"
echo "API: http://${API_HOST}:${API_PORT}"
echo "Frontend: http://127.0.0.1:${FRONTEND_PORT}/index.html"
exec python3 -m http.server "${FRONTEND_PORT}" --directory frontend
