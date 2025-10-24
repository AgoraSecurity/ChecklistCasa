FROM python:3.13-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install uv

WORKDIR /app

# Copy application code first (needed for pyproject.toml build)
COPY . .

# Install dependencies
RUN uv sync --frozen

# Create data directory for SQLite database
RUN mkdir -p data

# Set default Django settings to production
ENV DJANGO_SETTINGS_MODULE=core.settings.production

# Copy and make entrypoint script executable
COPY docker-entrypoint.sh /app/
RUN chmod +x /app/docker-entrypoint.sh

# Expose port
EXPOSE 8000

# Add healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=25s --retries=3 \
    CMD curl http://localhost:8000/health/basic/ || exit 1

# Use entrypoint script
CMD ["/app/docker-entrypoint.sh"]
