# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025–2026 Rohan R @rotsl

FROM python:3.11-slim-bookworm

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    tesseract-ocr \
    tesseract-ocr-eng \
    libtesseract-dev \
    libmagic1 \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Copy requirements first for better caching
COPY pyproject.toml README.md LICENSE ./
COPY src/ ./src/

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install -e ".[all]"

# Copy the rest of the application
COPY configs/ ./configs/
COPY examples/ ./examples/
COPY benchmarks/ ./benchmarks/

# Create non-root user
RUN useradd -m -u 1000 cpo && \
    mkdir -p /app/.cpo_cache /app/.cpo_memory && \
    chown -R cpo:cpo /app

USER cpo

# Set entrypoint
ENTRYPOINT ["cpo"]
CMD ["--help"]
