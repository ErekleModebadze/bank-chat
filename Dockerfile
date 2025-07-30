#
FROM python:3.12-slim

#
WORKDIR /code

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Copy dependency files
COPY ./pyproject.toml ./uv.lock* /code/

# Install dependencies with uv
RUN uv sync --frozen --no-dev

# Copy application code
COPY ./app /code/app

# Run the FastAPI application
CMD ["uv", "run", "fastapi", "run", "app/main.py", "--port", "80", "--workers", "1"]