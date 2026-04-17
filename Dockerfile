FROM python:3.12-slim

# ── Non-root user for security ──────────────────────────────────────────────
RUN groupadd --gid 1001 appgroup \
 && useradd --uid 1001 --gid appgroup --no-create-home appuser

WORKDIR /app

# ── Environment ─────────────────────────────────────────────────────────────
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PLAYWRIGHT_BROWSERS_PATH=/app/.ms-playwright

# ── System dependencies (for Playwright + psycopg2) ──────────────────────────
# Install build dependencies, then clean up in the same layer to keep image lean
RUN apt-get update && apt-get install -y --no-install-recommends \
        libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*

# ── Python dependencies ──────────────────────────────────────────────────────
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
 && python -m playwright install chromium \
 && python -m playwright install-deps chromium

# ── Runtime directories ──────────────────────────────────────────────────────
RUN mkdir -p logs data $PLAYWRIGHT_BROWSERS_PATH \
 && chown -R appuser:appgroup /app

# ── Application source ───────────────────────────────────────────────────────
COPY --chown=appuser:appgroup . .

# ── Switch to non-root user ──────────────────────────────────────────────────
USER appuser

# ── Healthcheck ──────────────────────────────────────────────────────────────
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
