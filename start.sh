#!/bin/bash

# AI Gap Finder - Development Startup Script

set -e  # Exit on any error

echo "🧠 Starting AI Gap Finder Microservice..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "🔧 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Install/upgrade dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found. Copying from .env.example"
    cp .env.example .env
    echo "⚠️  Please edit .env file and add your OpenAI API key before running!"
    exit 1
fi

# Run tests (optional)
if [ "$1" = "--test" ]; then
    echo "🧪 Running tests..."
    pytest tests/ -v
    echo "✅ Tests completed!"
fi

# Start the service
echo "🚀 Starting AI Gap Finder on http://localhost:8001..."
echo "📚 API Documentation available at http://localhost:8001/docs"
echo ""
python main.py
