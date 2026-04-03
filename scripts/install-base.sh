#!/bin/bash

# =============================================================================
# Agent OS Base Installation Script
# Installs Agent OS to your home directory (~/.agent-os/)
# =============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# -----------------------------------------------------------------------------
# Helper Functions
# -----------------------------------------------------------------------------

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

ensure_dir() {
    if [[ ! -d "$1" ]]; then
        mkdir -p "$1"
    fi
}

# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------

AGENT_OS_HOME="$HOME/.agent-os"
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
SOURCE_DIR="$(dirname "$SCRIPT_DIR")"

# -----------------------------------------------------------------------------
# Help Function
# -----------------------------------------------------------------------------

show_help() {
    cat << EOF
Usage: $0 [OPTIONS]

Install Agent OS base to your home directory (~/.agent-os/).

Options:
    --verbose            Show detailed output
    -h, --help           Show this help message

Examples:
    $0
    $0 --verbose

EOF
    exit 0
}

# -----------------------------------------------------------------------------
# Parse Arguments
# -----------------------------------------------------------------------------

VERBOSE="false"

parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --verbose)
                VERBOSE="true"
                shift
                ;;
            -h|--help)
                show_help
                ;;
            *)
                print_error "Unknown option: $1"
                show_help
                ;;
        esac
    done
}

# -----------------------------------------------------------------------------
# Validation
# -----------------------------------------------------------------------------

validate_source() {
    if [[ ! -f "$SOURCE_DIR/README.md" ]]; then
        print_error "Agent OS source not found at: $SOURCE_DIR"
        echo ""
        echo "Make sure you're running this script from the Agent OS directory."
        exit 1
    fi
}

# -----------------------------------------------------------------------------
# Installation
# -----------------------------------------------------------------------------

create_base_structure() {
    print_status "Creating Agent OS base structure at $AGENT_OS_HOME..."

    ensure_dir "$AGENT_OS_HOME"
    ensure_dir "$AGENT_OS_HOME/cache"
    ensure_dir "$AGENT_OS_HOME/mcp"
    ensure_dir "$AGENT_OS_HOME/memory"
    ensure_dir "$AGENT_OS_HOME/sessions"
    ensure_dir "$AGENT_OS_HOME/standards"
    ensure_dir "$AGENT_OS_HOME/skills"

    print_success "Created base directory structure"
}

copy_skills() {
    print_status "Copying skills..."

    local skills_source="$SOURCE_DIR/skills"
    local skills_dest="$AGENT_OS_HOME/skills"

    if [[ -d "$skills_source" ]]; then
        # Copy all skill directories that have a SKILL.md file
        for skill_dir in "$skills_source"/*/; do
            if [[ -d "$skill_dir" ]] && [[ -f "$skill_dir/SKILL.md" ]]; then
                local skill_name=$(basename "$skill_dir")
                cp -r "$skill_dir" "$skills_dest/"
            fi
        done

        local skill_count=$(find "$skills_dest" -maxdepth 1 -mindepth 1 -type d 2>/dev/null | wc -l)
        print_success "Copied $skill_count skills"
    else
        print_warning "No skills directory found in source"
    fi
}

copy_engines() {
    print_status "Copying workflow engines..."

    local engines_source="$SOURCE_DIR/engines"
    local engines_dest="$AGENT_OS_HOME/engines"

    if [[ -d "$engines_source" ]]; then
        rm -rf "$engines_dest"
        cp -r "$engines_source" "$engines_dest"
        print_success "Copied workflow engines"
    else
        print_warning "No engines directory found in source"
    fi
}

copy_commands() {
    print_status "Copying commands..."

    local commands_source="$SOURCE_DIR/commands/agent-os"
    local commands_dest="$AGENT_OS_HOME/commands/agent-os"

    if [[ -d "$commands_source" ]]; then
        rm -rf "$commands_dest"
        cp -r "$commands_source" "$commands_dest"
        local cmd_count=$(find "$commands_dest" -name "*.md" -type f 2>/dev/null | wc -l)
        print_success "Copied $cmd_count commands"
    else
        print_warning "No commands directory found in source (optional)"
    fi
}

copy_profiles() {
    print_status "Copying profiles..."

    local profiles_source="$SOURCE_DIR/profiles"
    local profiles_dest="$AGENT_OS_HOME/profiles"

    if [[ -d "$profiles_source" ]]; then
        rm -rf "$profiles_dest"
        cp -r "$profiles_source" "$profiles_dest"
        local profile_count=$(find "$profiles_dest" -maxdepth 1 -mindepth 1 -type d 2>/dev/null | wc -l)
        local standard_count=$(find "$profiles_dest" -name "*.md" -type f 2>/dev/null | wc -l)
        print_success "Copied $profile_count profiles with $standard_count standards"
    else
        print_warning "No profiles directory found in source"
    fi
}

create_config() {
    print_status "Creating configuration..."

    local config_file="$AGENT_OS_HOME/config.yml"

    if [[ ! -f "$config_file" ]]; then
        cat > "$config_file" << 'CONFIGEOF'
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
CONFIGEOF

        print_success "Created config.yml"
    else
        print_warning "config.yml already exists, skipping"
    fi
}

create_session_memory() {
    print_status "Creating session memory template..."

    local memory_file="$AGENT_OS_HOME/memory/session-memory.md"

    if [[ ! -f "$memory_file" ]]; then
        cat > "$memory_file" << 'MEMEOF'
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
MEMEOF

        print_success "Created session memory template"
    else
        print_warning "Session memory already exists, skipping"
    fi
}

# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------

main() {
    echo ""
    echo -e "${BLUE}=============================================${NC}"
    echo -e "${BLUE}   Agent OS Base Installation${NC}"
    echo -e "${BLUE}=============================================${NC}"
    echo ""

    parse_arguments "$@"

    validate_source

    create_base_structure
    copy_skills
    copy_engines
    copy_commands
    copy_profiles
    create_config
    create_session_memory

    echo ""
    print_success "Agent OS base installed successfully at $AGENT_OS_HOME"
    echo ""
    echo "Next steps:"
    echo "  1. Navigate to your project directory"
    echo "  2. Run: ~/.agent-os/scripts/project-install.sh"
    echo ""
    echo "See docs/INSTALLATION.md for full documentation."
    echo ""
}

# Run main
main "$@"
