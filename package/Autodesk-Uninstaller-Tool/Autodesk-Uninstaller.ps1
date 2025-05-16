# function Autodesk-Uninstaller {
# ... (original function content removed and replaced by the functions below) ...
# }

# Some apps are the depending apps of others. So, run the function three times to make sure all apps got removed.
# $i = 0
# for ($i = 1; $i -lt 5; $i++) {
#    Autodesk-Uninstaller
# }

# Uncomment the below line to delete the C:\Autodesk folder.
# Remove-Item -Path 'C:\Autodesk' -Recurse -Force

# Uncomment the below line to restart the computer automatically when complete.
# Restart-Computer -Force

# Clear-Host
# Write-Host "The uninstallation process has been completed. It is recommended to restart the computer." -ForegroundColor Green


function Get-AutodeskProductSelection {
    Write-Host "Discovering installed Autodesk products..." -ForegroundColor Cyan
    $allInstalledApps = @()
    $allInstalledApps = Get-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\*" -ErrorAction SilentlyContinue
    $allInstalledApps += Get-ItemProperty -Path "HKLM:\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\*" -ErrorAction SilentlyContinue
    
    $autodeskApps = $allInstalledApps | Where-Object {
        $_.DisplayName -like "*Autodesk*" -or 
        $_.Publisher -like "*Autodesk*" -or 
        $_.DisplayName -like "*AutoCAD*" -or 
        $_.DisplayName -like "*Revit*"
    } | Select-Object DisplayName, Publisher, PSChildName, UninstallString -Unique

    if ($autodeskApps.Count -eq 0) {
        Write-Host "No Autodesk products found installed." -ForegroundColor Yellow
        return @() 
    }

    Write-Host "Found the following Autodesk products:" -ForegroundColor Yellow
    for ($i = 0; $i -lt $autodeskApps.Count; $i++) {
        Write-Host ("{0}. {1}" -f ($i + 1), $autodeskApps[$i].DisplayName)
    }
    Write-Host "" 

    $selectedAppObjects = @()
    while ($true) {
        $userInput = Read-Host "Enter the numbers of the products to uninstall (e.g., 1,3,5), 'all' to select all, or 'none' to cancel"
        if ($userInput.ToLower() -eq 'none' -or -not $userInput.Trim()) {
            Write-Host "Uninstallation cancelled by user." -ForegroundColor Yellow
            return @()
        }

        if ($userInput.ToLower() -eq 'all') {
            $selectedAppObjects = $autodeskApps
            break
        }

        $indices = $userInput -split ',' | ForEach-Object { $_.Trim() }
        $validSelection = $true
        $tempSelectedObjects = @()

        foreach ($indexStr in $indices) {
            if ($indexStr -match '^\d+$') {
                $idx = [int]$indexStr - 1
                if ($idx -ge 0 -and $idx -lt $autodeskApps.Count) {
                    $tempSelectedObjects += $autodeskApps[$idx]
                } else {
                    Write-Host "Error: Selection '$($indexStr)' is out of range (1 to $($autodeskApps.Count))." -ForegroundColor Red
                    $validSelection = $false
                    break 
                }
            } else {
                Write-Host "Error: Invalid input '$indexStr'. Please enter numbers, 'all', or 'none'." -ForegroundColor Red
                $validSelection = $false
                break
            }
        }
        
        if ($validSelection) {
            if ($tempSelectedObjects.Count -gt 0) {
                $selectedAppObjects = $tempSelectedObjects | Sort-Object -Property PSChildName -Unique
                break
            } else {
                 Write-Host "No products selected with the provided numbers. Please try again." -ForegroundColor Yellow
            }
        }
    }

    if ($selectedAppObjects.Count -eq 0) {
        Write-Host "No products selected for uninstallation." -ForegroundColor Yellow
        return @()
    }

    Write-Host "`nYou have selected the following products for uninstallation:" -ForegroundColor Cyan
    $selectedAppObjects | ForEach-Object { Write-Host "- $($_.DisplayName)" -ForegroundColor Cyan }
    
    $confirmation = Read-Host "Are you sure you want to attempt to uninstall these $($selectedAppObjects.Count) products? (yes/no)"
    if ($confirmation.ToLower() -ne 'yes') {
        Write-Host "Uninstallation cancelled by user." -ForegroundColor Yellow
        return @()
    }
    
    return $selectedAppObjects | Select-Object -ExpandProperty PSChildName
}

function Uninstall-AutodeskProductsByPSChildName {
    param(
        [Parameter(Mandatory=$true)]
        [string[]]$TargetPSChildNames
    )

    Clear-Host
    if ($TargetPSChildNames.Count -eq 0) {
        Write-Host "No target products specified for uninstallation in this pass." -ForegroundColor Yellow
        return
    }

    $currentAppsRaw = @()
    $currentAppsRaw = Get-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\*" -ErrorAction SilentlyContinue
    $currentAppsRaw += Get-ItemProperty -Path "HKLM:\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\*" -ErrorAction SilentlyContinue
    
    $currentAutodeskApps = $currentAppsRaw | Where-Object {
        $_.DisplayName -like "*Autodesk*" -or 
        $_.Publisher -like "*Autodesk*" -or 
        $_.DisplayName -like "*AutoCAD*" -or 
        $_.DisplayName -like "*Revit*"
    } | Select-Object DisplayName, Publisher, PSChildName, UninstallString -Unique

    $appsToUninstallThisPass = $currentAutodeskApps | Where-Object { $TargetPSChildNames -contains $_.PSChildName }

    if ($appsToUninstallThisPass.Count -eq 0) {
        Write-Host "All selected Autodesk products appear to be uninstalled, or were not found in this pass." -ForegroundColor Green
        return
    }

    Write-Host "Found $($appsToUninstallThisPass.Count) selected Autodesk products to attempt uninstalling in this pass:" -ForegroundColor Yellow
    
    $apps = $appsToUninstallThisPass

    foreach ($app in $apps) {
        # Uninstall Autodesk Access
        if ($app.DisplayName -match "Autodesk Access"){
            Write-Host "Uninstalling $($app.DisplayName)..." -ForegroundColor Yellow
            Start-Process -FilePath "C:\Program Files\Autodesk\AdODIS\V1\Installer.exe" -ArgumentList "-q -i uninstall --trigger_point system -m C:\ProgramData\Autodesk\ODIS\metadata\{A3158B3E-5F28-358A-BF1A-9532D8EBC811}\pkg.access.xml -x `"C:\Program Files\Autodesk\AdODIS\V1\SetupRes\manifest.xsd`" --manifest_type package" -NoNewWindow -Wait
        }
        # Uninstall Autodesk Identity Manager
        elseif ($app.DisplayName -match "Autodesk Identity Manager"){
            Write-Host "Uninstalling $($app.DisplayName)..." -ForegroundColor Yellow
            Start-Process -FilePath "C:\Program Files\Autodesk\AdskIdentityManager\uninstall.exe" -ArgumentList "--mode unattended" -NoNewWindow -Wait
        }
        # Uninstall Autodesk Genuine Service
        elseif ($app.DisplayName -match "Autodesk Genuine Service"){
            Write-Host "Uninstalling $($app.DisplayName)..." -ForegroundColor Yellow
            Remove-Item "$Env:ALLUSERSPROFILE\Autodesk\Adlm\ProductInformation.pit" -Force -ErrorAction:SilentlyContinue
            Remove-Item "$Env:userprofile\AppData\Local\Autodesk\Genuine Autodesk Service\id.dat" -Force -ErrorAction:SilentlyContinue
            msiexec.exe /x "{21DE6405-91DE-4A69-A8FB-483847F702C6}" /qn /norestart
            Start-Sleep -Seconds 3
        }
        # Uninstall Carbon Insights for Revit
        elseif ($app.DisplayName -like "*Carbon Insights for Revit*"){
            Write-Host "Uninstalling $($app.DisplayName)..." -ForegroundColor Yellow
            Start-Process -FilePath "C:\Program Files\Autodesk\AdODIS\V1\Installer.exe" -ArgumentList "-q -i uninstall --trigger_point system -m C:\ProgramData\Autodesk\ODIS\metadata\{006E0C25-2C15-39A8-8590-AA5AD7D395D4}\pkg.RTCA.xml -x `"C:\Program Files\Autodesk\AdODIS\V1\SetupRes\manifest.xsd`" --manifest_type package" -NoNewWindow -Wait
        }
        # Generic ODIS Uninstaller (using bundleManifest.xml)
        elseif ($app.UninstallString -and $app.UninstallString -like "*installer.exe*") {
            $installerPath = "C:\Program Files\Autodesk\AdODIS\V1\Installer.exe" # Default ODIS installer
            # Attempt to parse installer path from UninstallString if it's different
            if ($app.UninstallString -match "^`"?(.*?installer.exe)`"?($|\s)") {
                $extractedPath = $Matches[1]
                if (Test-Path $extractedPath) {
                    $installerPath = $extractedPath
                }
            }
            
            $odisMetaDataPath = "C:\ProgramData\Autodesk\ODIS\metadata\$($app.PSChildName)"
            $bundleManifestPath = Join-Path $odisMetaDataPath "bundleManifest.xml"
            $setupResManifestPath = Join-Path $odisMetaDataPath "SetupRes\manifest.xsd"

            if ((Test-Path $bundleManifestPath) -and (Test-Path $setupResManifestPath)) {
                 Write-Host "Uninstalling $($app.DisplayName) using ODIS (bundle)..." -ForegroundColor Yellow
                 $argumentList = "-q -i uninstall --trigger_point system -m `"$bundleManifestPath`" -x `"$setupResManifestPath`""
                 Start-Process -FilePath $installerPath -ArgumentList $argumentList -NoNewWindow -Wait
                 Start-Sleep -Seconds 3
            } else {
                 Write-Host "Warning: ODIS bundle manifest not found for $($app.DisplayName). Trying generic MSIEXEC if applicable." -ForegroundColor Magenta
                 # Fall through to MSIEXEC if PSChildName is a GUID
                 if ($app.PSChildName -match '^{([0-9A-Fa-f]{8}-([0-9A-Fa-f]{4}-){3}[0-9A-Fa-f]{12})}$') {
                    Write-Host "Attempting to uninstall $($app.DisplayName) using msiexec (Product Code as fallback)..." -ForegroundColor Yellow
                    Start-Process -FilePath msiexec.exe -ArgumentList "/x `"$($app.PSChildName)`" /qn /norestart" -NoNewWindow -Wait
                    Start-Sleep -Seconds 3
                } else {
                    Write-Host "Warning: No ODIS bundle and PSChildName is not a GUID for $($app.DisplayName). Uninstallation might require manual steps." -ForegroundColor Red
                }
            }
        }
        # Generic MSI uninstallation (using product code)
        else {
            if ($app.PSChildName -match '^{([0-9A-Fa-f]{8}-([0-9A-Fa-f]{4}-){3}[0-9A-Fa-f]{12})}$') {
                Write-Host "Uninstalling $($app.DisplayName) using msiexec (Product Code)..." -ForegroundColor Yellow
                Start-Process -FilePath msiexec.exe -ArgumentList "/x `"$($app.PSChildName)`" /qn /norestart" -NoNewWindow -Wait
                Start-Sleep -Seconds 3
            } else {
                Write-Host "Warning: No clear uninstallation method found for $($app.DisplayName). PSChildName: $($app.PSChildName) (not a GUID), UninstallString: '$($app.UninstallString)' (not an installer.exe type)." -ForegroundColor Red
            }
        } 
    }
}

# --- Main script execution ---
Clear-Host
Write-Host "Autodesk Uninstaller - Selective Mode" -ForegroundColor Green
Write-Host "------------------------------------"

$selectedAppIdentifiers = Get-AutodeskProductSelection

if ($selectedAppIdentifiers -and $selectedAppIdentifiers.Count -gt 0) {
    Write-Host "`nStarting uninstallation process for selected products." -ForegroundColor Green
    Write-Host "The uninstaller will run multiple passes to handle dependencies." -ForegroundColor Yellow
    
    $passes = 3 
    for ($i = 1; $i -le $passes; $i++) {
        Write-Host "`n--- Running Uninstallation Pass $i of $passes ---" -ForegroundColor Cyan
        Uninstall-AutodeskProductsByPSChildName -TargetPSChildNames $selectedAppIdentifiers
        if ($i -lt $passes) {
            Write-Host "Waiting a few seconds before next pass..."
            Start-Sleep -Seconds 10 
        }
    }

    Write-Host "`n------------------------------------" -ForegroundColor Green
    Write-Host "Selective uninstallation process has completed for the chosen products." -ForegroundColor Green
    
    $deleteFolderChoice = Read-Host "Do you want to delete the C:\Autodesk folder (if it exists)? (yes/no)"
    if ($deleteFolderChoice.ToLower() -eq 'yes') {
       Write-Host "Attempting to delete C:\Autodesk folder..." -ForegroundColor Yellow
       if (Test-Path 'C:\Autodesk') {
           Remove-Item -Path 'C:\Autodesk' -Recurse -Force -ErrorAction SilentlyContinue
           if ($?) { Write-Host "C:\Autodesk folder deleted successfully." -ForegroundColor Green } 
           else { Write-Host "Failed to delete C:\Autodesk folder." -ForegroundColor Red }
       } else {
           Write-Host "C:\Autodesk folder doesn't exist or has already been deleted." -ForegroundColor Yellow
       }
    }
    
    $restartChoice = Read-Host "Do you want to restart the computer now? (yes/no)"
    if ($restartChoice.ToLower() -eq 'yes') {
        Write-Host "Restarting computer in 10 seconds..." -ForegroundColor Yellow
        Write-Host "Close this window to cancel the restart." -ForegroundColor Yellow
        Start-Sleep -Seconds 10
        Restart-Computer -Force
    } else {
        Write-Host "`nUninstallation completed without restart." -ForegroundColor Green
        Write-Host "It is recommended to restart your computer at your earliest convenience." -ForegroundColor Yellow
    }
} else {
    Write-Host "No products were selected for uninstallation. Exiting..." -ForegroundColor Yellow
}

Write-Host "`nPress any key to exit..." -ForegroundColor Cyan
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")