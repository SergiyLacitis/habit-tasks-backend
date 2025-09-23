FROM python:3.12-slim
COPY --from=ghcr.io/astral-sh/uv:0.8.21 /uv /uvx /bin/
WORKDIR /app
COPY pyproject.toml uv.lock* ./
RUN uv sync --locked
COPY src ./src
EXPOSE 8000
CMD ["uv", "run", "src/main.py"]
