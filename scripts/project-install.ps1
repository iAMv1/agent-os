# =============================================================================
# Agent OS Project Installation Script (PowerShell)
# Installs Agent OS into a project's codebase
# =============================================================================

#Requires -Version 5.1

# -----------------------------------------------------------------------------
# Helper Functions
# -----------------------------------------------------------------------------

function Write-Status {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Blue
}

function Write-Success {
    param([string]$Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

function Write-Section {
    param([string]$Title)
    Write-Host ""
    Write-Host "=============================================" -ForegroundColor Blue
    Write-Host "   $Title" -ForegroundColor Blue
    Write-Host "=============================================" -ForegroundColor Blue
    Write-Host ""
}

function Ensure-Directory {
    param([string]$Path)
    if (-not (Test-Path $Path)) {
        New-Item -ItemType Directory -Path $Path -Force | Out-Null
    }
}

# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$BaseDir = Split-Path -Parent $ScriptDir
$ProjectDir = Get-Location

# -----------------------------------------------------------------------------
# Default Values
# -----------------------------------------------------------------------------

$Verbose = $false
$Profile = ""
$CommandsOnly = $false

# -----------------------------------------------------------------------------
# Help Function
# -----------------------------------------------------------------------------

function Show-Help {
    Write-Host @"

Usage: $($MyInvocation.MyCommand.Name) [OPTIONS]

Install Agent OS into the current project directory.

Options:
    --profile <name>     Use specified profile (default: from config.yml)
    --commands-only      Only update commands, preserve existing standards
    --verbose            Show detailed output
    -h, --help           Show this help message

Examples:
    $($MyInvocation.MyCommand.Name)
    $($MyInvocation.MyCommand.Name) --profile default
    $($MyInvocation.MyCommand.Name) --commands-only

"@
    exit 0
}

# -----------------------------------------------------------------------------
# Parse Arguments
# -----------------------------------------------------------------------------

function Parse-Arguments {
    $args = @($args)
    for ($i = 0; $i -lt $args.Count; $i++) {
        switch ($args[$i]) {
            "--profile" {
                $script:Profile = $args[$i + 1]
                $i++
            }
            "--commands-only" {
                $script:CommandsOnly = $true
            }
            "--verbose" {
                $script:Verbose = $true
            }
            "-h" { Show-Help }
            "--help" { Show-Help }
            default {
                Write-Error "Unknown option: $($args[$i])"
                Show-Help
            }
        }
    }
}

# -----------------------------------------------------------------------------
# Validation
# -----------------------------------------------------------------------------

function Validate-BaseInstallation {
    if (-not (Test-Path $BaseDir)) {
        Write-Error "Agent OS base installation not found"
        Write-Host ""
        Write-Host "Run the base installation first:"
        Write-Host "  .\.agent-os\scripts\install-base.ps1"
        exit 1
    }

    if (-not (Test-Path (Join-Path $BaseDir "config.yml"))) {
        Write-Error "Base installation config.yml not found"
        exit 1
    }
}

function Validate-NotInBase {
    if ($ProjectDir.Path -eq $BaseDir) {
        Write-Error "Cannot install Agent OS in the base installation directory"
        Write-Host ""
        Write-Host "Navigate to your project directory first:"
        Write-Host "  cd \path\to\your\project"
        Write-Host ""
        exit 1
    }
}

# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------

function Load-Configuration {
    $ConfigFile = Join-Path $BaseDir "config.yml"
    $DefaultProfile = "default"

    if (Test-Path $ConfigFile) {
        $Content = Get-Content $ConfigFile -Raw
        if ($Content -match "default_profile:\s*(\S+)") {
            $DefaultProfile = $Matches[1]
        }
    }

    $EffectiveProfile = if ($Profile) { $Profile } else { $DefaultProfile }

    # Validate profile exists
    $ProfilePath = Join-Path $BaseDir "profiles\$EffectiveProfile"
    if (-not (Test-Path $ProfilePath)) {
        Write-Warning "Profile not found: $EffectiveProfile (using default)"
        $EffectiveProfile = "default"
    }

    if ($Verbose) {
        Write-Host "[VERBOSE] Using profile: $EffectiveProfile"
    }

    return $EffectiveProfile
}

# -----------------------------------------------------------------------------
# Confirmation
# -----------------------------------------------------------------------------

function Confirm-StandardsOverwrite {
    if ($CommandsOnly) { return }

    $ExistingStandards = Join-Path $ProjectDir "agent-os\standards"

    if (Test-Path $ExistingStandards) {
        Write-Host ""
        Write-Warning "Existing standards folder detected at: $ExistingStandards"
        Write-Host ""
        Write-Host "This will overwrite your existing standards."
        Write-Host ""
        $Response = Read-Host "Do you want to continue? (y/N)"
        if ($Response -notmatch "^[Yy]$") {
            Write-Host ""
            Write-Host "Installation cancelled."
            Write-Host ""
            Write-Host "To update only commands without touching standards, use:"
            Write-Host "  $($MyInvocation.MyCommand.Name) --commands-only"
            Write-Host ""
            exit 0
        }
    }
}

# -----------------------------------------------------------------------------
# Installation Functions
# -----------------------------------------------------------------------------

function Create-ProjectStructure {
    Write-Status "Creating project structure..."

    Ensure-Directory (Join-Path $ProjectDir "agent-os")
    Ensure-Directory (Join-Path $ProjectDir "agent-os\standards")
    Ensure-Directory (Join-Path $ProjectDir ".agent-os")
    Ensure-Directory (Join-Path $ProjectDir ".agent-os\memory")
    Ensure-Directory (Join-Path $ProjectDir ".agent-os\sessions")
    Ensure-Directory (Join-Path $ProjectDir ".agent-os\cache")

    Write-Success "Created agent-os/ directory structure"
}

function Install-Standards {
    if ($CommandsOnly) {
        Write-Status "Skipping standards (--commands-only)"
        return
    }

    Write-Host ""
    Write-Status "Installing standards..."

    $ProfileStandards = Join-Path $BaseDir "profiles\$EffectiveProfile\standards"
    $ProjectStandards = Join-Path $ProjectDir "agent-os\standards"
    $FileCount = 0

    if (Test-Path $ProfileStandards) {
        $Files = Get-ChildItem -Path $ProfileStandards -Filter "*.md" -Recurse -File
        foreach ($File in $Files) {
            $RelativePath = $File.FullName.Substring($ProfileStandards.Length + 1)
            $DestFile = Join-Path $ProjectStandards $RelativePath
            Ensure-Directory (Split-Path $DestFile -Parent)
            Copy-Item -Path $File.FullName -Destination $DestFile -Force
            $FileCount++
        }
    }

    # Copy base standards if profile doesn't have any
    if ($FileCount -eq 0) {
        $BaseStandards = Join-Path $BaseDir "standards"
        if (Test-Path $BaseStandards) {
            $Files = Get-ChildItem -Path $BaseStandards -Filter "*.md" -Recurse -File
            foreach ($File in $Files) {
                $RelativePath = $File.FullName.Substring($BaseStandards.Length + 1)
                $DestFile = Join-Path $ProjectStandards $RelativePath
                Ensure-Directory (Split-Path $DestFile -Parent)
                Copy-Item -Path $File.FullName -Destination $DestFile -Force
                $FileCount++
            }
        }
    }

    if ($FileCount -gt 0) {
        Write-Success "Installed $FileCount standards files"
    }
    else {
        Write-Success "No standards to install (profile is empty)"
    }
}

function Create-Index {
    Write-Host ""
    Write-Status "Updating standards index..."

    $StandardsDir = Join-Path $ProjectDir "agent-os\standards"
    $IndexFile = Join-Path $StandardsDir "index.yml"

    $IndexContent = "# Agent OS Standards Index`n`n"
    $EntryCount = 0

    # Handle root-level .md files
    $RootFiles = Get-ChildItem -Path $StandardsDir -Filter "*.md" -File | Sort-Object Name
    if ($RootFiles) {
        $IndexContent += "root:`n"
        foreach ($File in $RootFiles) {
            $Filename = $File.BaseName
            $IndexContent += "  $Filename:`n"
            $IndexContent += "    description: Needs description`n"
            $EntryCount++
        }
        $IndexContent += "`n"
    }

    # Handle files in subfolders
    $Folders = Get-ChildItem -Path $StandardsDir -Directory | Sort-Object Name
    foreach ($Folder in $Folders) {
        $MdFiles = Get-ChildItem -Path $Folder.FullName -Filter "*.md" -File | Sort-Object Name
        if ($MdFiles) {
            $IndexContent += "$($Folder.Name):`n"
            foreach ($File in $MdFiles) {
                $Filename = $File.BaseName
                $IndexContent += "  $Filename:`n"
                $IndexContent += "    description: Needs description`n"
                $EntryCount++
            }
            $IndexContent += "`n"
        }
    }

    Set-Content -Path $IndexFile -Value $IndexContent -Encoding UTF8

    if ($EntryCount -gt 0) {
        Write-Success "Created index.yml ($EntryCount entries)"
    }
    else {
        Write-Success "Created index.yml (no standards to index)"
    }
}

function Install-Commands {
    Write-Host ""
    Write-Status "Installing commands..."

    $CommandsSource = Join-Path $BaseDir "commands\agent-os"
    $CommandsDest = Join-Path $ProjectDir ".claude\commands\agent-os"

    if (-not (Test-Path $CommandsSource)) {
        Write-Warning "No commands found in base installation"
        return
    }

    Ensure-Directory $CommandsDest

    $Count = 0
    $Files = Get-ChildItem -Path $CommandsSource -Filter "*.md" -File
    foreach ($File in $Files) {
        Copy-Item -Path $File.FullName -Destination $CommandsDest -Force
        $Count++
    }

    if ($Count -gt 0) {
        Write-Success "Installed $Count commands to .claude/commands/agent-os/"
    }
    else {
        Write-Warning "No command files found"
    }
}

function Copy-WorkerMd {
    Write-Host ""
    Write-Status "Installing project instructions..."

    $WorkerSource = Join-Path $BaseDir "WORKER.md"
    $WorkerDest = Join-Path $ProjectDir "WORKER.md"

    if (Test-Path $WorkerSource) {
        if (-not (Test-Path $WorkerDest)) {
            Copy-Item -Path $WorkerSource -Destination $WorkerDest -Force
            Write-Success "Copied WORKER.md to project root"
        }
        else {
            Write-Warning "WORKER.md already exists in project, skipping"
        }
    }
}

# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------

function Main {
    Write-Section "Agent OS Project Installation"

    Parse-Arguments @args

    Validate-NotInBase
    Validate-BaseInstallation

    $script:EffectiveProfile = Load-Configuration

    Write-Host ""
    Write-Status "Configuration:"
    Write-Host "  Profile: $EffectiveProfile"
    Write-Host "  Commands only: $CommandsOnly"

    Confirm-StandardsOverwrite

    Write-Host ""

    Create-ProjectStructure
    Install-Standards
    Create-Index
    Install-Commands
    Copy-WorkerMd

    Write-Host ""
    Write-Success "Agent OS installed successfully!"
    Write-Host ""
    Write-Host "Next steps:"
    Write-Host "  1. Run /discover-standards to extract patterns from your codebase"
    Write-Host "  2. Run /inject-standards to inject standards into your context"
    Write-Host "  3. Start building with AgentOS!"
    Write-Host ""
}

# Run main
Main @args
