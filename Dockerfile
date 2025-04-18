FROM python:3.10-slim
COPY --from=ghcr.io/astral-sh/uv:0.6.14 /uv /uvx /bin/

WORKDIR /app

COPY pyproject.toml .
COPY uv.lock .

ENV UV_COMPILE_BYTECODE=1
ENV UV_FROZEN=1
ENV UV_NO_CACHE=1
RUN uv sync --no-editable

COPY . .

CMD ["uv", "run", "main.py"]
