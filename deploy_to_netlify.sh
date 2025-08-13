#!/bin/bash
# deploy_to_netlify.sh - Script to deploy to Netlify

echo "====================================================="
echo "  Deploying AI Avatar Video to Netlify (Free Tier)"
echo "====================================================="

# Check if netlify-cli is installed
if ! command -v netlify &> /dev/null; then
    echo "Installing netlify-cli..."
    npm install -g netlify-cli
fi

# Create necessary directories if they don't exist
mkdir -p netlify/functions

# Login to Netlify (if not already logged in)
netlify status || netlify login

# Initialize Netlify site if not already done
if [ ! -f ".netlify/state.json" ]; then
    echo "Initializing Netlify site..."
    netlify init
fi

# Deploy to Netlify
echo "Deploying to Netlify..."
netlify deploy --prod

echo ""
echo "====================================================="
echo "Deployment complete. Your site is now live at the URL shown above."
echo "====================================================="
