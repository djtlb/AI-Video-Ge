#!/bin/bash
# deploy_to_github.sh - Improved script to deploy to GitHub

echo "====================================================="
echo "  Deploying AI Avatar Video to GitHub"
echo "====================================================="

# Configure Git identity
read -p "Enter your Git email: " email
read -p "Enter your Git name: " name
git config --global user.email "$email"
git config --global user.name "$name"

# Clean up any existing Git configurations
rm -rf .git

# Initialize fresh Git repository
echo "Initializing fresh Git repository..."
git init

# Configure main branch instead of master
git branch -M main

# Remove embedded Git repositories (if any)
echo "Cleaning up embedded repositories..."
rm -rf integrations/ComfyUI/.git integrations/Talking_Face_Avatar/.git integrations/facechain/.git integrations/fast-stable-diffusion/.git integrations/image-generator/.git 2>/dev/null || true

# Create and update .gitignore
echo "Creating .gitignore file..."
cat > .gitignore << EOF
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
venv/
ENV/
env/

# IDE files
.idea/
.vscode/
*.swp
*.swo

# Database
*.db
*.sqlite3

# Application specific
app/storage/characters/*
app/storage/renders/*
app/storage/thumbs/*
!app/storage/characters/.gitkeep
!app/storage/renders/.gitkeep
!app/storage/thumbs/.gitkeep

# Log files
*.log

# OS specific
.DS_Store
Thumbs.db

# Environment variables
.env

# Embedded git repositories
integrations/*/
EOF

# Create storage directory placeholders
mkdir -p app/storage/characters app/storage/renders app/storage/thumbs
touch app/storage/characters/.gitkeep app/storage/renders/.gitkeep app/storage/thumbs/.gitkeep

# Ask for GitHub username and repository name
read -p "Enter your GitHub username: " username
read -p "Enter the name for your new repository (e.g., ai-avatar-video): " reponame

# Add all files
echo "Adding files to Git..."
git add .

# Commit changes
echo "Committing changes..."
git commit -m "Initial commit of AI Avatar Video application"

# Instructions for creating repository on GitHub
echo ""
echo "Please create a new repository on GitHub:"
echo "1. Go to https://github.com/new"
echo "2. Enter repository name: $reponame"
echo "3. Make it public or private as you prefer"
echo "4. Click 'Create repository'"
echo "5. Do NOT initialize with README, .gitignore, or license"
echo ""
read -p "Press Enter once you've created the repository on GitHub... " 

# Add remote and push
echo "Adding remote..."
git remote add origin "https://github.com/$username/$reponame.git"

echo "Pushing to GitHub..."
git push -u origin main

echo ""
echo "====================================================="
echo "Repository deployed to GitHub!"
echo "Your code is now on GitHub at: https://github.com/$username/$reponame"
echo ""
echo "To set up deployment to Render.com:"
echo "1. Go to render.com and sign up/login"
echo "2. Click 'New +' and select 'Web Service'"
echo "3. Connect your GitHub account and select this repository"
echo "4. Configure as follows:"
echo "   - Name: ai-avatar-video (or your preferred name)"
echo "   - Environment: Python"
echo "   - Build Command: pip install -r requirements.txt"
echo "   - Start Command: gunicorn app.main:app -k uvicorn.workers.UvicornWorker -b 0.0.0.0:\$PORT"
echo "   - Plan: Free"
echo "5. Click 'Create Web Service'"
echo "====================================================="
