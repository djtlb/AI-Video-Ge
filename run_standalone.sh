#!/bin/bash
# run_standalone.sh - Run AI Avatar Video application in standalone mode
# This script runs the application locally without requiring server setup

# Configuration
PORT=${1:-8084}
BROWSER=${2:-"auto"}  # Options: auto, chrome, firefox, none

echo "====================================================="
echo "  AI Avatar Video - Standalone Mode"
echo "====================================================="
echo "Starting application on port $PORT..."

# Check if Python virtual environment exists, create if it doesn't
if [ ! -d "venv" ]; then
    echo "Setting up Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Make sure all dependencies are installed
echo "Checking and installing dependencies..."
pip install -q -r requirements.txt

# Initialize database if needed
if [ ! -f "app.db" ]; then
    echo "Initializing database..."
    python3 init_db.py
fi

# Make sure storage directories exist
mkdir -p app/storage/characters
mkdir -p app/storage/renders
mkdir -p app/storage/thumbs

# Kill any existing server on the same port
echo "Cleaning up any existing processes on port $PORT..."
lsof -ti:$PORT | xargs kill -9 2>/dev/null || true

# Start the application
echo "Starting application..."
python3 -m uvicorn app.main:app --host 127.0.0.1 --port $PORT &
SERVER_PID=$!

# Wait for the server to start
echo "Waiting for application to start..."
for i in {1..10}; do
    if curl -s http://localhost:$PORT/ > /dev/null; then
        break
    fi
    sleep 1
    echo "."
done

# Open browser if requested
if [ "$BROWSER" != "none" ]; then
    echo "Opening browser..."
    
    if [ "$BROWSER" = "auto" ]; then
        # Try to detect the default browser
        if command -v xdg-open &> /dev/null; then
            xdg-open http://localhost:$PORT/
        elif command -v open &> /dev/null; then
            open http://localhost:$PORT/
        elif command -v google-chrome &> /dev/null; then
            google-chrome http://localhost:$PORT/
        elif command -v firefox &> /dev/null; then
            firefox http://localhost:$PORT/
        else
            echo "Could not detect browser. Please open http://localhost:$PORT/ manually."
        fi
    elif [ "$BROWSER" = "chrome" ] && command -v google-chrome &> /dev/null; then
        google-chrome http://localhost:$PORT/
    elif [ "$BROWSER" = "firefox" ] && command -v firefox &> /dev/null; then
        firefox http://localhost:$PORT/
    else
        echo "Requested browser not found. Please open http://localhost:$PORT/ manually."
    fi
fi

echo ""
echo "====================================================="
echo "AI Avatar Video is running at: http://localhost:$PORT/"
echo "Press Ctrl+C to stop the application"
echo "====================================================="

# Keep the script running until user interrupts
trap "echo 'Stopping application...'; kill $SERVER_PID; exit 0" INT TERM
wait $SERVER_PID
