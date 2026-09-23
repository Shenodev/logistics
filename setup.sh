#!/usr/bin/env bash
# ShenoFlow — one-click demo environment setup
# Runs Django migrations and seeds demo accounts + rich Faker data.
# Usage: ./setup.sh [--no-seed] [--reset-db]
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND="$ROOT/backend"
VENV_PY="$BACKEND/.venv/Scripts/python.exe"
if [[ ! -f "$VENV_PY" ]]; then
  VENV_PY="$BACKEND/.venv/bin/python"
fi
if [[ ! -f "$VENV_PY" ]]; then
  VENV_PY="python"
fi

NO_SEED=0
RESET_DB=0
for arg in "$@"; do
  case "$arg" in
    --no-seed) NO_SEED=1 ;;
    --reset-db) RESET_DB=1 ;;
    -h|--help)
      echo "Usage: ./setup.sh [--no-seed] [--reset-db]"
      echo "  --no-seed   Only run migrations, skip seed_demo"
      echo "  --reset-db  Delete backend/db.sqlite3 first (sqlite only)"
      exit 0
      ;;
  esac
done

info() { printf "[setup] %s\n" "$*"; }
ok()   { printf "[ok] %s\n" "$*"; }
warn() { printf "[warn] %s\n" "$*"; }
die()  { printf "[error] %s\n" "$*" >&2; exit 1; }

info "ShenoFlow demo setup — $ROOT"

if ! "$VENV_PY" -c "import django" 2>/dev/null; then
  die "Django not found via $VENV_PY. Create venv: python -m venv backend/.venv && backend/.venv/bin/pip install -r backend/requirements.txt"
fi
PY="$VENV_PY"
ok "Python: $($PY --version) ($PY)"

if [[ -z "${DATABASE_URL:-}" && -z "${SUPABASE_DB_PASSWORD:-}" ]]; then
  if command -v cygpath >/dev/null 2>&1; then
    WIN_BACKEND="$(cygpath -m "$BACKEND")"
    export DATABASE_URL="sqlite:///$WIN_BACKEND/db.sqlite3"
  else
    export DATABASE_URL="sqlite:///$BACKEND/db.sqlite3"
  fi
  warn "No DATABASE_URL/SUPABASE_DB_PASSWORD — using sqlite: $DATABASE_URL"
fi

if [[ "$RESET_DB" == "1" ]]; then
  # Prefer direct backend file; also parse DATABASE_URL for non-standard locations
  if [[ -f "$BACKEND/db.sqlite3" ]]; then
    info "Resetting sqlite DB at $BACKEND/db.sqlite3"
    rm -f "$BACKEND/db.sqlite3"
  elif [[ "${DATABASE_URL:-}" == sqlite://* ]]; then
    DB_PATH="${DATABASE_URL#sqlite:///}"
    # cygpath conversion may leave /d/...; try both forms
    if command -v cygpath >/dev/null 2>&1 && [[ "$DB_PATH" == /d/* ]]; then
      DB_PATH="$(cygpath -m "$DB_PATH" 2>/dev/null || echo "$DB_PATH")"
    fi
    if [[ -f "$DB_PATH" ]]; then
      info "Resetting sqlite DB at $DB_PATH"
      rm -f "$DB_PATH"
    fi
  fi
fi

if ! "$PY" -c "import faker" 2>/dev/null; then
  info "Installing Faker..."
  "$PY" -m pip install -q "Faker==37.11.0"
fi

info "Running migrations..."
"$PY" "$BACKEND/manage.py" migrate --noinput
ok "Migrations complete"

if [[ "$NO_SEED" == "1" ]]; then
  warn "Skipping seed_demo (--no-seed)"
else
  info "Seeding demo data (seed_demo --clear)..."
  "$PY" "$BACKEND/manage.py" seed_demo --clear
  ok "Seed complete"
  echo ""
  echo "Demo logins:"
  echo "  user@shenodev.tech      / user123      — logistics.shenodev.tech"
  echo "  admin@shenodev.tech     / admin123     — admin.logistics.shenodev.tech"
  echo "  delivery@shenodev.tech  / delivery123  — delivery.logistics.shenodev.tech"
fi

ok "Environment ready — one click done. Run: ./setup.sh"
