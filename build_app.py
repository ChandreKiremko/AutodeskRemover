import os
import sys
import subprocess
import shutil
import platform

def main():
    """
    Build the Autodesk Uninstaller Tool into a standalone executable
    """
    print("Starting build process for Autodesk Uninstaller Tool...")
    
    # Check if PyInstaller is installed
    try:
        import PyInstaller
        print("PyInstaller found.")
    except ImportError:
        print("PyInstaller not found. Installing PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
    
    # Create the icon directory if it doesn't exist
    if not os.path.exists("static/images/app_icon.ico"):
        print("Converting SVG icon to ICO format...")
        try:
            # Try to create a simple ICO file (fallback if no conversion tools available)
            create_fallback_icon()
        except Exception as e:
            print(f"Warning: Could not create icon: {e}")
    
    # Ensure PowerShell script is properly copied to the build directory
    print("Copying PowerShell script to build directory...")
    os.makedirs("build/ps_scripts", exist_ok=True)
    
    # Copy the Autodesk-Uninstaller.ps1 file
    if os.path.exists("attached_assets/Autodesk-Uninstaller.ps1"):
        shutil.copy("attached_assets/Autodesk-Uninstaller.ps1", "build/ps_scripts/Autodesk-Uninstaller.ps1")
        print("PowerShell script copied successfully.")
    else:
        print("Warning: Could not find Autodesk-Uninstaller.ps1 script.")
    
    # Check if spec file exists, if not create it
    if not os.path.exists("autodesk_uninstaller.spec"):
        print("Creating PyInstaller spec file...")
        create_spec_file()
    
    # Build the executable
    print("\nBuilding executable with PyInstaller...")
    if platform.system() == "Windows":
        subprocess.call(["pyinstaller", "autodesk_uninstaller.spec", "--clean"])
    else:
        subprocess.call([sys.executable, "-m", "PyInstaller", "autodesk_uninstaller.spec", "--clean"])
    
    # Set distribution directory name
    dist_dir = "Autodesk-Uninstaller-Package"
    
    # Check if build was successful
    exe_path = os.path.join("dist", "Autodesk-Uninstaller-Tool.exe")
    if os.path.exists(exe_path):
        print("\nBuild completed successfully!")
        print(f"The executable can be found at: {os.path.abspath(exe_path)}")
        
        # Create a distribution package with additional files
        print("\nCreating distribution package...")
        os.makedirs(dist_dir, exist_ok=True)
        
        # Copy the executable
        shutil.copy(exe_path, os.path.join(dist_dir, "Autodesk-Uninstaller-Tool.exe"))
        
        # Copy the PowerShell script
        ps_script_path = "build/ps_scripts/Autodesk-Uninstaller.ps1"
        if os.path.exists(ps_script_path):
            shutil.copy(ps_script_path, os.path.join(dist_dir, "Autodesk-Uninstaller.ps1"))
        
        # Copy the run as admin batch file
        if os.path.exists("run_as_admin.bat"):
            shutil.copy("run_as_admin.bat", os.path.join(dist_dir, "run_as_admin.bat"))
        
        # Copy documentation
        if os.path.exists("README.md"):
            shutil.copy("README.md", os.path.join(dist_dir, "README.md"))
        if os.path.exists("LICENSE.txt"):
            shutil.copy("LICENSE.txt", os.path.join(dist_dir, "LICENSE.txt"))
        if os.path.exists("INSTALLATION.md"):
            shutil.copy("INSTALLATION.md", os.path.join(dist_dir, "INSTALLATION.md"))
        
        print(f"Distribution package created at: {os.path.abspath(dist_dir)}")
    else:
        print("\nBuild failed. Check the output for errors.")
    
    print("\nTo distribute the application:")
    print(f"Share the entire '{dist_dir}' folder")
    print("Users need to run the executable as Administrator to uninstall Autodesk products")

def create_fallback_icon():
    """Create a simple fallback icon if conversion tools aren't available"""
    # Just copy an existing file if available
    if os.path.exists("static/images/default_icon.ico"):
        shutil.copy("static/images/default_icon.ico", "static/images/app_icon.ico")
    else:
        # We'll skip this for now - PyInstaller will use a default icon
        pass

def create_spec_file():
    """Create PyInstaller spec file"""
    with open("autodesk_uninstaller.spec", "w") as f:
        f.write("""# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['desktop_app.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('templates', 'templates'), 
        ('static', 'static'),
        ('attached_assets', 'attached_assets'),
        ('build/ps_scripts', 'ps_scripts')
    ],
    hiddenimports=['engineio.async_drivers.threading'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Autodesk-Uninstaller-Tool',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='static/images/app_icon.ico' if os.path.exists('static/images/app_icon.ico') else None,
    uac_admin=True,
)
""")

if __name__ == "__main__":
    main()