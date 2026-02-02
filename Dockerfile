# Use Python 3.10 slim for lightweight and secure image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONOPTIMIZE=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY bot/requirements.txt ./bot/
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r bot/requirements.txt

# Copy source code
COPY . .

# Create necessary directories
RUN mkdir -p database logs

# Set proper permissions
RUN chmod +x bot/main.py

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD python3 -c "import sqlite3; sqlite3.connect('database/trading.db').close()" || exit 1

# Run bot in scheduled mode (15:30 daily)
CMD ["python3", "bot/main.py", "--mode", "scheduled", "--time", "15:30"]
