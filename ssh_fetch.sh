#!/bin/bash
set -e  # exit if any command fails

# Install git
echo "Installing Git..."
sudo apt update -y
sudo apt install -y git python3 python3-pip

echo "Installing pkg resources"
sudo  apt-get install --reinstall -y python3-pkg-resources


echo "Printing gi version"
git --version

# Clone the repos (replace with your repo URLs)
REPO_URL="https://github.com/Brianthe2nd/topstep_study.git"
ASSISTANT_REPO_URL="https://github.com/Brianthe2nd/csv_study.git"

REPO_NAME=$(basename "$REPO_URL" .git)
ASSISTANT_REPO_NAME=$(basename "$ASSISTANT_REPO_URL" .git)

# Clone/update assistant repo
if [ -d "$ASSISTANT_REPO_NAME" ]; then
    echo "Assistant repo already cloned. Pulling latest changes..."
    cd "$ASSISTANT_REPO_NAME"
    git pull
    cd ..
else
    echo "Cloning assistant repository..."
    git clone "$ASSISTANT_REPO_URL"
fi

# Clone/update main repo
if [ -d "$REPO_NAME" ]; then
    echo "Repo already cloned. Pulling latest changes..."
    cd "$REPO_NAME"
    git pull
else
    echo "Cloning repository..."
    git clone "$REPO_URL"
    cd "$REPO_NAME"
fi

echo "Installing ytdlp"
sudo apt install -y yt-dlp

echo "Installing python3-venv"
sudo apt install -y python3-venv

echo "Creating Python virtual environment..."
python3 -m venv .venv
source .venv/bin/activate

echo "installing setup tools"
pip3 install --upgrade setuptools

echo "Installing camgear"
pip install -U vidgear[core]

echo "Installing requirements"
pip install -r requirements.txt

# Run main.py in background
echo "Running main.py in background..."
nohup .venv/bin/python main.py > main.log 2>&1 &

