@echo off
title Image Processing System - BUILD EXECUTABLE
cd /d "%~dp0"
color 0A

echo ============================================
echo   IMAGE PROCESSING SYSTEM
echo   EXECUTABLE BUILD SCRIPT
echo ============================================
echo.
echo This script will create a standalone .exe
echo No Python installation needed to run it!
echo.
pause

REM ── Step 1: Check Python ──
echo.
echo [1/5] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found! Please install Python first.
    echo Download from: https://www.python.org
    pause
    exit /b 1
)
python --version
echo ✓ Python found

REM ── Step 2: Create/Activate virtual environment ──
echo.
echo [2/5] Setting up virtual environment...
if not exist "venv" (
    echo Creating new virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
)
call venv\Scripts\activate.bat
echo ✓ Virtual environment ready

REM ── Step 3: Install dependencies ──
echo.
echo [3/5] Installing dependencies (this may take a few minutes)...
pip install --upgrade pip >nul 2>&1
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo ✓ Dependencies installed

REM ── Step 4: Clean previous builds ──
echo.
echo [4/5] Cleaning previous builds...
if exist "build" rmdir /s /q build
if exist "dist" rmdir /s /q dist
if exist "__pycache__" rmdir /s /q __pycache__
echo ✓ Cleanup complete

REM ── Step 5: Build executable ──
echo.
echo [5/5] Building executable with PyInstaller...
echo This will take several minutes - please be patient!
echo.
pyinstaller --clean ImageProcessingSystem.spec
if errorlevel 1 (
    echo.
    echo ERROR: Build failed!
    pause
    exit /b 1
)

echo.
echo ============================================
echo   BUILD COMPLETE!
echo ============================================
echo.
echo Your executable is ready:
echo   📁 dist\ImageProcessingSystem.exe
echo.
echo The .exe includes everything needed and can run
echo on any Windows PC without Python installed.
echo.
echo IMPORTANT: The executable needs these folders
echo in the same directory to work:
echo   - input\  (for source images)
echo   - output\ (for processed results)
echo.
echo These folders will be created automatically
echo when you first run the .exe
echo.
pause
