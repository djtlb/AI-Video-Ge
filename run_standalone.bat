@echo off
REM run_standalone.bat - Windows version of the standalone runner

echo =====================================================
echo   AI Avatar Video - Standalone Mode (Windows)
echo =====================================================

set PORT=8084
if not "%1"=="" set PORT=%1

REM Check if Python is installed
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Python is not installed or not in PATH. Please install Python 3.8 or higher.
    exit /b 1
)

REM Check if virtual environment exists
if not exist venv (
    echo Setting up Python virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate

REM Install dependencies
echo Checking and installing dependencies...
pip install -q -r requirements.txt

REM Initialize database if needed
if not exist app.db (
    echo Initializing database...
    python init_db.py
)

REM Make sure storage directories exist
if not exist app\storage\characters mkdir app\storage\characters
if not exist app\storage\renders mkdir app\storage\renders
if not exist app\storage\thumbs mkdir app\storage\thumbs

REM Kill any existing server on the same port (Windows version)
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :%PORT%') do (
    taskkill /F /PID %%a >nul 2>nul
)

REM Start the application
echo Starting application...
start /B python -m uvicorn app.main:app --host 127.0.0.1 --port %PORT%

REM Wait for the server to start
echo Waiting for application to start...
timeout /t 5 /nobreak >nul

REM Open browser
echo Opening browser...
start http://localhost:%PORT%/

echo.
echo =====================================================
echo AI Avatar Video is running at: http://localhost:%PORT%/
echo Close this window to stop the application
echo =====================================================

REM Keep the window open
pause > nul
