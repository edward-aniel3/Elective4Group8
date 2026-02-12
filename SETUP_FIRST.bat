@echo off
title Image Processing System - First Time Setup
cd /d "%~dp0"

echo ============================================
echo   IMAGE PROCESSING SYSTEM - SETUP
echo ============================================
echo.
echo Checking Python...
python --version
if errorlevel 1 (
    echo.
    echo ERROR: Python is not installed or not in PATH.
    echo Download Python from https://www.python.org
    echo Make sure to check "Add Python to PATH" during install.
    pause
    exit /b 1
)

echo.
echo Creating virtual environment...
if exist "venv" (
    echo Virtual environment already exists. Removing old one...
    rmdir /s /q venv
)
python -m venv venv
if errorlevel 1 (
    echo.
    echo ERROR: Failed to create virtual environment.
    pause
    exit /b 1
)

echo.
echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Installing required packages in virtual environment...
pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo ERROR: Failed to install packages.
    echo Try running: pip install opencv-python numpy Pillow pytest
    pause
    exit /b 1
)

echo.
echo ============================================
echo   SETUP COMPLETE!
echo ============================================
echo.
echo Virtual environment created and packages installed.
echo.
echo Next steps:
echo   1. Run RUN_APP.bat to launch the application
echo   2. Run BUILD_EXECUTABLE.bat to create a standalone .exe
echo.
pause
echo   SETUP COMPLETE!
echo ============================================
echo.
echo Virtual environment created and packages installed.
echo You can now double-click RUN_APP.bat to
echo start the Image Processing System.
echo.
pause
