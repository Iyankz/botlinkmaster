#!/bin/bash

# BotLinkMaster v4.1.0 - Complete Installation Script
# One-command setup: installs everything + systemd service
# Improved version with better error handling and path management

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_success() { echo -e "${GREEN}✓${NC} $1"; }
print_error() { echo -e "${RED}✗${NC} $1"; }
print_warning() { echo -e "${YELLOW}⚠${NC} $1"; }
print_info() { echo -e "${BLUE}ℹ${NC} $1"; }

clear
echo "╔════════════════════════════════════════════════╗"
echo "║     BotLinkMaster v4.1.0 - Complete Setup     ║"
echo "║     Systemd Service + Auto-Start              ║"
echo "╚════════════════════════════════════════════════╝"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    print_warning "This script needs root privileges"
    print_info "Re-running with sudo..."
    echo ""
    exec sudo "$0" "$@"
fi

# Get actual user
if [ -n "$SUDO_USER" ]; then
    ACTUAL_USER="$SUDO_USER"
    ACTUAL_HOME=$(getent passwd "$SUDO_USER" | cut -d: -f6)
else
    ACTUAL_USER="$USER"
    ACTUAL_HOME="$HOME"
fi

# Get install directory (use pwd instead of BASH_SOURCE for better compatibility)
INSTALL_DIR="$(pwd)"

print_info "Installation directory: $INSTALL_DIR"
print_info "Running as root, target user: $ACTUAL_USER"
echo ""

# ============================================
# STEP 0: Pre-flight Checks
# ============================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 0: Pre-flight Checks"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check critical files exist in current directory
CRITICAL_FILES=(
    "telegram_bot.py"
    "botlinkmaster.py"
    "database.py"
    "requirements.txt"
    ".env.example"
    "botlinkmaster.service"
)

print_info "Checking for critical files..."
missing_files=0
for file in "${CRITICAL_FILES[@]}"; do
    if [ -f "$INSTALL_DIR/$file" ]; then
        print_success "$file found"
    else
        print_error "$file NOT FOUND!"
        missing_files=1
    fi
done

if [ $missing_files -eq 1 ]; then
    echo ""
    print_error "Some critical files are missing!"
    print_error "Please ensure all files are in the current directory."
    print_error "Current directory: $INSTALL_DIR"
    echo ""
    print_info "Expected structure:"
    echo "  botlinkmaster/"
    echo "  ├── telegram_bot.py"
    echo "  ├── botlinkmaster.py"
    echo "  ├── database.py"
    echo "  ├── requirements.txt"
    echo "  ├── .env.example"
    echo "  └── ... (all other files)"
    echo ""
    print_info "ALL files must be directly in the root folder!"
    print_info "DO NOT create subfolders like 'Configuration' or 'Documentation'!"
    exit 1
fi

# Check for wrong subfolders
print_info "Checking for incorrect folder structure..."
WRONG_FOLDERS=(
    "Configuration"
    "Service & Installation"
    "Documentation"
    "Core Python Modules"
)

wrong_structure=0
for folder in "${WRONG_FOLDERS[@]}"; do
    if [ -d "$INSTALL_DIR/$folder" ]; then
        print_warning "Found incorrect folder: $folder"
        print_warning "This folder should not exist!"
        wrong_structure=1
    fi
done

if [ $wrong_structure -eq 1 ]; then
    echo ""
    print_error "Incorrect folder structure detected!"
    print_info "All files must be directly in the root directory."
    print_info "Please move files from subfolders to root and delete the subfolders."
    echo ""
    print_info "To fix automatically, run: ./fix-structure.sh"
    exit 1
fi

print_success "File structure OK"
echo ""

# ============================================
# STEP 1: Detect OS and Install Dependencies
# ============================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 1/8: Installing System Dependencies"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
    print_info "Detected OS: $PRETTY_NAME"
else
    print_error "Cannot detect OS"
    exit 1
fi

print_info "Installing dependencies..."
case $OS in
    ubuntu|debian)
        apt-get update -qq
        apt-get install -y -qq python3 python3-pip python3-venv git curl wget openssh-client telnet 2>&1 | grep -v "^Selecting\|^Preparing\|^Unpacking\|^Setting up" || true
        ;;
    centos|rhel|fedora|rocky|almalinux)
        if command -v dnf &> /dev/null; then
            dnf install -y -q python3 python3-pip git curl wget openssh-clients telnet 2>&1 | grep -v "Installing\|Upgrading\|Complete" || true
        else
            yum install -y -q python3 python3-pip git curl wget openssh-clients telnet 2>&1 | grep -v "Installing\|Upgrading\|Complete" || true
        fi
        ;;
    arch|manjaro)
        pacman -Sy --noconfirm python python-pip git curl wget openssh inetutils 2>&1 | grep -v "installing\|upgrading" || true
        ;;
    *)
        print_warning "Unknown OS. Attempting to continue..."
        ;;
esac

print_success "Dependencies installed"
echo ""

# ============================================
# STEP 2: Configure Timezone
# ============================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 2/8: Configuring Timezone"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

CURRENT_TZ=$(timedatectl show --property=Timezone --value 2>/dev/null || cat /etc/timezone 2>/dev/null || echo "UTC")
print_info "Current timezone: $CURRENT_TZ"
echo ""
echo "Options:"
echo "  1. Asia/Jakarta (WIB)"
echo "  2. Asia/Makassar (WITA)"  
echo "  3. Asia/Jayapura (WIT)"
echo "  4. Keep current ($CURRENT_TZ)"
echo ""
read -p "Select (1-4) [4]: " tz_choice
tz_choice=${tz_choice:-4}

case $tz_choice in
    1) TIMEZONE="Asia/Jakarta" ;;
    2) TIMEZONE="Asia/Makassar" ;;
    3) TIMEZONE="Asia/Jayapura" ;;
    *) TIMEZONE="$CURRENT_TZ" ;;
esac

if [ "$TIMEZONE" != "$CURRENT_TZ" ]; then
    timedatectl set-timezone "$TIMEZONE" 2>/dev/null || {
        ln -sf "/usr/share/zoneinfo/$TIMEZONE" /etc/localtime
        echo "$TIMEZONE" > /etc/timezone
    }
    print_success "Timezone set to: $TIMEZONE"
else
    print_info "Using timezone: $TIMEZONE"
fi

echo ""

# ============================================
# STEP 3: Check Python
# ============================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 3/8: Checking Python"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

run_as_user() {
    su - "$ACTUAL_USER" -c "cd '$INSTALL_DIR' && $1"
}

PYTHON_VERSION=$(run_as_user "python3 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2")
print_success "Python $PYTHON_VERSION found"
echo ""

# ============================================
# STEP 4: Create Virtual Environment
# ============================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 4/8: Setting Up Virtual Environment"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if [ -d "$INSTALL_DIR/venv" ]; then
    print_info "Virtual environment already exists, skipping..."
else
    run_as_user "python3 -m venv venv"
    print_success "Virtual environment created"
fi

run_as_user "venv/bin/pip install --upgrade pip -q"
print_success "Pip upgraded"
echo ""

# ============================================
# STEP 5: Install Python Dependencies
# ============================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 5/8: Installing Python Dependencies"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Verify requirements.txt exists and is readable
if [ ! -f "$INSTALL_DIR/requirements.txt" ]; then
    print_error "requirements.txt not found in $INSTALL_DIR"
    print_error "Make sure requirements.txt is in the root directory!"
    exit 1
fi

if [ ! -r "$INSTALL_DIR/requirements.txt" ]; then
    print_error "requirements.txt is not readable"
    exit 1
fi

print_info "Installing from: $INSTALL_DIR/requirements.txt"
run_as_user "venv/bin/pip install -r requirements.txt -q"
print_success "Python dependencies installed"
echo ""

# ============================================
# STEP 6: Setup Configuration
# ============================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 6/8: Setting Up Configuration"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Create .env if it doesn't exist
if [ ! -f "$INSTALL_DIR/.env" ]; then
    if [ -f "$INSTALL_DIR/.env.example" ]; then
        run_as_user "cp .env.example .env"
        print_success ".env file created from .env.example"
        print_warning "IMPORTANT: You need to add your Telegram bot token to .env"
    else
        print_error ".env.example not found!"
        exit 1
    fi
else
    print_info ".env file already exists"
fi

# Create config.py if it doesn't exist
if [ ! -f "$INSTALL_DIR/config.py" ]; then
    if [ -f "$INSTALL_DIR/config_example.py" ]; then
        run_as_user "cp config_example.py config.py"
        print_success "config.py created from config_example.py"
    else
        print_warning "config_example.py not found, skipping config.py creation"
    fi
else
    print_info "config.py already exists"
fi

# Set proper permissions
chown "$ACTUAL_USER:$ACTUAL_USER" "$INSTALL_DIR/.env" 2>/dev/null || true
chmod 600 "$INSTALL_DIR/.env"
print_success "Configuration files secured"
echo ""

# ============================================
# STEP 7: Setup Systemd Service
# ============================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 7/8: Setting Up Systemd Service"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check if service file exists
if [ ! -f "$INSTALL_DIR/botlinkmaster.service" ]; then
    print_error "botlinkmaster.service not found!"
    print_error "Make sure botlinkmaster.service is in the root directory!"
    exit 1
fi

# Update service file with actual paths
PYTHON_PATH="$INSTALL_DIR/venv/bin/python"
BOT_SCRIPT="$INSTALL_DIR/telegram_bot.py"

# Create service file
cat > /etc/systemd/system/botlinkmaster.service << EOF
[Unit]
Description=BotLinkMaster v4.1.0 - Network Device Monitoring Bot
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=$ACTUAL_USER
WorkingDirectory=$INSTALL_DIR
Environment="PATH=$INSTALL_DIR/venv/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=$PYTHON_PATH $BOT_SCRIPT
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=botlinkmaster

# Security
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ReadWritePaths=$INSTALL_DIR

# Resource limits
MemoryMax=512M
CPUQuota=100%

[Install]
WantedBy=multi-user.target
EOF

print_success "Service file created: /etc/systemd/system/botlinkmaster.service"

# Reload systemd
systemctl daemon-reload
print_success "Systemd reloaded"

# Enable service
systemctl enable botlinkmaster
print_success "Service enabled (auto-start on boot)"

echo ""

# ============================================
# STEP 8: Final Setup
# ============================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 8/8: Final Setup"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Make scripts executable
chmod +x "$INSTALL_DIR/botctl" 2>/dev/null || true
chmod +x "$INSTALL_DIR/setup-service.sh" 2>/dev/null || true
chmod +x "$INSTALL_DIR/diagnose.py" 2>/dev/null || true
chmod +x "$INSTALL_DIR/test_bot.py" 2>/dev/null || true
chmod +x "$INSTALL_DIR/cli.py" 2>/dev/null || true
print_success "Scripts made executable"

# Fix ownership
chown -R "$ACTUAL_USER:$ACTUAL_USER" "$INSTALL_DIR"
print_success "File ownership fixed"

echo ""

# ============================================
# Installation Complete
# ============================================
echo "╔════════════════════════════════════════════════╗"
echo "║          ✓ Installation Complete!            ║"
echo "╚════════════════════════════════════════════════╝"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📝 NEXT STEPS:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "1. Add your Telegram bot token to .env:"
echo "   sudo nano .env"
echo "   (Add: TELEGRAM_BOT_TOKEN=your_token_here)"
echo ""
echo "2. (Optional) Configure access control:"
echo "   Send /myid to your bot to get your Chat ID"
echo "   Add to .env: ALLOWED_CHAT_IDS=123456789"
echo ""
echo "3. Start the service:"
echo "   sudo systemctl start botlinkmaster"
echo ""
echo "4. Check service status:"
echo "   sudo systemctl status botlinkmaster"
echo ""
echo "5. View logs (realtime):"
echo "   sudo journalctl -u botlinkmaster -f"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎮 QUICK COMMANDS (using botctl):"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  sudo ./botctl start     # Start service"
echo "  sudo ./botctl stop      # Stop service"
echo "  sudo ./botctl restart   # Restart service"
echo "  sudo ./botctl status    # Check status"
echo "  sudo ./botctl logs      # View logs"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📚 Documentation:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  README.md             - Main documentation"
echo "  SERVICE_GUIDE.md      - Service management guide"
echo "  BOTCTL_GUIDE.md       - botctl usage guide"
echo "  TROUBLESHOOTING.md    - Fix common issues"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
print_success "BotLinkMaster v4.1.0 installed successfully!"
echo ""
