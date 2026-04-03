#!/bin/bash

# =============================================================================
# Agent OS Project Installation Script
# Installs Agent OS into a project's codebase
# =============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BASE_DIR="$(dirname "$SCRIPT_DIR")"
PROJECT_DIR="$(pwd)"

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

print_section() {
    echo ""
    echo -e "${BLUE}=============================================${NC}"
    echo -e "${BLUE}   $1${NC}"
    echo -e "${BLUE}=============================================${NC}"
    echo ""
}

print_verbose() {
    if [[ "$VERBOSE" == "true" ]]; then
        echo -e "${BLUE}[VERBOSE]${NC} $1"
    fi
}

ensure_dir() {
    if [[ ! -d "$1" ]]; then
        mkdir -p "$1"
    fi
}

# -----------------------------------------------------------------------------
# Default Values
# -----------------------------------------------------------------------------

VERBOSE="false"
PROFILE=""
COMMANDS_ONLY="false"

# -----------------------------------------------------------------------------
# Help Function
# -----------------------------------------------------------------------------

show_help() {
    cat << EOF
Usage: $0 [OPTIONS]

Install Agent OS into the current project directory.

Options:
    --profile <name>     Use specified profile (default: from config.yml)
    --commands-only      Only update commands, preserve existing standards
    --verbose            Show detailed output
    -h, --help           Show this help message

Examples:
    $0
    $0 --profile default
    $0 --commands-only

EOF
    exit 0
}

# -----------------------------------------------------------------------------
# Parse Command Line Arguments
# -----------------------------------------------------------------------------

parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --profile)
                PROFILE="$2"
                shift 2
                ;;
            --commands-only)
                COMMANDS_ONLY="true"
                shift
                ;;
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
# Validation Functions
# -----------------------------------------------------------------------------

validate_base_installation() {
    if [[ ! -d "$BASE_DIR" ]]; then
        print_error "Agent OS base installation not found"
        echo ""
        echo "Run the base installation first:"
        echo "  ~/.agent-os/scripts/install-base.sh"
        exit 1
    fi

    if [[ ! -f "$BASE_DIR/config.yml" ]]; then
        print_error "Base installation config.yml not found"
        exit 1
    fi
}

validate_not_in_base() {
    if [[ "$PROJECT_DIR" == "$BASE_DIR" ]]; then
        print_error "Cannot install Agent OS in the base installation directory"
        echo ""
        echo "Navigate to your project directory first:"
        echo "  cd /path/to/your/project"
        echo ""
        exit 1
    fi
}

# -----------------------------------------------------------------------------
# Configuration Functions
# -----------------------------------------------------------------------------

load_configuration() {
    local config_file="$BASE_DIR/config.yml"

    # Simple YAML parsing for default_profile
    local default_profile="default"
    if [[ -f "$config_file" ]]; then
        default_profile=$(grep "^default_profile:" "$config_file" | cut -d' ' -f2 | tr -d '[:space:]')
    fi

    # Use command line profile or default
    EFFECTIVE_PROFILE="${PROFILE:-$default_profile}"

    # Validate profile exists
    if [[ ! -d "$BASE_DIR/profiles/$EFFECTIVE_PROFILE" ]]; then
        print_warning "Profile not found: $EFFECTIVE_PROFILE (using default)"
        EFFECTIVE_PROFILE="default"
    fi

    print_verbose "Using profile: $EFFECTIVE_PROFILE"
}

# -----------------------------------------------------------------------------
# Confirmation Functions
# -----------------------------------------------------------------------------

confirm_standards_overwrite() {
    if [[ "$COMMANDS_ONLY" == "true" ]]; then
        return 0
    fi

    local existing_standards="$PROJECT_DIR/agent-os/standards"

    if [[ -d "$existing_standards" ]]; then
        echo ""
        print_warning "Existing standards folder detected at: $existing_standards"
        echo ""
        echo "This will overwrite your existing standards with standards from the '$EFFECTIVE_PROFILE' profile."
        echo ""
        read -p "Do you want to continue? (y/N) " -n 1 -r
        echo ""
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo ""
            echo "Installation cancelled."
            echo ""
            echo "To update only commands without touching standards, use:"
            echo "  $0 --commands-only"
            echo ""
            exit 0
        fi
    fi
}

# -----------------------------------------------------------------------------
# Installation Functions
# -----------------------------------------------------------------------------

create_project_structure() {
    print_status "Creating project structure..."

    ensure_dir "$PROJECT_DIR/agent-os"
    ensure_dir "$PROJECT_DIR/agent-os/standards"
    ensure_dir "$PROJECT_DIR/.agent-os"
    ensure_dir "$PROJECT_DIR/.agent-os/memory"
    ensure_dir "$PROJECT_DIR/.agent-os/sessions"
    ensure_dir "$PROJECT_DIR/.agent-os/cache"

    print_success "Created agent-os/ directory structure"
}

install_standards() {
    if [[ "$COMMANDS_ONLY" == "true" ]]; then
        print_status "Skipping standards (--commands-only)"
        return
    fi

    echo ""
    print_status "Installing standards..."

    local profile_standards="$BASE_DIR/profiles/$EFFECTIVE_PROFILE/standards"
    local project_standards="$PROJECT_DIR/agent-os/standards"
    local file_count=0

    if [[ -d "$profile_standards" ]]; then
        # Copy all standards from profile
        while IFS= read -r -d '' file; do
            local relative_path="${file#$profile_standards/}"
            local dest_file="$project_standards/$relative_path"

            ensure_dir "$(dirname "$dest_file")"
            cp "$file" "$dest_file"
            ((file_count++))
        done < <(find "$profile_standards" -name "*.md" -type f ! -path "*/.backups/*" -print0 2>/dev/null)
    fi

    # Copy base standards if profile doesn't have any
    if [[ $file_count -eq 0 ]] && [[ -d "$BASE_DIR/standards" ]]; then
        while IFS= read -r -d '' file; do
            local relative_path="${file#$BASE_DIR/standards/}"
            local dest_file="$project_standards/$relative_path"

            ensure_dir "$(dirname "$dest_file")"
            cp "$file" "$dest_file"
            ((file_count++))
        done < <(find "$BASE_DIR/standards" -name "*.md" -type f ! -path "*/.backups/*" -print0 2>/dev/null)
    fi

    if [[ $file_count -gt 0 ]]; then
        print_success "Installed $file_count standards files"
    else
        print_success "No standards to install (profile is empty)"
    fi
}

create_index() {
    echo ""
    print_status "Updating standards index..."

    local standards_dir="$PROJECT_DIR/agent-os/standards"
    local index_file="$standards_dir/index.yml"

    # Start fresh
    echo "# Agent OS Standards Index" > "$index_file"
    echo "" >> "$index_file"

    local entry_count=0

    # Handle root-level .md files
    local root_files=$(find "$standards_dir" -maxdepth 1 -name "*.md" -type f 2>/dev/null | sort)
    if [[ -n "$root_files" ]]; then
        echo "root:" >> "$index_file"
        while IFS= read -r file; do
            local filename=$(basename "$file" .md)
            echo "  $filename:" >> "$index_file"
            echo "    description: Needs description" >> "$index_file"
            ((entry_count++))
        done <<< "$root_files"
        echo "" >> "$index_file"
    fi

    # Handle files in subfolders
    local folders=$(find "$standards_dir" -mindepth 1 -maxdepth 1 -type d 2>/dev/null | sort)
    for folder in $folders; do
        local folder_name=$(basename "$folder")
        local md_files=$(find "$folder" -name "*.md" -type f 2>/dev/null | sort)

        if [[ -n "$md_files" ]]; then
            echo "$folder_name:" >> "$index_file"
            while IFS= read -r file; do
                local filename=$(basename "$file" .md)
                echo "  $filename:" >> "$index_file"
                echo "    description: Needs description" >> "$index_file"
                ((entry_count++))
            done <<< "$md_files"
            echo "" >> "$index_file"
        fi
    fi

    if [[ $entry_count -gt 0 ]]; then
        print_success "Created index.yml ($entry_count entries)"
    else
        print_success "Created index.yml (no standards to index)"
    fi
}

install_commands() {
    echo ""
    print_status "Installing commands..."

    local commands_source="$BASE_DIR/commands/agent-os"
    local commands_dest="$PROJECT_DIR/.claude/commands/agent-os"

    if [[ ! -d "$commands_source" ]]; then
        print_warning "No commands found in base installation"
        return
    fi

    ensure_dir "$commands_dest"

    local count=0
    for file in "$commands_source"/*.md; do
        if [[ -f "$file" ]]; then
            cp "$file" "$commands_dest/"
            ((count++))
        fi
    done

    if [[ $count -gt 0 ]]; then
        print_success "Installed $count commands to .claude/commands/agent-os/"
    else
        print_warning "No command files found"
    fi
}

copy_worker_md() {
    echo ""
    print_status "Installing project instructions..."

    local worker_source="$BASE_DIR/WORKER.md"
    local worker_dest="$PROJECT_DIR/WORKER.md"

    if [[ -f "$worker_source" ]]; then
        if [[ ! -f "$worker_dest" ]]; then
            cp "$worker_source" "$worker_dest"
            print_success "Copied WORKER.md to project root"
        else
            print_warning "WORKER.md already exists in project, skipping"
        fi
    fi
}

# -----------------------------------------------------------------------------
# Main Execution
# -----------------------------------------------------------------------------

main() {
    print_section "Agent OS Project Installation"

    # Parse arguments
    parse_arguments "$@"

    # Validations
    validate_not_in_base
    validate_base_installation

    # Load configuration
    load_configuration

    # Show configuration
    echo ""
    print_status "Configuration:"
    echo "  Profile: $EFFECTIVE_PROFILE"
    echo "  Commands only: $COMMANDS_ONLY"

    # Confirm overwrite if standards folder exists
    confirm_standards_overwrite

    echo ""

    # Install
    create_project_structure
    install_standards
    create_index
    install_commands
    copy_worker_md

    echo ""
    print_success "Agent OS installed successfully!"
    echo ""
    echo "Next steps:"
    echo "  1. Run /discover-standards to extract patterns from your codebase"
    echo "  2. Run /inject-standards to inject standards into your context"
    echo "  3. Start building with AgentOS!"
    echo ""
}

# Run main function
main "$@"
