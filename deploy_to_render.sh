#!/bin/bash
# deploy_to_render.sh - Script to deploy to Render.com

echo "====================================================="
echo "  Deploying AI Avatar Video to Render.com (Free Tier)"
echo "====================================================="

# Check if render-cli is installed
if ! command -v render &> /dev/null; then
    echo "Installing render-cli..."
    npm install -g @renderinc/cli
fi

# Create database
echo "Setting up database..."
python3 init_db.py

# Deploy to Render
echo "Deploying to Render.com..."
render deploy

echo ""
echo "====================================================="
echo "Deployment initiated. Check your Render dashboard:"
echo "https://dashboard.render.com/"
echo "====================================================="
