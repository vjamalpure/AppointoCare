#!/bin/sh
set -eu

echo "=========================================="
echo "AppointoCare Backend Startup"
echo "=========================================="

echo ""
echo "Step 1: Checking and creating database if needed..."
python init_db.py

echo ""
echo "Step 2: Running database migrations..."
flask --app run.py db upgrade

echo ""
if [ "${SEED_DEMO_DATA:-true}" = "true" ] || [ "${SEED_SAMPLE_DATA:-false}" = "true" ]; then
  echo "Step 3: Seeding comprehensive multi-industry sample data..."
  python sample_data.py || python create_users.py
  echo "✓ Demo data seeded successfully"
else
  echo "Step 3: Skipping demo data seed (SEED_DEMO_DATA=false)"
fi

echo ""
echo "=========================================="
echo "Backend initialization completed!"
echo "=========================================="
echo ""

exec "$@"
