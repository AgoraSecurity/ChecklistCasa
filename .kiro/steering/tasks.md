---
inclusion: always
---

# Django WhatsApp Project Development Guide

## Critical Command Rules
- **ALWAYS** prefix Python/Django commands with `uv run` - bare commands will fail
- **NEVER** use Django shell with `-c` flag - create temporary test files instead (tmp_test.py). Always use `uv run python tmp_test.py`. Never use other temporary file names. When done, don't delete the file, just the contents.
- Add the relevant unit tests to the `test.py` file for the app. Create a new test file if needed.
- Always run migrations after any model changes
- Use `make` commands when available for consistency

```bash
# Required command patterns
uv run python manage.py migrate
uv run python manage.py makemigrations [app_name]
uv run python manage.py runserver
uv run python manage.py shell
```

## Project Architecture
**Settings**: `base.py` → `development.py` (default) → `production.py`
**Database**: SQLite development (`data/db.sqlite3`)

## Development Workflow
1. **Testing**: Create `tmp_test.py` files for quick tests
2. **Execute**: `uv run python tmp_test.py`
Repeat as needed.
3. **Cleanup**: Empty `tmp_test.py` after testing
4. **Migrations**: Run after any model changes

## Make Commands
```bash
make dev     # Development server (preferred)
make test    # Full test suite
make lint    # All linters and formatters
make check   # Django system checks
make prod    # Production with Gunicorn
```

## Code Standards
- **Line length**: 88 characters (Black)
- **Import order**: FUTURE → STDLIB → DJANGO → THIRDPARTY → FIRSTPARTY → LOCALFOLDER
- **Formatting**: Black with 88-char limit
- **Linting**: Flake8, isort, MyPy (lenient), Bandit
- **Documentation**: Docstrings required for public methods/classes
- **Type hints**: Encouraged but not enforced

## File Organization
- **Models**: App's `models.py`
- **URLs**: App's `urls.py` → include in `core/urls.py`
- **Views**: App's `views.py` organized by functionality
- **Migrations**: Auto-generate with `makemigrations`
- **Static/Templates**: Respective directories

## Key Dependencies
- **Python 3.13+** with **uv** package manager
- **Django 5.2+**: Web framework