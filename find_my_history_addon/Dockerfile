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
COPY run.sh /run.sh

# Make run script executable
RUN chmod a+x /run.sh

# Run the application
CMD ["/run.sh"]
