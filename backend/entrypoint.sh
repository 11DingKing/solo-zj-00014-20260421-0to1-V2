#!/bin/bash

echo "⏳ Waiting for PostgreSQL to be ready..."
while ! python manage.py inspectdb > /dev/null 2>&1; do
    echo "⏳ PostgreSQL is not ready yet, waiting..."
    sleep 2
done

echo "✅ PostgreSQL is ready!"

echo "🔄 Running makemigrations..."
python manage.py makemigrations --no-input books carts orders

echo "🔄 Running migrate..."
python manage.py migrate --no-input

echo "✅ Database migrations completed!"

echo "📦 Collecting static files..."
python manage.py collectstatic --no-input

echo "✅ Static files collected!"

exec "$@"
