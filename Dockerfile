FROM python:3.13-slim-bookworm

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# System dependencies
RUN apt-get update && apt-get install -y curl build-essential libpq-dev && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 - && ln -s /root/.local/bin/poetry /usr/local/bin/poetry

# Copy dependency files
COPY pyproject.toml poetry.lock* ./

# Install dependencies
RUN poetry install --no-root --only main

# Copy project
COPY . .

# Entrypoint
COPY entrypoint.prod.sh /entrypoint.prod.sh
RUN chmod +x /entrypoint.prod.sh

EXPOSE 8080

ENTRYPOINT ["/entrypoint.prod.sh"]


# Default command to run Django
# CMD ["poetry", "run", "python", "-m", "core.manage", "runserver", "0.0.0.0:8000"]

