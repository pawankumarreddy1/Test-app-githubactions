# --------------------------
# 1️⃣ Base Image
# --------------------------
FROM python:3.11-slim

# --------------------------
# 2️⃣ Environment Vars
# --------------------------
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    POETRY_VERSION=1.8.3 \
    PATH="/root/.local/bin:$PATH"

# --------------------------
# 3️⃣ System Dependencies
# --------------------------
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# --------------------------
# 4️⃣ Install Poetry
# --------------------------
RUN curl -sSL https://install.python-poetry.org | python3 -

# --------------------------
# 5️⃣ Set Work Directory
# --------------------------
WORKDIR /app

# --------------------------
# 6️⃣ Copy Project Files
# --------------------------
COPY pyproject.toml poetry.lock* ./

# --------------------------
# 7️⃣ Install Python Dependencies
# --------------------------
RUN poetry install --no-interaction --no-ansi

# --------------------------
# 8️⃣ Copy Remaining Files
# --------------------------
COPY . .

# --------------------------
# 9️⃣ Expose Port
# --------------------------
EXPOSE 8000

# --------------------------
# 🔟 Start Django
# --------------------------
CMD ["poetry", "run", "python", "-m", "core.manage", "runserver", "0.0.0.0:8000"]

