@echo off
echo Autodesk Uninstaller Tool (GUI Version)
echo =====================================
echo.

:: Check for administrator privileges
NET SESSION >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo This application requires administrator privileges to function properly.
    echo.
    echo Please right-click this file and select "Run as administrator".
    echo.
    pause
    exit /B 1
)

echo Running with administrator privileges...
echo.

:: Start the executable
echo Starting Autodesk Uninstaller Tool...
echo The application will open in your default web browser.
echo.
echo Please wait...
echo.

:: Run the application executable
start "" "%~dp0Autodesk-Uninstaller-Tool.exe"

exit /B 0