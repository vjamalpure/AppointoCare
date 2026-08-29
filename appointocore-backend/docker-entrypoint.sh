#!/bin/sh
set -eu

flask --app run.py db upgrade

if [ "${SEED_DEMO_DATA:-false}" = "true" ]; then
  python create_users.py
fi

exec "$@"
