FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    ffmpeg \
    libsm6 \
    libxext6 \
    libgl1-mesa-glx \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set environment variables
ENV PYTHONPATH=/app
ENV ENVIRONMENT=production
ENV PORT=8000
ENV HOST=0.0.0.0
ENV ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000

# Create necessary directories
RUN mkdir -p /app/app/storage/characters /app/app/storage/renders /app/app/storage/thumbs /app/app/static

# Expose the application port
EXPOSE 8000

# Set up volume for persistent storage
VOLUME ["/app/app/storage"]

# Run the application
CMD ["./start.sh"]
