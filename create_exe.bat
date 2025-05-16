@echo off
echo ==============================================
echo Autodesk Uninstaller Tool - Build Script
echo ==============================================
echo.

echo Checking Python installation...
python --version
if %ERRORLEVEL% neq 0 (
    echo ERROR: Python is not installed or not in your PATH.
    echo Please install Python from https://www.python.org/downloads/
    pause
    exit /b 1
)

echo.
echo Installing required packages...
python -m pip install --upgrade pip
python -m pip install pyinstaller

echo.
echo Building the application...
python build_app.py

echo.
if exist "dist\Autodesk-Uninstaller-Tool.exe" (
    echo BUILD SUCCESSFUL!
    echo.
    echo The executable is located at: dist\Autodesk-Uninstaller-Tool.exe
    echo.
    echo To run the application:
    echo 1. Navigate to the dist folder
    echo 2. Right-click on "Autodesk-Uninstaller-Tool.exe"
    echo 3. Select "Run as administrator"
) else (
    echo BUILD FAILED!
    echo Please check the output above for errors.
)

echo.
echo ==============================================
echo.
pause