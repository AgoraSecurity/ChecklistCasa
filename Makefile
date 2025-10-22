.PHONY: dev test lint check prod migrate makemigrations shell

# Development server
dev:
	uv run python manage.py runserver

# Run tests
test:
	uv run python manage.py test

# Run all linters and formatters
lint:
	uv run black .
	uv run isort .
	uv run flake8 .
	uv run mypy .
	uv run bandit -r . -x .venv

# Django system checks
check:
	uv run python manage.py check

# Production server with Gunicorn
prod:
	DJANGO_SETTINGS_MODULE=core.settings.production uv run gunicorn core.wsgi:application

# Database migrations
migrate:
	uv run python manage.py migrate

makemigrations:
	uv run python manage.py makemigrations

# Django shell
shell:
	uv run python manage.py shell

# Create superuser
superuser:
	uv run python manage.py createsuperuser

# Collect static files
collectstatic:
	uv run python manage.py collectstatic --noinput