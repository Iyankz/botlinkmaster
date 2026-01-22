#!/bin/bash
#
# BotLinkMaster v4.8.7 - Update Script
# 
# Features:
# - Version checking (local vs remote)
# - Automatic backup before update
# - Rollback capability
# - Preserves user configuration
#
# Usage: 
#   ./update.sh          - Check and update to latest version
#   ./update.sh --force  - Force update without version check
#   ./update.sh --rollback [backup_dir] - Rollback to previous version
#
# GitHub: https://github.com/YOUR_USERNAME/botlinkmaster
#

set -e

# ============================================
# CONFIGURATION - EDIT THIS FOR YOUR REPO
# ============================================
GITHUB_USER="YOUR_USERNAME"
GITHUB_REPO="botlinkmaster"
GITHUB_BRANCH="main"
# ============================================

REPO_URL="https://raw.githubusercontent.com/${GITHUB_USER}/${GITHUB_REPO}/${GITHUB_BRANCH}"
SCRIPT_VERSION="4.8.7"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Get current directory
INSTALL_DIR=$(pwd)

# Files to update (will be replaced)
UPDATE_FILES=(
    "telegram_bot.py"
    "botlinkmaster.py"
    "vendor_commands.py"
    "database.py"
    "timezone_config.py"
)

# Script files to update
SCRIPT_FILES=(
    "update.sh"
    "install.sh"
)

# Documentation files to update
DOC_FILES=(
    "README.md"
    "CHANGELOG.md"
    "VERSION"
    ".env.example"
    "requirements.txt"
)

# Files to preserve (will NOT be replaced)
PRESERVE_FILES=(
    "botlinkmaster.db"
    ".env"
    "timezone.conf"
    "botlinkmaster.log"
)

# ============================================
# FUNCTIONS
# ============================================

print_header() {
    echo ""
    echo -e "${CYAN}=============================================="
    echo "   BotLinkMaster Update Script v${SCRIPT_VERSION}"
    echo -e "==============================================${NC}"
    echo ""
}

print_usage() {
    echo "Usage:"
    echo "  ./update.sh              - Check and update to latest version"
    echo "  ./update.sh --force      - Force update without version check"
    echo "  ./update.sh --check      - Check for updates only (no install)"
    echo "  ./update.sh --rollback   - Rollback to previous backup"
    echo "  ./update.sh --help       - Show this help"
    echo ""
}

check_installation() {
    if [ ! -f "telegram_bot.py" ]; then
        echo -e "${RED}Error: telegram_bot.py not found!${NC}"
        echo "Please run this script from the BotLinkMaster directory."
        exit 1
    fi
}

get_local_version() {
    if [ -f "VERSION" ]; then
        cat VERSION | tr -d '[:space:]'
    else
        echo "unknown"
    fi
}

get_remote_version() {
    local remote_ver
    remote_ver=$(wget -q -O - "${REPO_URL}/VERSION" 2>/dev/null | tr -d '[:space:]')
    if [ -z "$remote_ver" ]; then
        echo "error"
    else
        echo "$remote_ver"
    fi
}

version_compare() {
    # Returns: 0 if equal, 1 if $1 > $2, 2 if $1 < $2
    if [ "$1" = "$2" ]; then
        return 0
    fi
    
    local IFS=.
    local i ver1=($1) ver2=($2)
    
    for ((i=0; i<${#ver1[@]} || i<${#ver2[@]}; i++)); do
        local v1=${ver1[i]:-0}
        local v2=${ver2[i]:-0}
        if ((v1 > v2)); then
            return 1
        elif ((v1 < v2)); then
            return 2
        fi
    done
    return 0
}

check_for_updates() {
    echo -e "${YELLOW}Checking for updates...${NC}"
    echo ""
    
    local local_ver=$(get_local_version)
    local remote_ver=$(get_remote_version)
    
    echo -e "Local version:  ${BLUE}v${local_ver}${NC}"
    
    if [ "$remote_ver" = "error" ]; then
        echo -e "Remote version: ${RED}Unable to fetch${NC}"
        echo ""
        echo -e "${YELLOW}Could not connect to GitHub. Check your internet connection.${NC}"
        return 1
    fi
    
    echo -e "Remote version: ${GREEN}v${remote_ver}${NC}"
    echo ""
    
    version_compare "$local_ver" "$remote_ver"
    local result=$?
    
    if [ $result -eq 0 ]; then
        echo -e "${GREEN}✓ You are running the latest version!${NC}"
        return 0
    elif [ $result -eq 1 ]; then
        echo -e "${YELLOW}⚠ Your version is newer than remote (development version?)${NC}"
        return 0
    else
        echo -e "${CYAN}↑ Update available: v${local_ver} → v${remote_ver}${NC}"
        return 2
    fi
}

create_backup() {
    echo -e "${YELLOW}[1/6] Creating backup...${NC}"
    
    BACKUP_DIR="backup_$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$BACKUP_DIR"
    
    # Backup all Python files
    for file in *.py; do
        if [ -f "$file" ]; then
            cp "$file" "$BACKUP_DIR/"
        fi
    done
    
    # Backup script files
    for file in *.sh; do
        if [ -f "$file" ]; then
            cp "$file" "$BACKUP_DIR/"
        fi
    done
    
    # Backup VERSION and docs
    for file in VERSION README.md CHANGELOG.md .env.example requirements.txt; do
        if [ -f "$file" ]; then
            cp "$file" "$BACKUP_DIR/"
        fi
    done
    
    # Backup preserved files if they exist
    for file in "${PRESERVE_FILES[@]}"; do
        if [ -f "$file" ]; then
            cp "$file" "$BACKUP_DIR/"
        fi
    done
    
    echo -e "${GREEN}✓ Backup created: $BACKUP_DIR${NC}"
}

stop_service() {
    echo ""
    echo -e "${YELLOW}[2/6] Stopping service...${NC}"
    
    if systemctl is-active --quiet botlinkmaster 2>/dev/null; then
        sudo systemctl stop botlinkmaster
        echo -e "${GREEN}✓ Service stopped${NC}"
    else
        echo "Service not running, continuing..."
    fi
}

download_core_files() {
    echo ""
    echo -e "${YELLOW}[3/6] Downloading core files...${NC}"
    
    local failed=0
    for file in "${UPDATE_FILES[@]}"; do
        echo -n "  Downloading $file... "
        if wget -q -O "$file.new" "$REPO_URL/$file" 2>/dev/null; then
            mv "$file.new" "$file"
            echo -e "${GREEN}✓${NC}"
        else
            echo -e "${RED}✗${NC}"
            rm -f "$file.new"
            ((failed++))
        fi
    done
    
    if [ $failed -gt 0 ]; then
        echo -e "${YELLOW}Warning: $failed file(s) failed to download${NC}"
    fi
}

download_script_files() {
    echo ""
    echo -e "${YELLOW}[4/6] Downloading script files...${NC}"
    
    for file in "${SCRIPT_FILES[@]}"; do
        echo -n "  Downloading $file... "
        if wget -q -O "$file.new" "$REPO_URL/$file" 2>/dev/null; then
            mv "$file.new" "$file"
            chmod +x "$file"
            echo -e "${GREEN}✓${NC}"
        else
            echo -e "${YELLOW}⊘ (optional)${NC}"
            rm -f "$file.new"
        fi
    done
    
    for file in "${DOC_FILES[@]}"; do
        echo -n "  Downloading $file... "
        if wget -q -O "$file.new" "$REPO_URL/$file" 2>/dev/null; then
            mv "$file.new" "$file"
            echo -e "${GREEN}✓${NC}"
        else
            echo -e "${YELLOW}⊘ (optional)${NC}"
            rm -f "$file.new"
        fi
    done
}

set_permissions() {
    echo ""
    echo -e "${YELLOW}[5/6] Setting permissions...${NC}"
    
    chmod 644 *.py 2>/dev/null || true
    chmod 755 *.sh 2>/dev/null || true
    chmod 600 .env 2>/dev/null || true
    chmod 644 VERSION 2>/dev/null || true
    chmod 644 README.md 2>/dev/null || true
    chmod 644 CHANGELOG.md 2>/dev/null || true
    
    echo -e "${GREEN}✓ Permissions set${NC}"
}

restart_service() {
    echo ""
    echo -e "${YELLOW}[6/6] Restarting service...${NC}"
    
    if systemctl is-enabled --quiet botlinkmaster 2>/dev/null; then
        sudo systemctl restart botlinkmaster
        sleep 2
        
        if systemctl is-active --quiet botlinkmaster; then
            echo -e "${GREEN}✓ Service restarted successfully${NC}"
        else
            echo -e "${RED}✗ Service failed to start${NC}"
            echo "Check logs: sudo journalctl -u botlinkmaster -f"
        fi
    else
        echo "Service not enabled, skipping restart..."
        echo "Start manually: sudo systemctl start botlinkmaster"
    fi
}

show_summary() {
    local new_ver=$(get_local_version)
    
    echo ""
    echo -e "${CYAN}=============================================="
    echo -e "${GREEN}           Update Complete!${NC}"
    echo -e "${CYAN}==============================================${NC}"
    echo ""
    echo -e "Version: ${GREEN}v${new_ver}${NC}"
    echo ""
    echo -e "${YELLOW}Files updated:${NC}"
    for file in "${UPDATE_FILES[@]}"; do
        echo "  ✓ $file"
    done
    echo ""
    echo -e "${YELLOW}Files preserved:${NC}"
    for file in "${PRESERVE_FILES[@]}"; do
        if [ -f "$file" ]; then
            echo "  ✓ $file"
        fi
    done
    echo ""
    echo -e "${YELLOW}Backup location:${NC} $BACKUP_DIR"
    echo ""
    echo -e "${BLUE}Commands:${NC}"
    echo "  Status: sudo systemctl status botlinkmaster"
    echo "  Logs:   sudo journalctl -u botlinkmaster -f"
    echo "  Rollback: ./update.sh --rollback $BACKUP_DIR"
    echo ""
}

do_rollback() {
    local backup_dir="$1"
    
    # If no backup specified, find the latest
    if [ -z "$backup_dir" ]; then
        backup_dir=$(ls -td backup_* 2>/dev/null | head -1)
        if [ -z "$backup_dir" ]; then
            echo -e "${RED}Error: No backup directory found!${NC}"
            exit 1
        fi
    fi
    
    if [ ! -d "$backup_dir" ]; then
        echo -e "${RED}Error: Backup directory not found: $backup_dir${NC}"
        echo ""
        echo "Available backups:"
        ls -d backup_* 2>/dev/null || echo "  (none)"
        exit 1
    fi
    
    echo -e "${YELLOW}Rolling back from: $backup_dir${NC}"
    echo ""
    
    # Stop service
    if systemctl is-active --quiet botlinkmaster 2>/dev/null; then
        echo "Stopping service..."
        sudo systemctl stop botlinkmaster
    fi
    
    # Restore files
    echo "Restoring files..."
    for file in "$backup_dir"/*.py "$backup_dir"/*.sh "$backup_dir"/VERSION "$backup_dir"/README.md "$backup_dir"/CHANGELOG.md; do
        if [ -f "$file" ]; then
            filename=$(basename "$file")
            cp "$file" "./$filename"
            echo "  ✓ $filename"
        fi
    done
    
    # Set permissions
    chmod 644 *.py 2>/dev/null || true
    chmod 755 *.sh 2>/dev/null || true
    
    # Restart service
    if systemctl is-enabled --quiet botlinkmaster 2>/dev/null; then
        echo ""
        echo "Restarting service..."
        sudo systemctl restart botlinkmaster
        sleep 2
        
        if systemctl is-active --quiet botlinkmaster; then
            echo -e "${GREEN}✓ Service restarted${NC}"
        else
            echo -e "${RED}✗ Service failed to start${NC}"
        fi
    fi
    
    local restored_ver=$(get_local_version)
    echo ""
    echo -e "${GREEN}✓ Rollback complete! Now running v${restored_ver}${NC}"
}

do_update() {
    local force=$1
    
    if [ "$force" != "true" ]; then
        check_for_updates
        local result=$?
        
        if [ $result -eq 0 ]; then
            echo ""
            read -p "Do you want to force reinstall anyway? (y/N): " confirm
            if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
                echo "Update cancelled."
                exit 0
            fi
        elif [ $result -eq 1 ]; then
            # Error fetching version
            echo ""
            read -p "Continue with update anyway? (y/N): " confirm
            if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
                echo "Update cancelled."
                exit 0
            fi
        fi
    fi
    
    echo ""
    create_backup
    stop_service
    download_core_files
    download_script_files
    set_permissions
    restart_service
    show_summary
}

# ============================================
# MAIN
# ============================================

print_header
check_installation

case "${1:-}" in
    --help|-h)
        print_usage
        exit 0
        ;;
    --check|-c)
        check_for_updates
        exit $?
        ;;
    --force|-f)
        echo -e "${YELLOW}Force update mode${NC}"
        do_update "true"
        ;;
    --rollback|-r)
        do_rollback "${2:-}"
        ;;
    "")
        do_update "false"
        ;;
    *)
        echo -e "${RED}Unknown option: $1${NC}"
        print_usage
        exit 1
        ;;
esac
