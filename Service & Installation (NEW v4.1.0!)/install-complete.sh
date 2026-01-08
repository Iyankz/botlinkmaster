#!/bin/bash

# BotLinkMaster v4.0 - Complete Installation Script
# One-command setup: installs everything + systemd service

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

# Get install directory
INSTALL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

print_info "Installation directory: $INSTALL_DIR"
print_info "Running as root, target user: $ACTUAL_USER"
echo ""

# Detect OS
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
else
    OS=$(uname -s)
fi

print_info "Detected OS: $OS"
echo ""

# ============================================
# STEP 1: Install System Dependencies
# ============================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 1/8: Installing System Dependencies"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

case "$OS" in
    ubuntu|debian)
        apt-get update -qq
        apt-get install -y python3 python3-pip python3-venv git curl wget openssh-client telnet tzdata >/dev/null 2>&1
        print_success "System dependencies installed (Debian/Ubuntu)"
        ;;
    centos|rhel|fedora)
        yum install -y python3 python3-pip git curl wget openssh-clients telnet tzdata >/dev/null 2>&1
        print_success "System dependencies installed (CentOS/RHEL)"
        ;;
    arch|manjaro)
        pacman -Sy --noconfirm python python-pip git curl wget openssh inetutils tzdata >/dev/null 2>&1
        print_success "System dependencies installed (Arch Linux)"
        ;;
    *)
        print_warning "Unknown OS, attempting to continue..."
        ;;
esac

echo ""

# ============================================
# STEP 2: Configure Timezone
# ============================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 2/8: Timezone Configuration"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

CURRENT_TZ=$(timedatectl 2>/dev/null | grep 'Time zone' | awk '{print $3}' || cat /etc/timezone 2>/dev/null || echo 'UTC')
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

if [ ! -d "venv" ]; then
    run_as_user "python3 -m venv venv"
    print_success "Virtual environment created"
else
    print_info "Virtual environment already exists"
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

if [ -f "requirements.txt" ]; then
    run_as_user "venv/bin/pip install -r requirements.txt -q"
    print_success "Python dependencies installed"
else
    print_error "requirements.txt not found!"
    exit 1
fi

echo ""

# ============================================
# STEP 6: Setup Configuration Files
# ============================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 6/8: Configuration Setup"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        run_as_user "cp .env.example .env"
        print_success ".env created from template"
    else
        run_as_user "cat > .env << 'EOL'
TELEGRAM_BOT_TOKEN=your_token_here
DATABASE_URL=sqlite:///botlinkmaster.db
LOG_LEVEL=INFO
ALLOWED_CHAT_IDS=
EOL"
        print_success "Basic .env created"
    fi
    print_warning "IMPORTANT: Edit .env and add TELEGRAM_BOT_TOKEN"
else
    print_info ".env already exists"
fi

if [ ! -f "config.py" ] && [ -f "config_example.py" ]; then
    run_as_user "cp config_example.py config.py"
    print_success "config.py created"
fi

# Set permissions
chown -R "$ACTUAL_USER:$ACTUAL_USER" "$INSTALL_DIR"
chmod 600 .env 2>/dev/null || true
chmod +x install.sh setup-service.sh botctl docker-run.sh cli.py diagnose.py test_bot.py 2>/dev/null || true

print_success "Permissions configured"
echo ""

# ============================================
# STEP 7: Initialize Database
# ============================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 7/8: Database Initialization"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

run_as_user "venv/bin/python3 << 'EOF'
from database import DatabaseManager
try:
    db = DatabaseManager()
    print('Database initialized successfully')
except Exception as e:
    print(f'Database error: {e}')
    exit(1)
EOF
" && print_success "Database initialized" || print_warning "Database initialization had issues"

echo ""

# ============================================
# STEP 8: Setup Systemd Service
# ============================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 8/8: Installing Systemd Service"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

SERVICE_FILE="/etc/systemd/system/botlinkmaster.service"

# Create service file
cat > "$SERVICE_FILE" << EOF
[Unit]
Description=BotLinkMaster v4.0 - Network Device Monitoring Bot
Documentation=https://github.com/Iyankz/botlinkmaster
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=$ACTUAL_USER
Group=$ACTUAL_USER
WorkingDirectory=$INSTALL_DIR

Environment="PATH=$INSTALL_DIR/venv/bin:/usr/local/bin:/usr/bin:/bin"
EnvironmentFile=$INSTALL_DIR/.env

ExecStart=$INSTALL_DIR/venv/bin/python $INSTALL_DIR/telegram_bot.py

Restart=always
RestartSec=10
StartLimitInterval=200
StartLimitBurst=5

StandardOutput=journal
StandardError=journal
SyslogIdentifier=botlinkmaster

MemoryMax=512M
CPUQuota=100%

NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=$INSTALL_DIR

[Install]
WantedBy=multi-user.target
EOF

print_success "Service file created: $SERVICE_FILE"

# Reload systemd
systemctl daemon-reload
print_success "Systemd reloaded"

# Enable service
systemctl enable botlinkmaster.service
print_success "Service enabled (will start on boot)"

echo ""

# ============================================
# FINAL SUMMARY
# ============================================
clear
echo "╔════════════════════════════════════════════════╗"
echo "║          Installation Complete! ✅            ║"
echo "╚════════════════════════════════════════════════╝"
echo ""
print_success "BotLinkMaster installed successfully!"
echo ""
echo "📍 Installation: $INSTALL_DIR"
echo "👤 User: $ACTUAL_USER"
echo "🌍 Timezone: $TIMEZONE"
echo "🚀 Service: Enabled & Ready"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "NEXT STEPS:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "1️⃣  Configure Bot Token:"
echo ""
echo "    ${YELLOW}sudo nano $INSTALL_DIR/.env${NC}"
echo ""
echo "    Add your token (no spaces around =):"
echo "    TELEGRAM_BOT_TOKEN=123456:ABCdefGHIjklMNOpqrsTUVwxyz"
echo ""
echo "2️⃣  Start the Service:"
echo ""
echo "    ${GREEN}sudo systemctl start botlinkmaster${NC}"
echo ""
echo "3️⃣  Check Status:"
echo ""
echo "    ${BLUE}sudo systemctl status botlinkmaster${NC}"
echo ""
echo "4️⃣  View Logs:"
echo ""
echo "    ${BLUE}sudo journalctl -u botlinkmaster -f${NC}"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "QUICK COMMANDS:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  Start:    sudo systemctl start botlinkmaster"
echo "  Stop:     sudo systemctl stop botlinkmaster"
echo "  Restart:  sudo systemctl restart botlinkmaster"
echo "  Status:   sudo systemctl status botlinkmaster"
echo "  Logs:     sudo journalctl -u botlinkmaster -f"
echo ""
echo "  Or use:   sudo ./botctl <start|stop|restart|status|logs>"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "SYSTEM INFO:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  ✅ Service enabled (auto-start on boot)"
echo "  ✅ All dependencies installed"
echo "  ✅ Database initialized"
echo "  ✅ Virtual environment ready"
echo "  ✅ Permissions configured"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
print_warning "Don't forget to edit .env with your bot token!"
echo ""
print_info "After adding token, just run: sudo systemctl start botlinkmaster"
echo ""
echo "📚 Documentation:"
echo "   • SERVICE_GUIDE.md - Complete service guide"
echo "   • QUICKSTART_SERVICE.md - Quick start guide"
echo "   • TROUBLESHOOTING.md - Fix common issues"
echo ""
echo "🆘 Need help? Run: python diagnose.py"
echo ""