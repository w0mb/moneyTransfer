#!/bin/sh
set -e

echo "Applying migrations..."
cd /app/moneyTransfer
python manage.py migrate

echo "Starting server..."
exec python manage.py runserver 0.0.0.0:8000