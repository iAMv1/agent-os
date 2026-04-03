#!/bin/bash

# =============================================================================
# Agent OS Uninstall Script
# Removes Agent OS from your home directory and/or project
# =============================================================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

AGENT_OS_HOME="$HOME/.agent-os"
PROJECT_DIR="$(pwd)"

print_status() { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }

show_help() {
    cat << EOF
Usage: $0 [OPTIONS]

Uninstall Agent OS from your system.

Options:
    --base               Remove base installation (~/.agent-os/)
    --project            Remove project installation (agent-os/, .agent-os/)
    --all                Remove both base and project installations
    --dry-run            Show what would be removed without removing
    -h, --help           Show this help message

Examples:
    $0 --base
    $0 --project
    $0 --all
    $0 --all --dry-run

EOF
    exit 0
}

REMOVE_BASE="false"
REMOVE_PROJECT="false"
DRY_RUN="false"

parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --base)
                REMOVE_BASE="true"
                shift
                ;;
            --project)
                REMOVE_PROJECT="true"
                shift
                ;;
            --all)
                REMOVE_BASE="true"
                REMOVE_PROJECT="true"
                shift
                ;;
            --dry-run)
                DRY_RUN="true"
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

remove_base() {
    if [[ "$DRY_RUN" == "true" ]]; then
        print_status "Would remove: $AGENT_OS_HOME"
        return
    fi

    if [[ -d "$AGENT_OS_HOME" ]]; then
        print_status "Removing base installation at $AGENT_OS_HOME..."
        rm -rf "$AGENT_OS_HOME"
        print_success "Removed base installation"
    else
        print_warning "Base installation not found at $AGENT_OS_HOME"
    fi
}

remove_project() {
    if [[ "$DRY_RUN" == "true" ]]; then
        print_status "Would remove: $PROJECT_DIR/agent-os/"
        print_status "Would remove: $PROJECT_DIR/.agent-os/"
        print_status "Would remove: $PROJECT_DIR/.claude/commands/agent-os/"
        print_status "Would remove: $PROJECT_DIR/WORKER.md (if exists)"
        return
    fi

    if [[ -d "$PROJECT_DIR/agent-os" ]]; then
        print_status "Removing project installation at $PROJECT_DIR/agent-os/"
        rm -rf "$PROJECT_DIR/agent-os"
        print_success "Removed agent-os/"
    fi

    if [[ -d "$PROJECT_DIR/.agent-os" ]]; then
        print_status "Removing runtime data at $PROJECT_DIR/.agent-os/"
        rm -rf "$PROJECT_DIR/.agent-os"
        print_success "Removed .agent-os/"
    fi

    if [[ -d "$PROJECT_DIR/.claude/commands/agent-os" ]]; then
        print_status "Removing commands at $PROJECT_DIR/.claude/commands/agent-os/"
        rm -rf "$PROJECT_DIR/.claude/commands/agent-os"
        print_success "Removed .claude/commands/agent-os/"
    fi

    if [[ -f "$PROJECT_DIR/WORKER.md" ]]; then
        print_status "Removing WORKER.md..."
        rm "$PROJECT_DIR/WORKER.md"
        print_success "Removed WORKER.md"
    fi
}

main() {
    echo ""
    echo -e "${BLUE}=============================================${NC}"
    echo -e "${BLUE}   Agent OS Uninstall${NC}"
    echo -e "${BLUE}=============================================${NC}"
    echo ""

    parse_arguments "$@"

    if [[ "$REMOVE_BASE" == "false" ]] && [[ "$REMOVE_PROJECT" == "false" ]]; then
        print_error "No removal target specified. Use --base, --project, or --all."
        show_help
    fi

    if [[ "$DRY_RUN" == "true" ]]; then
        print_status "DRY RUN - No files will be removed"
        echo ""
    fi

    if [[ "$REMOVE_BASE" == "true" ]]; then
        remove_base
    fi

    if [[ "$REMOVE_PROJECT" == "true" ]]; then
        remove_project
    fi

    echo ""
    if [[ "$DRY_RUN" == "true" ]]; then
        print_status "Dry run complete. Remove --dry-run to actually delete files."
    else
        print_success "Uninstall complete!"
    fi
    echo ""
}

main "$@"
