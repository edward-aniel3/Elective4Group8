@echo off
title Image Processing System
cd /d "%~dp0"

REM Check if executable exists
if not exist "ImageProcessingSystem.exe" (
    echo ERROR: ImageProcessingSystem.exe not found!
    echo.
    echo Please build the executable first using BUILD_EXECUTABLE.bat
    echo.
    pause
    exit /b 1
)

REM Create required folders
if not exist "input" mkdir input
if not exist "output" mkdir output

REM Run the application
start "" "ImageProcessingSystem.exe"
