#!/bin/bash

# Health Tracker Dashboard - Development Environment Setup

echo "🏥 Setting up Health Tracker development environment..."

# Check if we're in the right directory
if [[ ! -f "requirements.txt" ]]; then
    echo "❌ requirements.txt not found. Please run this script from the project root directory."
    return 1 2>/dev/null || exit 1
fi

# Create venv if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip and install requirements
echo "📦 Installing dependencies..."
python -m pip install --upgrade pip
pip install -r requirements.txt

# Set up environment file
if [[ ! -f ".env" ]]; then
    if [[ -f "environment.example" ]]; then
        echo "📝 Creating .env file from environment.example..."
        cp environment.example .env
        echo "⚠️  Please edit .env file with your actual configuration"
    fi
fi

# Create app directory structure if it doesn't exist
echo "📁 Checking application structure..."
mkdir -p app/templates app/routers static/css static/js static/images

# Install flyctl if not present
if ! command -v flyctl &> /dev/null; then
    echo "📦 Installing flyctl..."
    curl -L https://fly.io/install.sh | sh
    export PATH="$HOME/.fly/bin:$PATH"
fi

# Check auth status (safely)
check_fly_auth() {
    if command -v flyctl &> /dev/null; then
        if flyctl auth whoami &> /dev/null 2>&1; then
            echo "✅ Authenticated with Fly.io as: $(flyctl auth whoami 2>/dev/null)"
            return 0
        else
            echo "🔐 Please authenticate with Fly.io: flyctl auth login"
            return 1
        fi
    else
        echo "⚠️  flyctl not available"
        return 1
    fi
}

# Run auth check
check_fly_auth

echo "✅ Development environment ready!"
echo ""
echo "🚀 Next steps:"
echo "• Start development server: ./start_dev.sh"
echo "• Or manually: cd app && uvicorn main:app --reload"
echo "• Access app: http://localhost:8000"
echo "• API docs: http://localhost:8000/docs" 