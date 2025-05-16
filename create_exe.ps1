# Autodesk Uninstaller Tool - PowerShell Build Script

Write-Host "=============================================="
Write-Host "Autodesk Uninstaller Tool - Build Script"
Write-Host "=============================================="
Write-Host ""

# Check if running as Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "WARNING: This script is not running as Administrator." -ForegroundColor Yellow
    Write-Host "Some functions may not work correctly." -ForegroundColor Yellow
    Write-Host ""
}

# Check Python installation
Write-Host "Checking Python installation..."
try {
    $pythonVersion = python --version
    Write-Host "Found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Python is not installed or not in your PATH." -ForegroundColor Red
    Write-Host "Please install Python from https://www.python.org/downloads/"
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

# Install required packages
Write-Host ""
Write-Host "Installing required packages..."
python -m pip install --upgrade pip
python -m pip install pyinstaller

# Build the application
Write-Host ""
Write-Host "Building the application..."
python build_app.py

# Check if build was successful
if (Test-Path "dist\Autodesk-Uninstaller-Tool.exe") {
    Write-Host ""
    Write-Host "BUILD SUCCESSFUL!" -ForegroundColor Green
    Write-Host ""
    Write-Host "The executable is located at: dist\Autodesk-Uninstaller-Tool.exe"
    Write-Host ""
    Write-Host "To run the application:"
    Write-Host "1. Navigate to the dist folder"
    Write-Host "2. Right-click on 'Autodesk-Uninstaller-Tool.exe'"
    Write-Host "3. Select 'Run as administrator'"
} else {
    Write-Host ""
    Write-Host "BUILD FAILED!" -ForegroundColor Red
    Write-Host "Please check the output above for errors."
}

Write-Host ""
Write-Host "=============================================="
Write-Host ""
Read-Host "Press Enter to exit"