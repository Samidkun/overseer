FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=7788 \
    HOST=0.0.0.0

WORKDIR /app

COPY backend/ ./backend/
COPY frontend/ ./frontend/

RUN useradd -u 10001 -d /app overseer && \
    chown -R overseer:overseer /app

USER overseer

EXPOSE 7788

HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
  CMD python3 -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:7788/api/telemetry/snapshot')" || exit 1

CMD ["python3", "-m", "backend.serve"]
