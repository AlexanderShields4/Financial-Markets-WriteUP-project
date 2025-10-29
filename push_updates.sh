#!/bin/bash
# Navigate to your project folder
cd /home/alex/projects/Finance || exit

# Add all changed files (you can limit to specific folders if needed)
git add .

# Commit changes with a timestamp message
git commit -m "Automated update: $(date '+%Y-%m-%d %H:%M:%S')"

# Push to your GitHub repository
git push origin main
