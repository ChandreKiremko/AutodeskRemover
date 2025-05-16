@echo off
echo Autodesk Uninstaller Tool - Starting with Admin Rights
echo =======================================================

:: Check if running with admin rights
NET SESSION >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo This application requires administrator privileges to function properly.
    echo.
    echo Please right-click on this batch file and select "Run as administrator".
    echo.
    pause
    exit /B 1
)

:: Find the executable
set EXECUTABLE="Autodesk-Uninstaller-Tool.exe"
if not exist %EXECUTABLE% (
    if exist "dist\%EXECUTABLE%" (
        set EXECUTABLE="dist\Autodesk-Uninstaller-Tool.exe"
    ) else (
        echo Could not find Autodesk-Uninstaller-Tool.exe
        echo Please make sure this batch file is in the same directory as the executable.
        pause
        exit /B 1
    )
)

:: Run the application
echo Starting Autodesk Uninstaller Tool with administrator privileges...
echo.
start "" %EXECUTABLE%

exit /B 0