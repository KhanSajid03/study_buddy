#!/bin/bash

# Study Buddy - Development Startup Script
# This script helps start the application in development mode

set -e

echo "🚀 Study Buddy - Starting Application"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from .env.example..."
    cp .env.example .env
    echo "✅ Created .env file. Please edit it with your settings."
    echo ""
fi

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check Docker
if command_exists docker && command_exists docker-compose; then
    echo "🐳 Docker detected. Starting with Docker Compose..."
    echo ""

    # Check if containers are already running
    if docker-compose ps | grep -q "Up"; then
        echo "⚠️  Containers already running. Restarting..."
        docker-compose restart
    else
        echo "Starting containers..."
        docker-compose up -d
    fi

    echo ""
    echo "⏳ Waiting for services to be ready..."
    sleep 10

    echo ""
    echo "✅ Application started!"
    echo ""
    echo "📝 Access points:"
    echo "   Frontend: http://localhost:3000"
    echo "   Backend:  http://localhost:8000"
    echo "   API Docs: http://localhost:8000/docs"
    echo ""
    echo "📊 View logs:"
    echo "   docker-compose logs -f backend"
    echo "   docker-compose logs -f frontend"
    echo ""
    echo "🛑 Stop application:"
    echo "   docker-compose down"
    echo ""

else
    echo "Docker not found. Please install Docker or run manually."
    echo ""
    echo "Manual setup:"
    echo "1. Backend: cd backend && source venv/bin/activate && python -m app.main"
    echo "2. Frontend: cd frontend && npm run dev"
    echo ""
fi
