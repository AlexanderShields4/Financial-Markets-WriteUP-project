#!/bin/bash

# Change to the repository root directory
cd "$(dirname "$0")"

# Add any new writeup files
git add Daily_write_ups/*.txt

# Only commit if there are changes
if git diff --cached --quiet; then
    echo "No new writeups to commit"
else
    git commit -m "Auto-update: Daily writeups $(date +%Y-%m-%d)"
    
    # Push if credentials are available (you'll need to set up credentials)
    if [ -n "$GITHUB_TOKEN" ]; then
        git push
    else
        echo "Changes committed locally. Push manually when ready."
    fi
fi