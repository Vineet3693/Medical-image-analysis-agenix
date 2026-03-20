@echo off
REM MIA FastAPI Server Startup Script
REM Starts the FastAPI development server

echo ========================================================================
echo MIA - Medical Image Analysis API Server
echo ========================================================================
echo.

REM Check if virtual environment exists
if exist .miavenv\ (
    echo Activating virtual environment...
    call .miavenv\Scripts\activate.bat
) else (
    echo Warning: Virtual environment not found at .miavenv\
    echo Please run setup first or ensure you're in the correct directory
    echo.
)

echo Starting FastAPI server...
echo.
echo API Documentation will be available at: http://localhost:8000/docs
echo Health Check: http://localhost:8000/api/health
echo.
echo Press Ctrl+C to stop the server
echo ========================================================================
echo.

REM Start the FastAPI server with uvicorn
python -m uvicorn api_main:app --reload --host 0.0.0.0 --port 8000

pause
