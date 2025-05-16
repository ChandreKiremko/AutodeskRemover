@echo off
echo Autodesk Uninstaller Tool
echo =======================
echo.

:: Check for administrator privileges
NET SESSION >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo This script requires administrator privileges.
    echo Please right-click this file and select "Run as administrator".
    echo.
    pause
    exit /B 1
)

echo Running with administrator privileges...
echo.

:: Set PowerShell execution policy for this process only
powershell -Command "Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process -Force"

:: Run the PowerShell script
echo Starting Autodesk Uninstaller...
powershell -ExecutionPolicy Bypass -File "%~dp0Autodesk-Uninstaller.ps1"

exit /B 0