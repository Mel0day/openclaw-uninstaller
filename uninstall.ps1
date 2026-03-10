#Requires -RunAsAdministrator
# OpenClaw Complete Uninstaller for Windows
# https://github.com/Mel0day/openclaw-uninstaller

$ErrorActionPreference = "Continue"
$host.UI.RawUI.WindowTitle = "OpenClaw Uninstaller"

function Write-Step { param($msg) Write-Host "`n[*] $msg" -ForegroundColor Cyan }
function Write-OK   { param($msg) Write-Host "    [OK] $msg" -ForegroundColor Green }
function Write-Warn { param($msg) Write-Host "    [!] $msg" -ForegroundColor Yellow }

Write-Host "==========================================" -ForegroundColor Red
Write-Host "       OpenClaw Complete Uninstaller      " -ForegroundColor Red
Write-Host "==========================================" -ForegroundColor Red
Write-Host ""

# Step 1: Try official uninstall command
Write-Step "Step 1/8 - Running official uninstall command..."
if (Get-Command openclaw -ErrorAction SilentlyContinue) {
    try {
        & openclaw uninstall --all --yes 2>&1 | Out-Null
        Write-OK "Official uninstall completed"
    } catch {
        Write-Warn "Official uninstall failed, continuing manually"
    }
} else {
    Write-Warn "openclaw command not found, skipping"
}

# Step 2: Kill processes
Write-Step "Step 2/8 - Terminating OpenClaw processes..."
@("openclaw", "openclaw_agent", "openclaw_updater") | ForEach-Object {
    if (Get-Process -Name $_ -ErrorAction SilentlyContinue) {
        Stop-Process -Name $_ -Force -ErrorAction SilentlyContinue
        Write-OK "Killed: $_"
    }
}

# Step 3: Stop and delete Windows service
Write-Step "Step 3/8 - Removing Windows service..."
if (Get-Service -Name "OpenClawService" -ErrorAction SilentlyContinue) {
    Stop-Service -Name "OpenClawService" -Force -ErrorAction SilentlyContinue
    sc.exe delete OpenClawService | Out-Null
    Write-OK "Service removed"
} else {
    Write-Warn "Service not found"
}

# Step 4: Remove scheduled tasks
Write-Step "Step 4/8 - Removing scheduled tasks..."
@("OpenClaw Gateway", "OpenClaw.UpdateScheduler") | ForEach-Object {
    if (Get-ScheduledTask -TaskName $_ -ErrorAction SilentlyContinue) {
        Unregister-ScheduledTask -TaskName $_ -Confirm:$false
        Write-OK "Removed task: $_"
    }
}

# Step 5: Uninstall npm package
Write-Step "Step 5/8 - Removing npm package..."
if (Get-Command npm -ErrorAction SilentlyContinue) {
    npm uninstall -g openclaw 2>&1 | Out-Null
    Write-OK "npm package removed"
} else {
    Write-Warn "npm not found, skipping"
}

# Step 6: Delete residual files and directories
Write-Step "Step 6/8 - Deleting residual files..."
@(
    "$env:USERPROFILE\.openclaw",
    "$env:USERPROFILE\.clawdbot",
    "$env:APPDATA\OpenClaw",
    "$env:LOCALAPPDATA\OpenClaw"
) | ForEach-Object {
    if (Test-Path $_) {
        Remove-Item -Recurse -Force $_ -ErrorAction SilentlyContinue
        Write-OK "Deleted: $_"
    }
}

# Step 7: Clean registry
Write-Step "Step 7/8 - Cleaning registry..."
@("HKLM:\SOFTWARE\OpenClaw", "HKCU:\Software\OpenClaw") | ForEach-Object {
    if (Test-Path $_) {
        Remove-Item -Recurse -Force $_ -ErrorAction SilentlyContinue
        Write-OK "Removed registry key: $_"
    }
}

# Step 8: Verify port 18789 is closed
Write-Step "Step 8/8 - Checking port 18789..."
$portInUse = netstat -ano | Select-String ":18789"
if ($portInUse) {
    Write-Warn "Port 18789 still in use! Manual check needed:"
    Write-Host $portInUse -ForegroundColor Yellow
} else {
    Write-OK "Port 18789 is closed"
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Green
Write-Host "         Uninstall complete!              " -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""
Write-Host "IMPORTANT: Manually revoke OAuth tokens:" -ForegroundColor Yellow
Write-Host "  Google    -> https://myaccount.google.com/permissions" -ForegroundColor Yellow
Write-Host "  Microsoft -> https://account.live.com/consent/Manage" -ForegroundColor Yellow
Write-Host "  Also revoke API keys in your AI provider dashboard." -ForegroundColor Yellow
Write-Host ""
Read-Host "Press Enter to exit"
