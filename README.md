# Housing Evaluation System (Checklist.casa)

A mobile-first micro SaaS application that simplifies and standardizes the process of evaluating multiple housing options during in-person visits.

## Features

- **Project Management**: Create and organize housing evaluation projects
- **Team Collaboration**: Invite partners and team members to evaluate properties together
- **Custom Criteria**: Define evaluation parameters tailored to your needs
- **Mobile-Optimized**: Capture information on-site with mobile-friendly forms
- **Property Comparison**: Side-by-side comparison tables with sorting and filtering
- **Data Export**: Export evaluations to CSV and PDF formats

## Quick Start

1. **Install dependencies**:
   ```bash
   uv sync
   ```

2. **Run migrations**:
   ```bash
   uv run python manage.py migrate
   ```

3. **Create a superuser** (optional):
   ```bash
   uv run python manage.py createsuperuser
   ```

4. **Start the development server**:
   ```bash
   make dev
   # or
   uv run python manage.py runserver
   ```

5. **Visit** http://localhost:8000

## Development Commands

- `make dev` - Start development server
- `make test` - Run tests
- `make lint` - Run linters and formatters
- `make check` - Django system checks
- `make migrate` - Apply database migrations
- `make makemigrations` - Create new migrations
- `make shell` - Django shell
- `make superuser` - Create superuser

## Technology Stack

- **Backend**: Django 5.2+ with Python 3.13+
- **Database**: SQLite (development and production)
- **Authentication**: Django Allauth
- **Frontend**: Django Templates + Tailwind CSS + HTMX
- **Package Management**: uv

## Project Structure

```
├── core/                    # Django project settings
├── accounts/                # User authentication app
├── projects/                # Project management app
├── templates/               # HTML templates
├── static/                  # Static assets
├── media/                   # User uploads
├── data/                    # Database files
└── manage.py               # Django management script
```
