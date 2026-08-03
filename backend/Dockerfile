# ── Build Stage ──────────────────────────────────────────────────────────
FROM python:3.11-slim as builder

WORKDIR /app

# Install system compilation dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies into user local path
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# ── Runtime Stage ────────────────────────────────────────────────────────
FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies (like postgresql client library)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy installed python libraries from builder
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Copy backend codebase
COPY . /app/backend

# Set the Python path to the repository parent directory so absolute imports resolve correctly
ENV PYTHONPATH=/app

# Port that FastAPI runs on inside the container
EXPOSE 8000

# Default service to boot on startup
ENV SERVICE_NAME=auth_service

# Run the selected microservice dynamically based on SERVICE_NAME environment variable
CMD sh -c "uvicorn backend.services.${SERVICE_NAME}.main:app --host 0.0.0.0 --port 8000"
