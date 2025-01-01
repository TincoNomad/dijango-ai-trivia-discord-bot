# Base Python image for all services
FROM python:3.12

# Set working directory for application
WORKDIR /app

# Install system dependencies
# - default-libmysqlclient-dev: Required for MySQL connections
# - gcc: Required for compiling some Python packages
# - curl: Used for health checks
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application code
COPY . .
