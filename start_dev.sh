#!/bin/bash

# Health Tracker Dashboard - Start Development Server

echo "🏥 Starting Health Tracker development server..."

# Check if we're in the right directory
if [[ ! -f "requirements.txt" ]]; then
    echo "❌ requirements.txt not found. Please run this script from the project root directory."
    exit 1
fi

# Check if virtual environment exists
if [[ ! -d "venv" ]]; then
    echo "❌ Virtual environment not found. Run ./dev_setup.sh first."
    exit 1
fi

# Activate virtual environment if not already active
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo "🔧 Activating virtual environment..."
    source venv/bin/activate
fi

# Check if .env exists
if [[ ! -f ".env" ]]; then
    echo "⚠️  .env file not found. Some features may not work correctly."
    echo "   Run ./dev_setup.sh to create one from environment.example"
fi

# Start the development server
echo "🚀 Starting FastAPI development server..."
echo "📍 Server will be available at: http://localhost:8000"
echo "📖 API docs will be available at: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

cd app && uvicorn main:app --reload --host 0.0.0.0 --port 8000 