#!/bin/bash

# BotLinkMaster v4.0 - Simple Installation Script (No Colors)
# Use this if install.sh has display issues
# Author: Yayang Ardiansyah

set -e

echo "======================================"
echo "BotLinkMaster v4.0 - Installation"
echo "======================================"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "=> Script requires root privileges"
    echo "=> Re-running with sudo..."
    echo ""
    sudo "$0" "$@"
    exit $?
fi

# Get actual user
if [ -n "$SUDO_USER" ]; then
    ACTUAL_USER="$SUDO_USER"
else
    ACTUAL_USER="$USER"
fi

echo "=> Running as: root"
echo "=> Target user: $ACTUAL_USER"
echo ""

# Detect OS
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
else
    OS=$(uname -s)
fi

echo "=> Detected OS: $OS"
echo ""

# Install system dependencies
echo "=> Installing system dependencies..."
case "$OS" in
    ubuntu|debian)
        apt-get update -qq
        apt-get install -y python3 python3-pip python3-venv git curl wget openssh-client telnet tzdata
        echo "=> System dependencies installed (Debian/Ubuntu)"
        ;;
    centos|rhel|fedora)
        yum install -y python3 python3-pip git curl wget openssh-clients telnet tzdata
        echo "=> System dependencies installed (CentOS/RHEL/Fedora)"
        ;;
    arch|manjaro)
        pacman -Sy --noconfirm python python-pip git curl wget openssh inetutils tzdata
        echo "=> System dependencies installed (Arch Linux)"
        ;;
    *)
        echo "=> Unknown OS: $OS"
        echo "=> Please manually install: python3, pip, git, openssh, telnet"
        read -p "Continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
        ;;
esac
echo ""

# Timezone configuration
echo "=> Timezone Configuration"
echo ""
CURRENT_TZ=$(timedatectl | grep 'Time zone' | awk '{print $3}' 2>/dev/null || cat /etc/timezone 2>/dev/null || echo 'Unknown')
echo "=> Current timezone: $CURRENT_TZ"
echo ""

read -p "Change timezone? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "Popular timezones:"
    echo "  1. Asia/Jakarta (WIB - UTC+7)"
    echo "  2. Asia/Makassar (WITA - UTC+8)"
    echo "  3. Asia/Jayapura (WIT - UTC+9)"
    echo "  4. Asia/Singapore (SGT - UTC+8)"
    echo "  5. UTC (UTC+0)"
    echo "  6. Custom"
    echo ""
    
    read -p "Select timezone (1-6): " tz_choice
    
    case $tz_choice in
        1) TIMEZONE="Asia/Jakarta" ;;
        2) TIMEZONE="Asia/Makassar" ;;
        3) TIMEZONE="Asia/Jayapura" ;;
        4) TIMEZONE="Asia/Singapore" ;;
        5) TIMEZONE="UTC" ;;
        6)
            echo ""
            read -p "Enter timezone (e.g., America/New_York): " TIMEZONE
            ;;
        *)
            echo "=> Invalid choice, using current timezone"
            TIMEZONE=""
            ;;
    esac
    
    if [ -n "$TIMEZONE" ]; then
        if timedatectl set-timezone "$TIMEZONE" 2>/dev/null; then
            echo "=> Timezone changed to: $TIMEZONE"
        elif [ -f "/usr/share/zoneinfo/$TIMEZONE" ]; then
            ln -sf "/usr/share/zoneinfo/$TIMEZONE" /etc/localtime
            echo "$TIMEZONE" > /etc/timezone
            echo "=> Timezone changed to: $TIMEZONE"
        else
            echo "=> Invalid timezone: $TIMEZONE"
            echo "=> Using current timezone"
        fi
    fi
else
    echo "=> Using current timezone"
fi
echo ""

# Switch to user
echo "=> Switching to user: $ACTUAL_USER"
echo ""

run_as_user() {
    su - "$ACTUAL_USER" -c "cd $(pwd) && $1"
}

# Check Python
echo "=> Checking Python version..."
PYTHON_VERSION=$(run_as_user "python3 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2")

if [ -z "$PYTHON_VERSION" ]; then
    echo "=> ERROR: Python 3 not found"
    exit 1
fi

REQUIRED_VERSION="3.8"
if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "=> ERROR: Python $PYTHON_VERSION is too old (need $REQUIRED_VERSION+)"
    exit 1
fi

echo "=> Python $PYTHON_VERSION found"
echo ""

# Create venv
echo "=> Creating virtual environment..."
if [ ! -d "venv" ]; then
    run_as_user "python3 -m venv venv"
    echo "=> Virtual environment created"
else
    echo "=> Virtual environment already exists"
fi
echo ""

# Upgrade pip
echo "=> Upgrading pip..."
run_as_user "venv/bin/pip install --upgrade pip -q" || echo "=> Pip upgrade failed, continuing..."
echo "=> Pip upgraded"
echo ""

# Install requirements
echo "=> Installing Python dependencies..."
if [ -f "requirements.txt" ]; then
    run_as_user "venv/bin/pip install -r requirements.txt"
    echo "=> Dependencies installed"
else
    echo "=> ERROR: requirements.txt not found"
    exit 1
fi
echo ""

# Setup config
echo "=> Setting up configuration..."
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        run_as_user "cp .env.example .env"
        echo "=> .env created from template"
        echo "=> IMPORTANT: Edit .env and add TELEGRAM_BOT_TOKEN"
    else
        run_as_user "cat > .env << 'EOL'
TELEGRAM_BOT_TOKEN=your_token_here
DATABASE_URL=sqlite:///botlinkmaster.db
LOG_LEVEL=INFO
EOL"
        echo "=> Basic .env created"
    fi
else
    echo "=> .env already exists"
fi

if [ ! -f "config.py" ]; then
    if [ -f "config_example.py" ]; then
        run_as_user "cp config_example.py config.py"
        echo "=> config.py created"
    fi
else
    echo "=> config.py already exists"
fi
echo ""

# Fix permissions
echo "=> Setting file permissions..."
chown -R "$ACTUAL_USER:$ACTUAL_USER" venv/ .env config.py 2>/dev/null || true
chmod 600 .env config.py 2>/dev/null || true
chmod +x install.sh install-simple.sh docker-run.sh cli.py 2>/dev/null || true
echo "=> Permissions set"
echo ""

# Test imports
echo "=> Testing imports..."
if run_as_user "venv/bin/python3 -c 'import paramiko; import telegram; import sqlalchemy' 2>/dev/null"; then
    echo "=> All modules imported successfully"
else
    echo "=> ERROR: Import test failed"
    exit 1
fi
echo ""

# Initialize database
echo "=> Initializing database..."
run_as_user "venv/bin/python3 << 'EOF'
from database import DatabaseManager
try:
    db = DatabaseManager()
    print('=> Database initialized')
except Exception as e:
    print(f'=> ERROR: {e}')
    exit(1)
EOF
" || echo "=> Database initialization failed"
echo ""

echo "======================================"
echo "=> Installation completed!"
echo "======================================"
echo ""
echo "Next steps:"
echo ""
echo "1. Edit .env file:"
echo "   nano .env"
echo "   (Add your TELEGRAM_BOT_TOKEN)"
echo ""
echo "2. Run the bot as user $ACTUAL_USER:"
echo "   su - $ACTUAL_USER"
echo "   cd $(pwd)"
echo "   source venv/bin/activate"
echo "   python telegram_bot.py"
echo ""
echo "Or run as user with sudo:"
echo "   sudo -u $ACTUAL_USER bash -c 'cd $(pwd) && source venv/bin/activate && python telegram_bot.py'"
echo ""
echo "Current timezone: $(timedatectl | grep 'Time zone' | awk '{print $3}' 2>/dev/null || cat /etc/timezone 2>/dev/null || echo 'Unknown')"
echo ""
echo "For help: https://github.com/yourusername/botlinkmaster"
echo ""
