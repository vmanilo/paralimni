FROM tiangolo/uvicorn-gunicorn:python3.10-slim
COPY --from=ghcr.io/astral-sh/uv:0.6.14 /uv /uvx /bin/

WORKDIR /app

COPY pyproject.toml .
COPY uv.lock .

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV UV_COMPILE_BYTECODE=1
ENV UV_FROZEN=1
ENV UV_NO_CACHE=1

RUN uv sync --frozen --no-install-project --no-dev

COPY . .

RUN uv sync --frozen --no-dev

ENV PATH="/app/.venv/bin:$PATH"

CMD ["uvicorn", "api.api:app", "--host", "0.0.0.0", "--port", "8000", "--log-level", "info",  "--workers", "4"]
