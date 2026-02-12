@echo off
title Verify Environment Setup
cd /d "%~dp0"
color 0E

echo ============================================
echo   ENVIRONMENT VERIFICATION
echo ============================================
echo.

set ERROR_COUNT=0

REM Check Python
echo [1/8] Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ FAIL: Python not found
    set /a ERROR_COUNT+=1
) else (
    python --version
    echo ✓ PASS
)

REM Check virtual environment
echo.
echo [2/8] Checking virtual environment...
if exist "venv\Scripts\python.exe" (
    echo ✓ PASS: Virtual environment exists
) else (
    echo ❌ FAIL: Virtual environment not found
    echo    Run SETUP_FIRST.bat to create it
    set /a ERROR_COUNT+=1
)

REM Check required folders
echo.
echo [3/8] Checking required folders...
set FOLDERS_OK=1
if not exist "input" (
    echo ❌ FAIL: input\ folder missing
    set FOLDERS_OK=0
    set /a ERROR_COUNT+=1
)
if not exist "output" (
    echo ❌ FAIL: output\ folder missing
    set FOLDERS_OK=0
    set /a ERROR_COUNT+=1
)
if %FOLDERS_OK%==1 (
    echo ✓ PASS: input\ and output\ folders exist
)

REM Check Python modules exist
echo.
echo [4/8] Checking Python modules...
set MODULES_OK=1
if not exist "main.py" set MODULES_OK=0
if not exist "background_remover.py" set MODULES_OK=0
if not exist "puzzle_shuffle.py" set MODULES_OK=0
if not exist "minecraft_filter.py" set MODULES_OK=0
if not exist "mosaic_tile_effect.py" set MODULES_OK=0
if %MODULES_OK%==1 (
    echo ✓ PASS: All Python modules found
) else (
    echo ❌ FAIL: Some Python modules missing
    set /a ERROR_COUNT+=1
)

REM Check test files
echo.
echo [5/8] Checking test files...
set TESTS_OK=1
if not exist "test_background_remover.py" set TESTS_OK=0
if not exist "test_puzzle_shuffle.py" set TESTS_OK=0
if not exist "test_minecraft_filter.py" set TESTS_OK=0
if not exist "test_mosaic_tile_effect.py" set TESTS_OK=0
if %TESTS_OK%==1 (
    echo ✓ PASS: All test files found
) else (
    echo ❌ FAIL: Some test files missing
    set /a ERROR_COUNT+=1
)

REM Check batch scripts
echo.
echo [6/8] Checking batch scripts...
set SCRIPTS_OK=1
if not exist "SETUP_FIRST.bat" set SCRIPTS_OK=0
if not exist "RUN_APP.bat" set SCRIPTS_OK=0
if not exist "BUILD_EXECUTABLE.bat" set SCRIPTS_OK=0
if %SCRIPTS_OK%==1 (
    echo ✓ PASS: All batch scripts found
) else (
    echo ❌ FAIL: Some batch scripts missing
    set /a ERROR_COUNT+=1
)

REM Check PyInstaller spec
echo.
echo [7/8] Checking PyInstaller configuration...
if exist "ImageProcessingSystem.spec" (
    echo ✓ PASS: PyInstaller spec file found
) else (
    echo ❌ FAIL: ImageProcessingSystem.spec missing
    set /a ERROR_COUNT+=1
)

REM Check requirements.txt
echo.
echo [8/8] Checking requirements.txt...
if exist "requirements.txt" (
    findstr /C:"pyinstaller" requirements.txt >nul
    if errorlevel 1 (
        echo ⚠️  WARNING: pyinstaller not in requirements.txt
    ) else (
        echo ✓ PASS: requirements.txt is complete
    )
) else (
    echo ❌ FAIL: requirements.txt missing
    set /a ERROR_COUNT+=1
)

REM Summary
echo.
echo ============================================
if %ERROR_COUNT%==0 (
    echo   ✓ ALL CHECKS PASSED
    echo ============================================
    echo.
    echo Your environment is ready!
    echo.
    echo Next steps:
    echo   • Run RUN_APP.bat to test the application
    echo   • Run BUILD_EXECUTABLE.bat to create .exe
    echo.
) else (
    echo   ❌ %ERROR_COUNT% CHECK(S) FAILED
    echo ============================================
    echo.
    echo Please fix the issues above before continuing.
    echo Run SETUP_FIRST.bat if you haven't already.
    echo.
)

pause
