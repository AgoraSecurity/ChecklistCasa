#!/bin/bash
set -e

echo "Starting North Star Tracker..."

# Create data directory if it doesn't exist
mkdir -p data

# Run database migrations
echo "Running database migrations..."
uv run python manage.py migrate --noinput

# Create cache table for database cache backend
echo "Creating cache table..."
uv run python manage.py createcachetable

# Collect static files
echo "Collecting static files..."
uv run python manage.py collectstatic --noinput --clear

# Verify static files were collected
echo "Verifying static files..."
ls -la /app/staticfiles/ || echo "Static files directory not found"
ls -la /app/staticfiles/admin/ || echo "Admin static files not found"
ls -la /app/staticfiles/admin/css/ || echo "Admin CSS files not found"
ls -la /app/staticfiles/admin/js/ || echo "Admin JS files not found"

# Check if specific files exist
echo "Checking specific admin files..."
test -f /app/staticfiles/admin/css/responsive.css && echo "SUCCESS: responsive.css found" || echo "ERROR: responsive.css missing"
test -f /app/staticfiles/admin/js/nav_sidebar.js && echo "SUCCESS: nav_sidebar.js found" || echo "ERROR: nav_sidebar.js missing"

# Start the application
echo "Starting application server..."
# Use Gunicorn for production instead of Django's development server
exec uv run gunicorn core.wsgi:application --bind 0.0.0.0:8000 --workers 2 --timeout 120
