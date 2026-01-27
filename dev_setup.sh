#!/bin/bash

# Health Tracker - Development Environment Setup

echo "Setting up Health Tracker development environment..."

# Check if we're in the right directory
if [[ ! -f "requirements.txt" ]]; then
    echo "Error: requirements.txt not found. Please run this script from the project root directory."
    return 1 2>/dev/null || exit 1
fi

# Create venv if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip and install requirements
echo "Installing dependencies..."
python -m pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet

echo ""
echo "Development environment ready!"
