#!/bin/bash
# Utility script to kill processes using specific ports

# Kill all uvicorn and gunicorn processes (safer option)
kill_servers() {
  echo "Killing all uvicorn and gunicorn processes..."
  pkill -f 'uvicorn app.main:app' || true
  pkill -f 'gunicorn app.main:app' || true
  echo "Done."
}

# Kill process using a specific port
kill_port() {
  local PORT=$1
  echo "Checking for processes using port $PORT..."
  PID=$(lsof -t -i:$PORT 2>/dev/null)
  if [ -n "$PID" ]; then
    echo "Found process $PID using port $PORT. Killing..."
    kill -9 $PID
    echo "Process killed."
    return 0
  else
    echo "No process found using port $PORT."
    return 1
  fi
}

# Check if a port is in use
check_port() {
  local PORT=$1
  if lsof -i:$PORT >/dev/null 2>&1; then
    echo "Port $PORT is in use."
    return 0
  else
    echo "Port $PORT is available."
    return 1
  fi
}

# Main script logic
if [ "$1" = "all" ]; then
  kill_servers
elif [ -n "$1" ] && [ "$1" -eq "$1" ] 2>/dev/null; then
  kill_port "$1"
else
  echo "Usage: $0 <port_number> | all"
  echo "  port_number: Kill process using the specified port"
  echo "  all: Kill all uvicorn and gunicorn processes"
  exit 1
fi

exit 0
