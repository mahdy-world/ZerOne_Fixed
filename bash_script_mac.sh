#!/bin/zsh

# Activate the virtual environment
source /Users/egy/Desktop/ZerOneV6/venv/bin/activate

# Navigate to the Django project directory
cd /Users/egy/Desktop/ZerOneV6 || exit 1

# Start the server in the background
python3 manage.py runserver 2023 &

# Give the server a few seconds to start
sleep 2

# Open in Chrome Incognito
open -na "Google Chrome" --args --incognito http://localhost:2023 &
