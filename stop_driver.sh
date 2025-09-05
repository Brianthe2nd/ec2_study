#!/bin/bash
set -e  # stop if any command fails

echo "Navigating to the folder"
cd "topstep_study" || { echo "Failed to cd into topstep_study"; exit 1; }

echo "Killing driver"
pkill -f driver.py || echo "No driver.py process found"

# echo "Pulling latest changes"
# git pull --ff-only

# echo "Running driver.py in background..."
# nohup .venv/bin/python driver.py > main.log 2>&1 &
# echo "driver.py started (PID $!)"
