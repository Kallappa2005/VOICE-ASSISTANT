# Multi-stage Dockerfile for Voice Assistant
# Optimized for Kubernetes deployment
# Supports both GUI (local development) and headless (production) modes

# Stage 1: Builder
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libportaudio2 \
    portaudio19-dev \
    libssl-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Build wheels
RUN pip install --no-cache-dir --user --wheel --no-warn-script-location -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y \
    libportaudio2 \
    alsa-utils \
    pulseaudio \
    xvfb \
    x11-apps \
    && rm -rf /var/lib/apt/lists/*

# Copy Python dependencies from builder
COPY --from=builder /root/.local /root/.local

# Copy application code
COPY . .

# Set environment variables
ENV PATH=/root/.local/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    DOCKER_CONTAINER=true \
    ASSISTANT_MODE=ai

# Create non-root user for security
RUN useradd -m -u 1000 assistant && \
    chown -R assistant:assistant /app

USER assistant

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)" || exit 1

# Default: Run AI assistant in headless mode
CMD ["python", "launcher.py", "--mode", "ai", "--no-gui"]
