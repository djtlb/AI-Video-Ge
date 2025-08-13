#!/usr/bin/env bash

# Production startup script for AI Avatar Video application
set -e

# Check for virtual environment
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Install dependencies if needed
if [ "$INSTALL_DEPS" = "true" ]; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
fi

# Setup environment variables
export PYTHONPATH=$(pwd)
export ALLOWED_ORIGINS=${ALLOWED_ORIGINS:-"http://localhost:3000,http://localhost:8000"}
export ENVIRONMENT=${ENVIRONMENT:-"production"}
export LOG_LEVEL=${LOG_LEVEL:-"info"}

# Check if using development or production mode
if [ "$ENVIRONMENT" = "development" ]; then
    echo "Starting in development mode..."
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
else
    echo "Starting in production mode..."
    # Start with Gunicorn for production
    gunicorn -c gunicorn_config.py app.main:app
fi
