
# --------------------------
# 1️⃣ Base Python Image
# --------------------------
FROM python:3.12-slim

# --------------------------
# 2️⃣ Set Work Directory
# --------------------------
WORKDIR /app

# --------------------------
# 3️⃣ Install System Dependencies
# --------------------------
# psycopg2 + poetry dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && apt-get clean

# --------------------------
# 4️⃣ Install Poetry Properly
# --------------------------
ENV POETRY_VERSION=1.8.3
RUN curl -sSL https://install.python-poetry.org | python3 -

# Add Poetry to PATH
ENV PATH="/root/.local/bin:$PATH"

# Disable Poetry virtualenv (we use system python)
RUN poetry config virtualenvs.create false

# --------------------------
# 5️⃣ Copy Project Files
# --------------------------
COPY pyproject.toml poetry.lock* /app/

# --------------------------
# 6️⃣ Install Python Dependencies
# --------------------------
RUN poetry install --no-interaction --no-ansi

# --------------------------
# 7️⃣ Copy Whole Project
# --------------------------
COPY . /app

# --------------------------
# 8️⃣ Expose Port
# --------------------------
EXPOSE 8000

# --------------------------
# 9️⃣ Default Command
# --------------------------
CMD ["poetry", "run", "python", "-m", "core.manage", "runserver", "0.0.0.0:8000"]
