#!/bin/bash
# Start script with nohup to keep server running even when terminal is closed

# Default port
PORT=${1:-8084}

# Kill any existing servers first
./kill_server.sh all

# Ensure storage directories exist
mkdir -p app/storage/characters app/storage/thumbs app/storage/renders app/storage/edited

# Ensure database is initialized
if [ ! -f app/app.db ]; then
  echo "Initializing database..."
  source venv/bin/activate && python3 init_db.py
fi

# Start server with nohup to keep running
echo "Starting server on port $PORT in the background..."

# Use nohup to keep process running
nohup bash -c "source venv/bin/activate && python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT" > server.log 2>&1 &

# Get the PID of the background process
PID=$!
echo "Server started with PID $PID"
echo "You can check logs in server.log"
echo "Server running on http://localhost:$PORT"
echo "To stop the server, run: ./kill_server.sh all"
