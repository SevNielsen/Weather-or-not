#!/bin/bash

# Check for Python 3
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed. Please install it first."
    exit 1
fi

# Install dependencies
echo "Installing dependencies..."
python3 -m pip install -r requirements.txt

# Check for .env file
if [ ! -f .env ]; then
    echo "WARNING: .env file not found. Weather features will not work without an API key."
    echo "Please create a .env file with API_KEY=your_api_key_here"
fi

# Run the app
echo "Starting Weather App..."
python3 app.py
