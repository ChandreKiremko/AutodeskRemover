# Autodesk Uninstaller Tool

A user-friendly desktop application for safely uninstalling Autodesk products from your Windows system.

## Features

- Simple graphical interface for managing Autodesk product uninstallation
- Select which Autodesk products to uninstall
- Option to delete the C:\Autodesk folder
- Option to restart your computer after uninstallation
- Real-time progress logging

## Requirements

- Windows operating system
- Administrator privileges (required to uninstall software)

## Installation Options

### Option 1: Run as a Web Application

1. Install Python 3.9 or higher
2. Install the requirements: `pip install -r requirements.txt`
3. Run the application: `python main.py`
4. Open your browser and go to: http://localhost:5000

### Option 2: Build as a Desktop Application

1. Install Python 3.9 or higher
2. Install the requirements: `pip install -r requirements.txt`
3. Run the build script: `python build_app.py`
4. After building, find the executable in the `dist` folder
5. Run the executable as Administrator

## How to Use

1. Launch the application (requires administrator privileges)
2. Select the Autodesk products you want to uninstall
3. Choose additional options:
   - Delete C:\Autodesk folder
   - Restart computer after uninstallation
4. Click the "Uninstall Selected" button
5. Confirm the uninstallation
6. Wait for the process to complete

## Important Notes

- **Run as Administrator**: This tool requires administrator privileges to uninstall software
- **Backup Your Data**: Always back up important files before uninstalling software
- **No Internet Required**: This tool works offline and doesn't send any data

## Technical Details

This application is built with:
- Python
- Flask web framework
- Bootstrap for UI
- PowerShell for the uninstallation logic

## License

This project is available as open source under the terms of the MIT License.