#!/usr/bin/env sh
set -eu

if [ "${ASSAY_RUN_MIGRATIONS:-1}" = "1" ]; then
  alembic upgrade head
fi

exec "$@"
