# =============================================================================
# Agent OS Uninstall Script (PowerShell)
# Removes Agent OS from your home directory and/or project
# =============================================================================

#Requires -Version 5.1

function Write-Status { param([string]$Message); Write-Host "[INFO] $Message" -ForegroundColor Blue }
function Write-Success { param([string]$Message); Write-Host "[SUCCESS] $Message" -ForegroundColor Green }
function Write-Warning { param([string]$Message); Write-Host "[WARNING] $Message" -ForegroundColor Yellow }
function Write-Error { param([string]$Message); Write-Host "[ERROR] $Message" -ForegroundColor Red }

$AgentOsHome = Join-Path $env:USERPROFILE ".agent-os"
$ProjectDir = Get-Location

$RemoveBase = $false
$RemoveProject = $false
$DryRun = $false

function Show-Help {
    Write-Host @"

Usage: $($MyInvocation.MyCommand.Name) [OPTIONS]

Uninstall Agent OS from your system.

Options:
    --base               Remove base installation (~/.agent-os/)
    --project            Remove project installation (agent-os/, .agent-os/)
    --all                Remove both base and project installations
    --dry-run            Show what would be removed without removing
    -h, --help           Show this help message

Examples:
    $($MyInvocation.MyCommand.Name) --base
    $($MyInvocation.MyCommand.Name) --project
    $($MyInvocation.MyCommand.Name) --all
    $($MyInvocation.MyCommand.Name) --all --dry-run

"@
    exit 0
}

function Parse-Arguments {
    $args = @($args)
    for ($i = 0; $i -lt $args.Count; $i++) {
        switch ($args[$i]) {
            "--base" { $script:RemoveBase = $true }
            "--project" { $script:RemoveProject = $true }
            "--all" { $script:RemoveBase = $true; $script:RemoveProject = $true }
            "--dry-run" { $script:DryRun = $true }
            "-h" { Show-Help }
            "--help" { Show-Help }
            default { Write-Error "Unknown option: $($args[$i])"; Show-Help }
        }
    }
}

function Remove-Base {
    if ($DryRun) {
        Write-Status "Would remove: $AgentOsHome"
        return
    }
    if (Test-Path $AgentOsHome) {
        Write-Status "Removing base installation at $AgentOsHome..."
        Remove-Item -Path $AgentOsHome -Recurse -Force
        Write-Success "Removed base installation"
    }
    else {
        Write-Warning "Base installation not found at $AgentOsHome"
    }
}

function Remove-Project {
    if ($DryRun) {
        Write-Status "Would remove: $(Join-Path $ProjectDir 'agent-os')"
        Write-Status "Would remove: $(Join-Path $ProjectDir '.agent-os')"
        Write-Status "Would remove: $(Join-Path $ProjectDir '.claude\commands\agent-os')"
        return
    }

    $AgentOsDir = Join-Path $ProjectDir "agent-os"
    if (Test-Path $AgentOsDir) {
        Write-Status "Removing project installation at $AgentOsDir"
        Remove-Item -Path $AgentOsDir -Recurse -Force
        Write-Success "Removed agent-os/"
    }

    $DotAgentOsDir = Join-Path $ProjectDir ".agent-os"
    if (Test-Path $DotAgentOsDir) {
        Write-Status "Removing runtime data at $DotAgentOsDir"
        Remove-Item -Path $DotAgentOsDir -Recurse -Force
        Write-Success "Removed .agent-os/"
    }

    $CommandsDir = Join-Path $ProjectDir ".claude\commands\agent-os"
    if (Test-Path $CommandsDir) {
        Write-Status "Removing commands at $CommandsDir"
        Remove-Item -Path $CommandsDir -Recurse -Force
        Write-Success "Removed .claude/commands/agent-os/"
    }

    $WorkerMd = Join-Path $ProjectDir "WORKER.md"
    if (Test-Path $WorkerMd) {
        Write-Status "Removing WORKER.md..."
        Remove-Item -Path $WorkerMd -Force
        Write-Success "Removed WORKER.md"
    }
}

function Main {
    Write-Host ""
    Write-Host "=============================================" -ForegroundColor Blue
    Write-Host "   Agent OS Uninstall" -ForegroundColor Blue
    Write-Host "=============================================" -ForegroundColor Blue
    Write-Host ""

    Parse-Arguments @args

    if (-not $RemoveBase -and -not $RemoveProject) {
        Write-Error "No removal target specified. Use --base, --project, or --all."
        Show-Help
    }

    if ($DryRun) {
        Write-Status "DRY RUN - No files will be removed"
        Write-Host ""
    }

    if ($RemoveBase) { Remove-Base }
    if ($RemoveProject) { Remove-Project }

    Write-Host ""
    if ($DryRun) {
        Write-Status "Dry run complete. Remove --dry-run to actually delete files."
    }
    else {
        Write-Success "Uninstall complete!"
    }
    Write-Host ""
}

Main @args
