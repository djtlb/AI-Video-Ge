#!/bin/bash
# deploy_to_railway.sh - Script to deploy to Railway.app

echo "====================================================="
echo "  Deploying AI Avatar Video to Railway.app (Free Tier)"
echo "====================================================="

# Check if railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "Installing railway CLI..."
    npm i -g @railway/cli
fi

# Login to Railway (if not already logged in)
railway login

# Initialize Railway project if not already done
if [ ! -f "railway.json" ]; then
    echo "Initializing Railway project..."
    railway init
fi

# Deploy to Railway
echo "Deploying to Railway..."
railway up

echo ""
echo "====================================================="
echo "Deployment initiated. Check your Railway dashboard:"
echo "https://railway.app/dashboard"
echo "====================================================="
