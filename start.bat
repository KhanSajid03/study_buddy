@echo off
REM Study Buddy - Development Startup Script for Windows
REM This script helps start the application in development mode

echo.
echo ========================================
echo   Study Buddy - Starting Application
echo ========================================
echo.

REM Check if .env exists
if not exist .env (
    echo [WARNING] .env file not found. Creating from .env.example...
    copy .env.example .env
    echo [SUCCESS] Created .env file. Please edit it with your settings.
    echo.
)

REM Check if Docker is installed
docker --version >nul 2>&1
if %errorlevel% == 0 (
    echo [INFO] Docker detected. Starting with Docker Compose...
    echo.

    docker-compose up -d

    echo.
    echo [SUCCESS] Application started!
    echo.
    echo ========================================
    echo   Access Points:
    echo ========================================
    echo   Frontend: http://localhost:3000
    echo   Backend:  http://localhost:8000
    echo   API Docs: http://localhost:8000/docs
    echo.
    echo ========================================
    echo   Useful Commands:
    echo ========================================
    echo   View logs:   docker-compose logs -f backend
    echo   Stop app:    docker-compose down
    echo.

) else (
    echo [ERROR] Docker not found. Please install Docker Desktop or run manually.
    echo.
    echo Manual setup:
    echo 1. Backend: cd backend ^&^& venv\Scripts\activate ^&^& python -m app.main
    echo 2. Frontend: cd frontend ^&^& npm run dev
    echo.
)

pause
