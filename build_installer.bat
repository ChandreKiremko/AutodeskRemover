@echo off
echo Building Autodesk Uninstaller Tool installer...

REM Convert SVG to ICO (assuming ImageMagick is installed)
REM If ImageMagick is not available, we'll skip this step and use a fallback icon
echo Converting icon...
IF EXIST "C:\Program Files\ImageMagick-7.0\magick.exe" (
    "C:\Program Files\ImageMagick-7.0\magick.exe" convert -background none static\images\app_icon.svg -define icon:auto-resize=256,128,64,48,32,16 static\images\app_icon.ico
) ELSE (
    echo ImageMagick not found. Using default icon.
    REM Copy a default icon if available
    IF EXIST "static\images\default_icon.ico" copy "static\images\default_icon.ico" "static\images\app_icon.ico"
)

REM Build the executable with PyInstaller
echo Building executable...
pyinstaller autodesk_uninstaller.spec --clean

REM Show completion message
echo.
IF EXIST "dist\Autodesk-Uninstaller-Tool.exe" (
    echo Build completed successfully!
    echo The installer can be found in the "dist" folder.
) ELSE (
    echo Build failed. Check the output for errors.
)

pause