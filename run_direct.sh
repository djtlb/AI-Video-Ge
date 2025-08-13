#!/usr/bin/env bash

# Simple direct run script for AI Avatar Video application
set -e

# Use explicit port
PORT=${1:-8084}
echo "Using port: ${PORT}"

# Kill any process using the specified port
echo "Checking for processes using port $PORT..."
PID=$(lsof -t -i:$PORT 2>/dev/null)
if [ -n "$PID" ]; then
  echo "Found process $PID using port $PORT. Killing..."
  kill -9 $PID || true
  sleep 1
else
  echo "No process found using port $PORT."
fi

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
elif [ -d ".venv" ]; then
    source .venv/bin/activate
else
    echo "Virtual environment not found. Please create it first."
    exit 1
fi

# Initialize database
echo "Initializing database..."
python3 -c "
from app.database import Base, engine
import app.models

# Create tables
Base.metadata.create_all(bind=engine)
print('Database tables created successfully!')
"

# Start the server
echo "Starting server in development mode..."
exec python3 -m uvicorn app.main:app --host 0.0.0.0 --port ${PORT}
