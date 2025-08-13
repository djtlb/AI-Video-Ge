#!/bin/bash
# Test script to verify the AI Avatar Video server is running correctly

PORT=${1:-8084}
MAX_ATTEMPTS=10
DELAY=2  # seconds between attempts

echo "Testing server connection on port $PORT..."
echo "Will attempt to connect $MAX_ATTEMPTS times with $DELAY second intervals"

# Check if server is responsive
check_server() {
  echo "Attempt $1: Testing connection to http://localhost:$PORT/"
  if curl -s http://localhost:$PORT/ > /dev/null; then
    echo "Success! Server is responding on port $PORT"
    
    # Check system info endpoint
    echo "Testing system info endpoint..."
    if curl -s http://localhost:$PORT/system/info > /dev/null; then
      echo "System info endpoint is working!"
      return 0
    else
      echo "System info endpoint failed"
      return 1
    fi
  else
    echo "Failed to connect to server"
    return 1
  fi
}

# Try to connect multiple times
for ((i=1; i<=$MAX_ATTEMPTS; i++)); do
  if check_server $i; then
    echo "Server is fully operational!"
    exit 0
  fi
  
  if [ $i -lt $MAX_ATTEMPTS ]; then
    echo "Waiting $DELAY seconds before next attempt..."
    sleep $DELAY
  fi
done

echo "Failed to connect to server after $MAX_ATTEMPTS attempts"
echo "Please check server logs for errors"
exit 1
