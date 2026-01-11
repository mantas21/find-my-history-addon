ARG BUILD_FROM=ghcr.io/home-assistant/amd64-base:latest
FROM ${BUILD_FROM}

# Install Python, pip, and jq
RUN apk add --no-cache \
    python3 \
    py3-pip \
    jq

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt /app/
RUN pip3 install --no-cache-dir --break-system-packages -r requirements.txt

# Copy application code
COPY find_my_history/ /app/find_my_history/

# Copy web UI files (cache-bust: v0.3.4)
COPY www/ /app/www/

# Copy S6 service files (proper integration with HA base image)
COPY rootfs /

# Make S6 service scripts executable
RUN chmod a+x /etc/services.d/find_my_history/run \
    && chmod a+x /etc/services.d/find_my_history/finish
