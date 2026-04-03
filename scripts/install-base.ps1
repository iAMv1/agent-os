# =============================================================================
# Agent OS Base Installation Script (PowerShell)
# Installs Agent OS to your home directory (~/.agent-os/)
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

function Ensure-Directory {
    param([string]$Path)
    if (-not (Test-Path $Path)) {
        New-Item -ItemType Directory -Path $Path -Force | Out-Null
    }
}

# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------

$AgentOsHome = Join-Path $env:USERPROFILE ".agent-os"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$SourceDir = Split-Path -Parent $ScriptDir

# -----------------------------------------------------------------------------
# Validation
# -----------------------------------------------------------------------------

function Validate-Source {
    if (-not (Test-Path (Join-Path $SourceDir "README.md"))) {
        Write-Error "Agent OS source not found at: $SourceDir"
        Write-Host ""
        Write-Host "Make sure you're running this script from the Agent OS directory."
        exit 1
    }
}

# -----------------------------------------------------------------------------
# Installation
# -----------------------------------------------------------------------------

function Create-BaseStructure {
    Write-Status "Creating Agent OS base structure at $AgentOsHome..."

    Ensure-Directory $AgentOsHome
    Ensure-Directory (Join-Path $AgentOsHome "cache")
    Ensure-Directory (Join-Path $AgentOsHome "mcp")
    Ensure-Directory (Join-Path $AgentOsHome "memory")
    Ensure-Directory (Join-Path $AgentOsHome "sessions")
    Ensure-Directory (Join-Path $AgentOsHome "standards")
    Ensure-Directory (Join-Path $AgentOsHome "skills")

    Write-Success "Created base directory structure"
}

function Copy-Skills {
    Write-Status "Copying skills..."

    $SkillsSource = Join-Path $SourceDir "skills"
    $SkillsDest = Join-Path $AgentOsHome "skills"

    if (Test-Path $SkillsSource) {
        # Copy custom skills
        $CustomSkills = @(
            "deep-research", "decision-framework", "knowledge-synthesis",
            "strategic-planning", "problem-decomposition", "quality-assurance",
            "communication-design", "learning-accelerator", "risk-assessment",
            "optimization-engine", "context-manager", "meta-cognition"
        )

        foreach ($skill in $CustomSkills) {
            $skillPath = Join-Path $SkillsSource $skill
            if (Test-Path $skillPath) {
                Copy-Item -Path $skillPath -Destination $SkillsDest -Recurse -Force
            }
        }

        $SkillCount = (Get-ChildItem -Path $SkillsDest -Directory).Count
        Write-Success "Copied $SkillCount skills"
    }
    else {
        Write-Warning "No skills directory found in source"
    }
}

function Copy-Engines {
    Write-Status "Copying workflow engines..."

    $EnginesSource = Join-Path $SourceDir "engines"
    $EnginesDest = Join-Path $AgentOsHome "engines"

    if (Test-Path $EnginesSource) {
        if (Test-Path $EnginesDest) {
            Remove-Item -Path $EnginesDest -Recurse -Force
        }
        Copy-Item -Path $EnginesSource -Destination $EnginesDest -Recurse
        Write-Success "Copied workflow engines"
    }
    else {
        Write-Warning "No engines directory found in source"
    }
}

function Copy-Commands {
    Write-Status "Copying commands..."

    $CommandsSource = Join-Path $SourceDir "commands" "agent-os"
    $CommandsDest = Join-Path $AgentOsHome "commands" "agent-os"

    if (Test-Path $CommandsSource) {
        if (Test-Path (Join-Path $AgentOsHome "commands")) {
            Remove-Item -Path (Join-Path $AgentOsHome "commands") -Recurse -Force
        }
        Copy-Item -Path $CommandsSource -Destination $CommandsDest -Recurse
        $CmdCount = (Get-ChildItem -Path $CommandsDest -Filter "*.md" -File).Count
        Write-Success "Copied $CmdCount commands"
    }
    else {
        Write-Warning "No commands directory found in source (optional)"
    }
}

function Copy-Profiles {
    Write-Status "Copying profiles..."

    $ProfilesSource = Join-Path $SourceDir "profiles"
    $ProfilesDest = Join-Path $AgentOsHome "profiles"

    if (Test-Path $ProfilesSource) {
        if (Test-Path $ProfilesDest) {
            Remove-Item -Path $ProfilesDest -Recurse -Force
        }
        Copy-Item -Path $ProfilesSource -Destination $ProfilesDest -Recurse
        $ProfileCount = (Get-ChildItem -Path $ProfilesDest -Directory).Count
        $StandardCount = (Get-ChildItem -Path $ProfilesDest -Filter "*.md" -Recurse -File).Count
        Write-Success "Copied $ProfileCount profiles with $StandardCount standards"
    }
    else {
        Write-Warning "No profiles directory found in source"
    }
}

function Create-Config {
    Write-Status "Creating configuration..."

    $ConfigFile = Join-Path $AgentOsHome "config.yml"

    if (-not (Test-Path $ConfigFile)) {
        $ConfigContent = @"
# Agent OS Configuration
# See docs/CONCEPTS.md for profile documentation

default_profile: default

profiles:
  default:
    description: "Default profile for general development"
    inherits: []
    standards:
      - coding-standards
      - git-workflow
      - testing-standards
"@
        Set-Content -Path $ConfigFile -Value $ConfigContent -Encoding UTF8
        Write-Success "Created config.yml"
    }
    else {
        Write-Warning "config.yml already exists, skipping"
    }
}

function Create-SessionMemory {
    Write-Status "Creating session memory template..."

    $MemoryDir = Join-Path $AgentOsHome "memory"
    $MemoryFile = Join-Path $MemoryDir "session-memory.md"

    if (-not (Test-Path $MemoryFile)) {
        $MemoryContent = @"
# Session Memory

## Session Title
[New Session]

## Current State
[Session started]

## Task Specification
[Waiting for task]

## Files and Functions
[None yet]

## Workflow
[Not started]

## Errors & Corrections
[None]

## Codebase and System Documentation
[None]

## Learnings
[None]

## Key Results
[None]

## Worklog
[Session started]
"@
        Set-Content -Path $MemoryFile -Value $MemoryContent -Encoding UTF8
        Write-Success "Created session memory template"
    }
    else {
        Write-Warning "Session memory already exists, skipping"
    }
}

# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------

function Main {
    Write-Host ""
    Write-Host "=============================================" -ForegroundColor Blue
    Write-Host "   Agent OS Base Installation" -ForegroundColor Blue
    Write-Host "=============================================" -ForegroundColor Blue
    Write-Host ""

    Validate-Source

    Create-BaseStructure
    Copy-Skills
    Copy-Engines
    Copy-Commands
    Copy-Profiles
    Create-Config
    Create-SessionMemory

    Write-Host ""
    Write-Success "Agent OS base installed successfully at $AgentOsHome"
    Write-Host ""
    Write-Host "Next steps:"
    Write-Host "  1. Navigate to your project directory"
    Write-Host "  2. Run: .\.agent-os\scripts\project-install.ps1"
    Write-Host ""
    Write-Host "See docs/INSTALLATION.md for full documentation."
    Write-Host ""
}

# Run main
Main
