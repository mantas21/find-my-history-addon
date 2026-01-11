ARG BUILD_FROM
FROM ${BUILD_FROM}

# Install jq for configuration parsing
RUN apk add --no-cache jq

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt /app/
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy application code
COPY find_my_history/ /app/find_my_history/
COPY run.sh /run.sh

# Make run script executable
RUN chmod a+x /run.sh

# Set entrypoint
ENTRYPOINT ["/run.sh"]
