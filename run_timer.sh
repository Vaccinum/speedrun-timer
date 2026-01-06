#!/usr/bin/env bash
# This ensures the script runs in bash, not fish, to avoid Pure prompt errors
# Change directory to the repo folder
cd "$(dirname "$0")"

# Run the timer
python3 livesplit_clone.py
