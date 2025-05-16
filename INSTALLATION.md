# Autodesk Uninstaller Tool - Installation Guide

This guide explains how to build and install the Autodesk Uninstaller Tool as a desktop application.

## Prerequisites

Before building the application, you need:

- Windows 10 or Windows 11
- Python 3.9 or higher installed
- Administrator privileges

## Build Options

### Option 1: Build using the build script (Recommended)

1. Right-click on the Command Prompt and select "Run as administrator"
2. Navigate to the folder containing the application files
3. Run the build script:
   ```
   python build_app.py
   ```
4. Once completed, you'll find the executable in the `dist` folder
5. Double-click the executable to run the application

### Option 2: Build manually with PyInstaller

1. Install PyInstaller:
   ```
   pip install pyinstaller
   ```

2. Run PyInstaller:
   ```
   pyinstaller autodesk_uninstaller.spec
   ```

3. The executable will be created in the `dist` folder

### Option 3: Creating an installer (Advanced)

If you want to create a proper Windows installer, you'll need to:

1. Download and install [Inno Setup](https://jrsoftware.org/isinfo.php)
2. Build the application using Option 1 or 2 above
3. Open the Inno Setup script (`installer/inno_setup_script.iss`) with Inno Setup
4. Compile the installer
5. The installer will be created in the `output` folder

## Running the Application

1. Double-click the `Autodesk-Uninstaller-Tool.exe` file
2. If prompted by User Account Control, click "Yes" to grant administrator privileges
3. The application will open in your default web browser
4. Use the interface to select and uninstall Autodesk products

## Distributing the Application

You can distribute the application in two ways:

1. **Standalone Executable**: 
   - Share the executable file (`dist/Autodesk-Uninstaller-Tool.exe`)
   - Users simply need to run it with administrator privileges

2. **Windows Installer**:
   - Share the installer file (`output/Autodesk-Uninstaller-Tool-Setup.exe`)
   - Users run the installer, which will install the application and create shortcuts

## Troubleshooting

If you encounter any issues:

1. Make sure you're running as administrator
2. Check the console output for any error messages
3. Verify that all necessary files are included in the distribution