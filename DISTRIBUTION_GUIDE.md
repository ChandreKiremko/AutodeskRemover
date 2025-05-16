# Autodesk Uninstaller Tool - Distribution Guide

This guide explains how to distribute the Autodesk Uninstaller Tool to end users.

## Package Contents

After building the application, the distribution package should contain:

- **Autodesk-Uninstaller-Tool.exe** - The main application executable
- **run_as_admin.bat** - Helper script to ensure the application runs with administrative privileges
- **Autodesk-Uninstaller.ps1** - The original PowerShell script (included for reference)
- **README.md** - Basic information about the application
- **INSTALLATION.md** - Installation instructions
- **LICENSE.txt** - License information

## Distribution Options

### Option 1: Simple ZIP Distribution

1. Compress the entire `Autodesk-Uninstaller-Package` folder into a ZIP file
2. Share the ZIP file with users
3. Instruct users to:
   - Extract the ZIP file to a location on their computer
   - Run `run_as_admin.bat` or right-click `Autodesk-Uninstaller-Tool.exe` and select "Run as administrator"

### Option 2: Create an Installer (Recommended)

For a more professional distribution, create a Windows installer:

1. Download and install [Inno Setup](https://jrsoftware.org/isinfo.php)
2. Open the included Inno Setup script (`installer/inno_setup_script.iss`)
3. Adjust settings as needed (publisher name, version, etc.)
4. Compile the installer
5. Share the resulting installer file with users
6. Users run the installer, which will create start menu shortcuts and properly register the application

## User Instructions

Provide these instructions to your users:

1. Run the application with administrator privileges (required to uninstall software)
2. Select the Autodesk products to uninstall from the list
3. Choose additional options if desired:
   - Delete C:\Autodesk folder
   - Restart computer after uninstallation
4. Click "Uninstall Selected" and confirm when prompted
5. Monitor the progress in the log area

## Requirements

Inform users that the application requires:

- Windows 10 or Windows 11
- Administrator privileges
- .NET Framework 4.5 or higher (normally pre-installed on modern Windows)

## Troubleshooting for Users

Include these troubleshooting tips for your users:

1. **"The application won't start"** - Make sure they run it as administrator
2. **"No products appear in the list"** - Verify they're running as administrator and have Autodesk products installed
3. **"Uninstallation failed"** - Check the logs for specific error messages; some products may require manual uninstallation
4. **"The application looks strange"** - Ensure their web browser is up to date

## Support

Consider adding your contact information or creating a support channel for users who encounter issues.