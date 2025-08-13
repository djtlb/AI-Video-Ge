#!/bin/bash
# Script to start the AI Avatar Video server with automatic port cleanup

# Default port
PORT=${1:-8084}

echo "Starting AI Avatar Video server on port $PORT..."

# Kill any process using the specified port
echo "Checking for processes using port $PORT..."
PID=$(lsof -t -i:$PORT 2>/dev/null)
if [ -n "$PID" ]; then
  echo "Found process $PID using port $PORT. Killing..."
  kill -9 $PID
  sleep 1
else
  echo "No process found using port $PORT."
fi

# Make sure the storage directories exist
mkdir -p app/storage/characters app/storage/thumbs app/storage/renders app/storage/edited

# Ensure the database is initialized
if [ ! -f app/app.db ]; then
  echo "Initializing database..."
  python3 init_db.py
fi

# Activate virtual environment if it exists
if [ -d "venv" ]; then
  echo "Activating virtual environment..."
  source venv/bin/activate
fi

# Start the server
echo "Starting server on port $PORT..."
exec python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT --reload
