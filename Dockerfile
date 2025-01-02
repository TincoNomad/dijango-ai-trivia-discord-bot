# Base Python image for all services
FROM python:3.12

# Set working directory for application
WORKDIR /app

# Install system dependencies
# - default-libmysqlclient-dev: Required for MySQL connections
# - gcc: Required for compiling some Python packages
# - curl: Used for health checks
# - netcat-traditional: Used for network testing
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    gcc \
    curl \
    netcat-traditional \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt requirements-docker.txt ./
RUN pip install -r requirements.txt && \
    pip install -r requirements-docker.txt

# Copy application code
COPY . .

# Make entrypoint executable and set it
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh
ENTRYPOINT ["./entrypoint.sh"]
