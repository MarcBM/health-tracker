#!/bin/bash

# Health Tracker - Start Development Server

echo "Starting Health Tracker development server..."

# Check if we're in the right directory
if [[ ! -f "requirements.txt" ]]; then
    echo "Error: requirements.txt not found. Please run this script from the project root directory."
    exit 1
fi

# Check if virtual environment exists
if [[ ! -d "venv" ]]; then
    echo "Error: Virtual environment not found. Run 'source dev_setup.sh' first."
    exit 1
fi

# Activate virtual environment if not already active
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Initialize database if instance folder doesn't exist
if [[ ! -d "instance" ]]; then
    echo "Initializing database..."
    flask --app healthapp init-db
fi

flask --app healthapp run --debug
