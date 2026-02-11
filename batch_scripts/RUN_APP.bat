@echo off
title Image Processing System
cd /d "%~dp0"

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo ============================================
    echo   Virtual Environment Not Found!
    echo ============================================
    echo.
    echo Please run SETUP_FIRST.bat to set up the
    echo development environment before running the app.
    echo.
    pause
    exit /b 1
)

REM Create required folders
if not exist "input" mkdir input
if not exist "output" mkdir output

REM Activate virtual environment and run app
call venv\Scripts\activate.bat
echo Starting Image Processing System...
python main.py

