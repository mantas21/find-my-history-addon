ARG BUILD_FROM=ghcr.io/home-assistant/amd64-base-python:latest
FROM ${BUILD_FROM}

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt /app/
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy application code
COPY find_my_history/ /app/find_my_history/
COPY run.sh /app/

# Make run script executable
RUN chmod a+x /app/run.sh

# Run the application
CMD [ "/app/run.sh" ]
