#!/bin/bash
# git_setup.sh - Script to set up a Git repository and push to GitHub

echo "====================================================="
echo "  Setting up Git repository for AI Avatar Video"
echo "====================================================="

# Check if Git is installed
if ! command -v git &> /dev/null; then
    echo "Git is not installed. Installing Git..."
    sudo apt-get update
    sudo apt-get install -y git
fi

# Initialize Git repository if not already done
if [ ! -d ".git" ]; then
    echo "Initializing Git repository..."
    git init
else
    echo "Git repository already initialized."
fi

# Add all files
echo "Adding files to Git..."
git add .

# Update README with GitHub repository information
sed -i "s|yourusername|$username|g" README.md

# Commit changes
echo "Committing changes..."
git commit -m "Initial commit of AI Avatar Video application"

# Ask for GitHub username and repository name
read -p "Enter your GitHub username: " username
read -p "Enter the name for your new repository (e.g., ai-avatar-video): " reponame

# Create repository on GitHub using GitHub CLI if available, otherwise provide instructions
if command -v gh &> /dev/null; then
    echo "Creating repository on GitHub..."
    gh auth login
    gh repo create "$reponame" --public --source=. --remote=origin --push
else
    echo "GitHub CLI not found. Please create a repository manually on GitHub."
    echo "Once created, run the following commands:"
    echo ""
    echo "git remote add origin https://github.com/$username/$reponame.git"
    echo "git branch -M main"
    echo "git push -u origin main"
    echo ""
    
    # Ask if repository was created manually
    read -p "Have you created the repository on GitHub? (y/n): " created
    if [ "$created" = "y" ]; then
        echo "Adding remote..."
        git remote add origin "https://github.com/$username/$reponame.git"
        echo "Setting main branch..."
        git branch -M main
        echo "Pushing to GitHub..."
        git push -u origin main
    fi
fi

echo ""
echo "====================================================="
echo "Git repository setup complete!"
echo "Your code is now on GitHub at: https://github.com/$username/$reponame"
echo "====================================================="
