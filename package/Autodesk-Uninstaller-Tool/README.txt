===================================================
AUTODESK UNINSTALLER TOOL - README
===================================================

This tool provides a simple way to uninstall Autodesk products from your system.

== IMPORTANT REQUIREMENTS ==

1. Windows 10 or Windows 11
2. Administrator privileges (essential)

== FILES INCLUDED ==

1. Autodesk-Uninstaller.ps1 - The PowerShell script that handles uninstallation
2. Run-Uninstaller.bat - Batch file to run the script with administrator privileges

== HOW TO USE ==

Method 1 - Quick Start:
1. Right-click on "Run-Uninstaller.bat"
2. Select "Run as administrator"
3. Follow the on-screen instructions

Method 2 - Manual Run:
1. Right-click on Windows PowerShell
2. Select "Run as administrator"
3. Navigate to this folder
4. Type: .\Autodesk-Uninstaller.ps1
5. Press Enter

== WHAT THIS TOOL DOES ==

1. Lists all installed Autodesk products
2. Lets you select which products to uninstall
3. Uninstalls the selected products
4. Optionally deletes the C:\Autodesk folder
5. Optionally restarts your computer

== TROUBLESHOOTING ==

- If you get a "script execution is disabled on this system" error, run:
  Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process

- If uninstallation fails for some products, try running the script again
  to catch any dependent products that need to be removed first.

== DISCLAIMER ==

This tool is provided as-is without warranty of any kind. Always back up 
important data before uninstalling software. The user assumes all risk 
of usage.

===================================================