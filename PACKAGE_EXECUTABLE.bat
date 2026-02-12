@echo off
title Package Executable for Distribution
cd /d "%~dp0"
color 0B

echo ============================================
echo   PACKAGE EXECUTABLE FOR DISTRIBUTION
echo ============================================
echo.

REM Check if executable exists
if not exist "dist\ImageProcessingSystem.exe" (
    echo ERROR: ImageProcessingSystem.exe not found in dist\ folder
    echo.
    echo Please run BUILD_EXECUTABLE.bat first to create the executable.
    echo.
    pause
    exit /b 1
)

REM Create package directory
set PACKAGE_DIR=ImageProcessingSystem_Portable
if exist "%PACKAGE_DIR%" rmdir /s /q "%PACKAGE_DIR%"
mkdir "%PACKAGE_DIR%"

echo [1/4] Copying executable...
copy "dist\ImageProcessingSystem.exe" "%PACKAGE_DIR%\" >nul
echo ✓ Executable copied

echo [2/4# Creating folders...
mkdir "%PACKAGE_DIR%\input"
mkdir "%PACKAGE_DIR%\output"
echo ✓ Folders created

echo [3/4] Copying documentation...
copy "EXECUTABLE_README.md" "%PACKAGE_DIR%\README.md" >nul
copy "RUN_EXECUTABLE.bat" "%PACKAGE_DIR%\" >nul
echo ✓ Documentation copied

echo [4/4] Creating ZIP archive...
if exist "ImageProcessingSystem_Portable.zip" del "ImageProcessingSystem_Portable.zip"
powershell -command "Compress-Archive -Path '%PACKAGE_DIR%\*' -DestinationPath 'ImageProcessingSystem_Portable.zip'"
if errorlevel 1 (
    echo WARNING: Could not create ZIP. Package folder is ready though.
) else (
    echo ✓ ZIP archive created
)

echo.
echo ============================================
echo   PACKAGING COMPLETE!
echo ============================================
echo.
echo Package location:
echo   📁 %PACKAGE_DIR%\
echo   📦 ImageProcessingSystem_Portable.zip
echo.
echo The package includes:
echo   ✓ ImageProcessingSystem.exe
echo   ✓ RUN_EXECUTABLE.bat
echo   ✓ README.md
echo   ✓ input\ and output\ folders
echo.
echo This package can be distributed to any Windows PC!
echo No Python installation required on target machines.
echo.
pause
