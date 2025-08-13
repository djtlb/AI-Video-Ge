#!/bin/bash
# deploy_free.sh - One script to deploy to any free platform

echo "====================================================="
echo "  AI Avatar Video - Free Deployment Tool"
echo "====================================================="
echo ""
echo "Select a free platform to deploy to:"
echo "1) Render.com"
echo "2) Netlify"
echo "3) Railway App"
echo "4) Export for Replit"
echo "5) Run Locally"
echo "6) Exit"
echo ""
read -p "Enter your choice (1-6): " choice

case $choice in
    1)
        echo "Deploying to Render.com..."
        ./deploy_to_render.sh
        ;;
    2)
        echo "Deploying to Netlify..."
        ./deploy_to_netlify.sh
        ;;
    3)
        echo "Deploying to Railway App..."
        ./deploy_to_railway.sh
        ;;
    4)
        echo "Preparing for Replit..."
        if [ ! -f ".replit" ]; then
            echo "Creating .replit configuration..."
            cat > .replit << EOF
run = "python -m uvicorn app.main:app --host 0.0.0.0 --port 8080"
language = "python3"

[env]
PYTHONPATH = "/home/runner/\${REPL_SLUG}"

[nix]
channel = "stable-22_11"

[deployment]
run = ["sh", "-c", "python -m uvicorn app.main:app --host 0.0.0.0 --port 8080"]

[[ports]]
localPort = 8080
externalPort = 80
EOF
        fi
        echo "Ready for Replit. Upload your project to replit.com"
        ;;
    5)
        echo "Running locally..."
        ./run_standalone.sh
        ;;
    6)
        echo "Exiting..."
        exit 0
        ;;
    *)
        echo "Invalid choice. Exiting."
        exit 1
        ;;
esac
