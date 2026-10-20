# Use the course lock file so the HTTP demo cannot silently change SDK versions.
FROM python:3.12-slim
WORKDIR /app
COPY --from=ghcr.io/astral-sh/uv:0.8.22 /uv /usr/local/bin/uv
COPY python/pyproject.toml python/uv.lock ./python/
RUN uv sync --project python --locked --no-dev
COPY azure-demo/server.py ./server.py
# The service needs no filesystem write access or privileged ports.
RUN useradd --create-home --uid 10001 instructor
USER instructor
EXPOSE 8000
CMD ["/app/python/.venv/bin/python", "/app/server.py"]
