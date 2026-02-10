FROM python:3.13-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /stones

RUN mkdir -p /stones/db

COPY stones/ ./stones
COPY app.py pyproject.toml uv.lock ./

RUN uv sync --frozen --no-dev --no-install-project

EXPOSE 5000

ENV PATH="/stones/.venv/bin:$PATH"

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "app:app"]

