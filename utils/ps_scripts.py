import subprocess
import logging
import ctypes
import sys
import os
import re
import tempfile
import time
import json

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def check_admin_rights():
    """Check if the script is running with administrative privileges"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except AttributeError:
        # Not running on Windows
        return False
    except Exception as e:
        logger.error(f"Error checking admin rights: {str(e)}")
        return False

def run_powershell_command(command, capture_output=True):
    """Run a PowerShell command and return the output"""
    try:
        # Create a full PowerShell command
        full_command = ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", command]
        
        # Run the command
        result = subprocess.run(
            full_command,
            capture_output=capture_output,
            text=True,
            check=False  # Don't raise exception on non-zero exit code
        )
        
        if result.returncode != 0 and result.stderr:
            logger.warning(f"PowerShell command exited with code {result.returncode}: {result.stderr}")
        
        return result.stdout if capture_output else None
    except Exception as e:
        logger.error(f"Error running PowerShell command: {str(e)}")
        raise Exception(f"Failed to execute PowerShell command: {str(e)}")

def get_installed_autodesk_products():
    """Get a list of installed Autodesk products"""
    ps_command = """
    $allInstalledApps = @()
    $allInstalledApps = Get-ItemProperty -Path "HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\*" -ErrorAction SilentlyContinue
    $allInstalledApps += Get-ItemProperty -Path "HKLM:\\SOFTWARE\\WOW6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\*" -ErrorAction SilentlyContinue
    
    $autodeskApps = $allInstalledApps | Where-Object {
        $_.DisplayName -like "*Autodesk*" -or 
        $_.Publisher -like "*Autodesk*" -or 
        $_.DisplayName -like "*AutoCAD*" -or 
        $_.DisplayName -like "*Revit*"
    } | Select-Object DisplayName, Publisher, PSChildName, UninstallString -Unique
    
    $autodeskApps | ConvertTo-Json
    """
    
    try:
        output = run_powershell_command(ps_command)
        if not output or output.strip() == "":
            return []
        
        products = json.loads(output)
        
        # Ensure we have a list even if only one product is found
        if not isinstance(products, list):
            products = [products]
            
        # Process the products to ensure all fields exist
        processed_products = []
        for product in products:
            if product.get('DisplayName'):  # Skip any entries without a DisplayName
                processed_products.append({
                    'displayName': product.get('DisplayName', 'Unknown Product'),
                    'publisher': product.get('Publisher', 'Unknown Publisher'),
                    'psChildName': product.get('PSChildName', ''),
                    'uninstallString': product.get('UninstallString', '')
                })
        
        return processed_products
    except Exception as e:
        logger.error(f"Error getting installed Autodesk products: {str(e)}")
        raise Exception(f"Failed to retrieve installed Autodesk products: {str(e)}")

def create_temp_ps_script():
    """Create a temporary PowerShell script file with the uninstallation functions"""
    try:
        # Get the path to Autodesk-Uninstaller.ps1
        script_content = """
function Get-AutodeskProductSelection {
    param (
        [Parameter(Mandatory=$true)]
        [string[]]$TargetPSChildNames
    )
    
    Write-Output "Selecting products with the following PSChildNames: $($TargetPSChildNames -join ', ')"
    return $TargetPSChildNames
}

function Uninstall-AutodeskProductsByPSChildName {
    param(
        [Parameter(Mandatory=$true)]
        [string[]]$TargetPSChildNames
    )

    if ($TargetPSChildNames.Count -eq 0) {
        Write-Output "No target products specified for uninstallation in this pass."
        return @{
            "status" = "warning"
            "message" = "No target products specified"
        }
    }

    $currentAppsRaw = @()
    $currentAppsRaw = Get-ItemProperty -Path "HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\*" -ErrorAction SilentlyContinue
    $currentAppsRaw += Get-ItemProperty -Path "HKLM:\\SOFTWARE\\WOW6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\*" -ErrorAction SilentlyContinue
    
    $currentAutodeskApps = $currentAppsRaw | Where-Object {
        $_.DisplayName -like "*Autodesk*" -or 
        $_.Publisher -like "*Autodesk*" -or 
        $_.DisplayName -like "*AutoCAD*" -or 
        $_.DisplayName -like "*Revit*"
    } | Select-Object DisplayName, Publisher, PSChildName, UninstallString -Unique

    $appsToUninstallThisPass = $currentAutodeskApps | Where-Object { $TargetPSChildNames -contains $_.PSChildName }

    if ($appsToUninstallThisPass.Count -eq 0) {
        Write-Output "All selected Autodesk products appear to be uninstalled, or were not found in this pass."
        return @{
            "status" = "info"
            "message" = "All selected products appear to be uninstalled or were not found"
        }
    }

    Write-Output "Found $($appsToUninstallThisPass.Count) selected Autodesk products to attempt uninstalling in this pass:"
    
    $results = @()
    
    foreach ($app in $appsToUninstallThisPass) {
        $uninstallResult = @{
            "displayName" = $app.DisplayName
            "status" = "unknown"
            "message" = ""
        }
        
        try {
            # Uninstall Autodesk Access
            if ($app.DisplayName -match "Autodesk Access"){
                Write-Output "Uninstalling $($app.DisplayName)..."
                Start-Process -FilePath "C:\\Program Files\\Autodesk\\AdODIS\\V1\\Installer.exe" -ArgumentList "-q -i uninstall --trigger_point system -m C:\\ProgramData\\Autodesk\\ODIS\\metadata\\{A3158B3E-5F28-358A-BF1A-9532D8EBC811}\\pkg.access.xml -x `"C:\\Program Files\\Autodesk\\AdODIS\\V1\\SetupRes\\manifest.xsd`" --manifest_type package" -NoNewWindow -Wait
                $uninstallResult.status = "success"
                $uninstallResult.message = "Successfully uninstalled"
            }
            # Uninstall Autodesk Identity Manager
            elseif ($app.DisplayName -match "Autodesk Identity Manager"){
                Write-Output "Uninstalling $($app.DisplayName)..."
                Start-Process -FilePath "C:\\Program Files\\Autodesk\\AdskIdentityManager\\uninstall.exe" -ArgumentList "--mode unattended" -NoNewWindow -Wait
                $uninstallResult.status = "success"
                $uninstallResult.message = "Successfully uninstalled"
            }
            # Uninstall Autodesk Genuine Service
            elseif ($app.DisplayName -match "Autodesk Genuine Service"){
                Write-Output "Uninstalling $($app.DisplayName)..."
                Remove-Item "$Env:ALLUSERSPROFILE\\Autodesk\\Adlm\\ProductInformation.pit" -Force -ErrorAction:SilentlyContinue
                Remove-Item "$Env:userprofile\\AppData\\Local\\Autodesk\\Genuine Autodesk Service\\id.dat" -Force -ErrorAction:SilentlyContinue
                msiexec.exe /x "{21DE6405-91DE-4A69-A8FB-483847F702C6}" /qn /norestart
                Start-Sleep -Seconds 3
                $uninstallResult.status = "success"
                $uninstallResult.message = "Successfully uninstalled"
            }
            # Uninstall Carbon Insights for Revit
            elseif ($app.DisplayName -like "*Carbon Insights for Revit*"){
                Write-Output "Uninstalling $($app.DisplayName)..."
                Start-Process -FilePath "C:\\Program Files\\Autodesk\\AdODIS\\V1\\Installer.exe" -ArgumentList "-q -i uninstall --trigger_point system -m C:\\ProgramData\\Autodesk\\ODIS\\metadata\\{006E0C25-2C15-39A8-8590-AA5AD7D395D4}\\pkg.RTCA.xml -x `"C:\\Program Files\\Autodesk\\AdODIS\\V1\\SetupRes\\manifest.xsd`" --manifest_type package" -NoNewWindow -Wait
                $uninstallResult.status = "success"
                $uninstallResult.message = "Successfully uninstalled"
            }
            # Generic ODIS Uninstaller (using bundleManifest.xml)
            elseif ($app.UninstallString -and $app.UninstallString -like "*installer.exe*") {
                $installerPath = "C:\\Program Files\\Autodesk\\AdODIS\\V1\\Installer.exe" # Default ODIS installer
                # Attempt to parse installer path from UninstallString if it's different
                if ($app.UninstallString -match "^`"?(.*?installer.exe)`"?($|\\s)") {
                    $extractedPath = $Matches[1]
                    if (Test-Path $extractedPath) {
                        $installerPath = $extractedPath
                    }
                }
                
                $odisMetaDataPath = "C:\\ProgramData\\Autodesk\\ODIS\\metadata\\$($app.PSChildName)"
                $bundleManifestPath = Join-Path $odisMetaDataPath "bundleManifest.xml"
                $setupResManifestPath = Join-Path $odisMetaDataPath "SetupRes\\manifest.xsd"

                if ((Test-Path $bundleManifestPath) -and (Test-Path $setupResManifestPath)) {
                    Write-Output "Uninstalling $($app.DisplayName) using ODIS (bundle)..."
                    $argumentList = "-q -i uninstall --trigger_point system -m `"$bundleManifestPath`" -x `"$setupResManifestPath`""
                    Start-Process -FilePath $installerPath -ArgumentList $argumentList -NoNewWindow -Wait
                    Start-Sleep -Seconds 3
                    $uninstallResult.status = "success"
                    $uninstallResult.message = "Successfully uninstalled using ODIS bundle"
                } else {
                    Write-Output "Warning: ODIS bundle manifest not found for $($app.DisplayName). Trying generic MSIEXEC if applicable."
                    # Fall through to MSIEXEC if PSChildName is a GUID
                    if ($app.PSChildName -match '^{([0-9A-Fa-f]{8}-([0-9A-Fa-f]{4}-){3}[0-9A-Fa-f]{12})}$') {
                        Write-Output "Attempting to uninstall $($app.DisplayName) using msiexec (Product Code as fallback)..."
                        Start-Process -FilePath msiexec.exe -ArgumentList "/x `"$($app.PSChildName)`" /qn /norestart" -NoNewWindow -Wait
                        Start-Sleep -Seconds 3
                        $uninstallResult.status = "success"
                        $uninstallResult.message = "Successfully uninstalled using MSI fallback"
                    } else {
                        $uninstallResult.status = "warning"
                        $uninstallResult.message = "No ODIS bundle and PSChildName is not a GUID. Manual uninstallation may be required."
                    }
                }
            }
            # Generic MSI uninstallation (using product code)
            else {
                if ($app.PSChildName -match '^{([0-9A-Fa-f]{8}-([0-9A-Fa-f]{4}-){3}[0-9A-Fa-f]{12})}$') {
                    Write-Output "Uninstalling $($app.DisplayName) using msiexec (Product Code)..."
                    Start-Process -FilePath msiexec.exe -ArgumentList "/x `"$($app.PSChildName)`" /qn /norestart" -NoNewWindow -Wait
                    Start-Sleep -Seconds 3
                    $uninstallResult.status = "success"
                    $uninstallResult.message = "Successfully uninstalled using MSI"
                } else {
                    $uninstallResult.status = "error"
                    $uninstallResult.message = "No clear uninstallation method found. PSChildName not a GUID and no installer.exe found."
                }
            }
        }
        catch {
            $uninstallResult.status = "error"
            $uninstallResult.message = "Error: $($_.Exception.Message)"
        }
        
        $results += $uninstallResult
    }
    
    return $results | ConvertTo-Json -Depth 3
}

# Expose a function to delete the Autodesk folder
function Remove-AutodeskFolder {
    if (Test-Path 'C:\\Autodesk') {
        try {
            Remove-Item -Path 'C:\\Autodesk' -Recurse -Force -ErrorAction Stop
            return $true
        } catch {
            Write-Error "Failed to delete C:\\Autodesk folder: $_"
            return $false
        }
    } else {
        Write-Output "C:\\Autodesk folder does not exist."
        return $true # Return true since there's nothing to delete
    }
}

# Expose a function to restart the computer
function Restart-ComputerForced {
    Restart-Computer -Force
}
"""
        
        # Create a temporary file and write the script content
        fd, script_path = tempfile.mkstemp(suffix='.ps1')
        with os.fdopen(fd, 'w') as f:
            f.write(script_content)
        
        logger.debug(f"Created temporary PowerShell script at {script_path}")
        return script_path
    except Exception as e:
        logger.error(f"Error creating temporary PowerShell script: {str(e)}")
        raise Exception(f"Failed to create temporary PowerShell script: {str(e)}")

def uninstall_products(product_ids):
    """Uninstall selected Autodesk products"""
    try:
        # Create temporary script file
        script_path = create_temp_ps_script()
        
        # Format the product IDs as a PowerShell array
        product_ids_str = ",".join([f'"{id}"' for id in product_ids])
        
        # Create the PowerShell command to run the uninstallation
        ps_command = f". {script_path}; "
        ps_command += f"$productIds = @({product_ids_str}); "
        
        results = []
        
        # Run 3 passes to handle dependencies
        for i in range(3):
            logger.info(f"Running uninstallation pass {i+1} of 3")
            
            # Run the uninstallation for this pass
            pass_command = ps_command + f"Uninstall-AutodeskProductsByPSChildName -TargetPSChildNames $productIds"
            output = run_powershell_command(pass_command)
            
            try:
                # Parse results if possible
                pass_results = json.loads(output)
                if isinstance(pass_results, list):
                    results.extend(pass_results)
                elif isinstance(pass_results, dict):
                    # Single result or status message
                    results.append(pass_results)
                
                logger.debug(f"Pass {i+1} results: {pass_results}")
            except json.JSONDecodeError:
                # If we can't parse as JSON, just add the raw output
                logger.warning(f"Could not parse uninstallation output as JSON: {output}")
                results.append({
                    "status": "unknown", 
                    "message": f"Uninstallation pass {i+1} completed with unparseable output",
                    "rawOutput": output
                })
            
            # Wait a bit before next pass
            if i < 2:  # Don't wait after the last pass
                time.sleep(5)
        
        # Clean up the temporary script file
        try:
            os.unlink(script_path)
        except Exception as e:
            logger.warning(f"Could not delete temporary script file {script_path}: {str(e)}")
        
        return results
    except Exception as e:
        logger.error(f"Error uninstalling products: {str(e)}")
        raise Exception(f"Failed to uninstall products: {str(e)}")

def delete_autodesk_folder():
    """Delete the C:\Autodesk folder"""
    try:
        # Create temporary script file
        script_path = create_temp_ps_script()
        
        # Create the PowerShell command
        ps_command = f". {script_path}; Remove-AutodeskFolder"
        
        # Run the command
        output = run_powershell_command(ps_command)
        
        # Clean up the temporary script file
        try:
            os.unlink(script_path)
        except Exception as e:
            logger.warning(f"Could not delete temporary script file {script_path}: {str(e)}")
        
        # Parse the result
        if output.strip().lower() == "true":
            return True
        else:
            logger.warning(f"Failed to delete Autodesk folder: {output}")
            return False
    except Exception as e:
        logger.error(f"Error deleting Autodesk folder: {str(e)}")
        return False

def restart_computer():
    """Restart the computer"""
    try:
        # Create temporary script file
        script_path = create_temp_ps_script()
        
        # Create the PowerShell command
        ps_command = f". {script_path}; Restart-ComputerForced"
        
        # Run the command without capturing output
        run_powershell_command(ps_command, capture_output=False)
        
        # We'll never reach here if the restart is successful
        return True
    except Exception as e:
        logger.error(f"Error restarting computer: {str(e)}")
        return False
