FROM python:3.11-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

# Install curl for health checks
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Copy application code
COPY . .

# Make scripts executable
RUN chmod +x scripts/wait_for_db.py scripts/migrate_database.py

# Expose port
EXPOSE 8001

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8001/health || exit 1

# Set environment
ENV ENVIRONMENT=production

# Run the application with database migration and wait
CMD ["sh", "-c", "python scripts/wait_for_db.py && python scripts/migrate_database.py && python -m uvicorn server:app --host 0.0.0.0 --port 8001"]