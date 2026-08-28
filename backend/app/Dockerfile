# ---------- Stage 1: Builder ----------
FROM python:3.11-slim AS builder

WORKDIR /app

# Build-time deps needed to compile packages like cffi, psycopg, asyncpg
# (apt-get is the correct package manager on Debian/slim images, not apk)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libffi-dev \
    libpq-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

COPY app/requirements.txt /app/requirements.txt
# Install into a local user dir so we can copy just this into the final image
RUN pip install --upgrade pip --no-warn-script-location && \
    pip install --no-cache-dir --no-warn-script-location --user -r requirements.txt


# ---------- Stage 2: Final (runtime) ----------
# IMPORTANT: must match the builder's Python version + base family (slim/glibc),
# otherwise the compiled packages copied from --from=builder won't work.
FROM python:3.11-slim

WORKDIR /app

# Only runtime deps — no compilers, no -dev headers
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user/group to run the app
RUN groupadd -r appgroup && useradd -r -g appgroup -m appuser

# Bring in the already-built Python packages from the builder stage
COPY --from=builder /root/.local /home/appuser/.local

COPY app /app/app

# Make sure appuser owns everything it needs (app code + installed packages)
RUN chown -R appuser:appgroup /app /home/appuser/.local

# Switch to non-root user
USER appuser

# Make sure locally-installed packages are on PATH
ENV PATH=/home/appuser/.local/bin:$PATH

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]