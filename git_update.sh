#!/bin/bash
# Usage: ./git_update.sh <csv_file>

CSV_FILE=$1
echo "Updating topstep.csv from $CSV_FILE"
BRANCH="main"
REPO_DIR="C:/Users/Brayo/Desktop/topstep_study"

cd "$REPO_DIR" || exit 1

cp "$CSV_FILE" topstep.csv

git checkout "$BRANCH"
git pull origin "$BRANCH"
git add topstep.csv
git commit -m "Update topstep.csv from $(basename "$CSV_FILE") on $(date '+%Y-%m-%d %H:%M:%S')" || true
git push origin "$BRANCH"
