#!/bin/bash
# Script to start AI Avatar Video in a VNC session
# This script sets up a VNC server, starts a browser, and runs the application

# Configuration
VNC_PORT=${1:-5901}
APP_PORT=${2:-8084}
VNC_RESOLUTION=${3:-1280x800}
VNC_PASSWORD=${4:-"password"}  # Default password, change for security

echo "Setting up VNC server on port $VNC_PORT with app on port $APP_PORT"

# Check if x11vnc is installed
if ! command -v x11vnc &> /dev/null; then
    echo "x11vnc not found. Installing required packages..."
    sudo apt-get update
    sudo apt-get install -y x11vnc xvfb firefox openbox
fi

# Kill any existing VNC or app servers
echo "Cleaning up any existing processes..."
pkill -f x11vnc || true
pkill -f Xvfb || true
pkill -f openbox || true
pkill -f firefox || true
./kill_server.sh all || true

# Create VNC password file if it doesn't exist
if [ ! -f ~/.vnc/passwd ]; then
    mkdir -p ~/.vnc
    echo "$VNC_PASSWORD" | vncpasswd -f > ~/.vnc/passwd
    chmod 600 ~/.vnc/passwd
fi

# Start Xvfb
echo "Starting Xvfb virtual display..."
Xvfb :1 -screen 0 $VNC_RESOLUTION -ac &
export DISPLAY=:1

# Wait for Xvfb to start
sleep 2

# Start window manager (Openbox)
echo "Starting window manager..."
openbox &

# Wait for window manager to start
sleep 2

# Start VNC server
echo "Starting VNC server on port $VNC_PORT..."
x11vnc -display :1 -rfbport $VNC_PORT -passwd "$VNC_PASSWORD" -forever -bg -xkb -noxrecord -noxfixes -noxdamage -shared

# Start our application in background
echo "Starting AI Avatar Video application on port $APP_PORT..."
./start_daemon.sh $APP_PORT

# Wait for the application to start
sleep 5

# Start Firefox and open the application
echo "Starting Firefox browser pointed to the application..."
firefox http://localhost:$APP_PORT &

echo ""
echo "======================================================"
echo "VNC Server is running on port $VNC_PORT"
echo "Connect with a VNC client to localhost:$VNC_PORT"
echo "Password: $VNC_PASSWORD"
echo ""
echo "The application is running on http://localhost:$APP_PORT"
echo "Firefox has been started and will load the application"
echo "======================================================"
echo ""
echo "To stop the VNC server and application:"
echo "$ pkill -f x11vnc"
echo "$ pkill -f Xvfb"
echo "$ ./kill_server.sh all"
echo ""
echo "Press Ctrl+C to stop this script"

# Keep the script running to maintain the VNC session
while true; do
    sleep 60
done
