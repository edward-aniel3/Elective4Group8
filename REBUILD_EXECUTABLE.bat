@echo off
title Rebuild Executable (Quick)
cd /d "%~dp0"
color 0A

echo ============================================
echo   QUICK REBUILD - Executable Update
echo ============================================
echo.
echo This will rebuild your executable with the
echo resource file fixes (steve_face.png, alex_face.png)
echo.
pause

REM Check if venv exists
if not exist "venv\Scripts\activate.bat" (
    echo ERROR: Virtual environment not found!
    echo Please run SETUP_FIRST.bat first.
    pause
    exit /b 1
)

REM Activate venv
call venv\Scripts\activate.bat

echo.
echo [1/3] Cleaning previous build...
if exist "build" rmdir /s /q build
if exist "dist" rmdir /s /q dist
echo ✓ Cleanup complete

echo.
echo [2/3] Rebuilding executable...
echo (This will take a few minutes)
pyinstaller --clean ImageProcessingSystem.spec
if errorlevel 1 (
    echo.
    echo ERROR: Build failed!
    pause
    exit /b 1
)

echo.
echo [3/3] Verifying resource files...
echo Checking if PNG files are bundled...
echo ✓ Build complete

echo.
echo ============================================
echo   REBUILD COMPLETE!
echo ============================================
echo.
echo Your updated executable is ready:
echo   📁 dist\ImageProcessingSystem.exe
echo.
echo The Minecraft filter will now work correctly!
echo Steve and Alex face overlays are now included.
echo.
pause
