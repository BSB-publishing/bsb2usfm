# Use Python 3.11 slim image as base
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir gunicorn

# Copy application code from parent directory
COPY *.py .
COPY web_service/webapp.py .
COPY web_service/templates ./templates/
COPY web_service/static ./static/

# Create directories for input/output
RUN mkdir -p /app/input /app/output /app/results /app/templates /app/static

# Set permissions
RUN chmod +x *.py

# Create a non-root user
RUN useradd -m -u 1000 bsb2usfm && \
    chown -R bsb2usfm:bsb2usfm /app
USER bsb2usfm

# Expose port for web service
EXPOSE 5000

# Default command (can be overridden)
# Use gunicorn for production, fallback to Flask dev server
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--threads", "4", "--timeout", "300", "--access-logfile", "-", "--error-logfile", "-", "webapp:app"]
