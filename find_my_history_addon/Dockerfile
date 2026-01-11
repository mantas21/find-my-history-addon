ARG BUILD_FROM=ghcr.io/home-assistant/amd64-base-python:latest
FROM ${BUILD_FROM}

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt /app/
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy application code
COPY find_my_history/ /app/find_my_history/

# Copy s6-overlay service files
COPY rootfs /
