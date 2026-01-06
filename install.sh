#!/bin/bash

# BotLinkMaster v4.0 - Installation Script
# Author: Yayang Ardiansyah
# Requires: root/sudo privileges for system package installation

set -e

echo "=================================="
echo "BotLinkMaster v4.0 - Installation"
echo "=================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

# Check if running as root, if not, re-run with sudo
if [ "$EUID" -ne 0 ]; then 
    print_warning "Script memerlukan root privileges untuk install system dependencies"
    print_info "Menjalankan ulang dengan sudo..."
    echo ""
    sudo "$0" "$@"
    exit $?
fi

# Get the actual user (not root when using sudo)
if [ -n "$SUDO_USER" ]; then
    ACTUAL_USER="$SUDO_USER"
    ACTUAL_HOME=$(getent passwd "$SUDO_USER" | cut -d: -f6)
else
    ACTUAL_USER="$USER"
    ACTUAL_HOME="$HOME"
fi

print_info "Running as: root (for system installation)"
print_info "Target user: $ACTUAL_USER"
echo ""

# Detect OS
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
    VER=$VERSION_ID
else
    OS=$(uname -s)
fi

print_info "Detected OS: $OS"
echo ""

# Function to install system dependencies based on OS
install_system_deps() {
    print_info "Installing system dependencies..."
    
    case "$OS" in
        ubuntu|debian)
            apt-get update -qq
            apt-get install -y \
                python3 \
                python3-pip \
                python3-venv \
                git \
                curl \
                wget \
                openssh-client \
                telnet \
                tzdata \
                || { print_error "Failed to install dependencies"; exit 1; }
            print_success "System dependencies installed (Debian/Ubuntu)"
            ;;
        
        centos|rhel|fedora)
            yum install -y \
                python3 \
                python3-pip \
                git \
                curl \
                wget \
                openssh-clients \
                telnet \
                tzdata \
                || { print_error "Failed to install dependencies"; exit 1; }
            print_success "System dependencies installed (CentOS/RHEL/Fedora)"
            ;;
        
        arch|manjaro)
            pacman -Sy --noconfirm \
                python \
                python-pip \
                git \
                curl \
                wget \
                openssh \
                inetutils \
                tzdata \
                || { print_error "Failed to install dependencies"; exit 1; }
            print_success "System dependencies installed (Arch Linux)"
            ;;
        
        *)
            print_warning "Unknown OS: $OS"
            print_warning "Please manually install: python3, pip, git, openssh, telnet"
            read -p "Continue anyway? (y/N): " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                exit 1
            fi
            ;;
    esac
}

# Install system dependencies
install_system_deps
echo ""

# Timezone Configuration
print_info "Konfigurasi Timezone"
echo ""
print_warning "Bot akan menggunakan timezone untuk logging dan timestamp"
print_info "Timezone saat ini: $(timedatectl | grep 'Time zone' | awk '{print $3}' || cat /etc/timezone 2>/dev/null || echo 'Unknown')"
echo ""

read -p "Apakah Anda ingin mengubah timezone? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    print_info "Beberapa timezone populer:"
    echo "  1. Asia/Jakarta (WIB - UTC+7)"
    echo "  2. Asia/Makassar (WITA - UTC+8)"
    echo "  3. Asia/Jayapura (WIT - UTC+9)"
    echo "  4. Asia/Singapore (SGT - UTC+8)"
    echo "  5. UTC (UTC+0)"
    echo "  6. Custom (masukkan manual)"
    echo ""
    
    read -p "Pilih timezone (1-6): " tz_choice
    
    case $tz_choice in
        1) TIMEZONE="Asia/Jakarta" ;;
        2) TIMEZONE="Asia/Makassar" ;;
        3) TIMEZONE="Asia/Jayapura" ;;
        4) TIMEZONE="Asia/Singapore" ;;
        5) TIMEZONE="UTC" ;;
        6)
            echo ""
            print_info "Daftar timezone: https://en.wikipedia.org/wiki/List_of_tz_database_time_zones"
            read -p "Masukkan timezone (contoh: America/New_York): " TIMEZONE
            ;;
        *)
            print_warning "Pilihan tidak valid, menggunakan timezone saat ini"
            TIMEZONE=""
            ;;
    esac
    
    if [ -n "$TIMEZONE" ]; then
        if timedatectl set-timezone "$TIMEZONE" 2>/dev/null; then
            print_success "Timezone diubah ke: $TIMEZONE"
        elif [ -f "/usr/share/zoneinfo/$TIMEZONE" ]; then
            ln -sf "/usr/share/zoneinfo/$TIMEZONE" /etc/localtime
            echo "$TIMEZONE" > /etc/timezone
            print_success "Timezone diubah ke: $TIMEZONE"
        else
            print_error "Timezone tidak valid: $TIMEZONE"
            print_warning "Menggunakan timezone saat ini"
        fi
    fi
else
    print_info "Menggunakan timezone saat ini"
fi
echo ""

# Now switch to actual user for Python operations
print_info "Switching to user: $ACTUAL_USER"
echo ""

# Create function to run as actual user
run_as_user() {
    su - "$ACTUAL_USER" -c "cd $(pwd) && $1"
}

# Check Python version
print_info "Checking Python version..."
PYTHON_VERSION=$(run_as_user "python3 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2")

if [ -z "$PYTHON_VERSION" ]; then
    print_error "Python 3 is not installed or not accessible"
    exit 1
fi

REQUIRED_VERSION="3.8"
if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    print_error "Python version $PYTHON_VERSION is too old. Required: $REQUIRED_VERSION or higher"
    exit 1
fi

print_success "Python $PYTHON_VERSION found"
echo ""

# Create virtual environment as actual user
print_info "Creating virtual environment..."
if [ ! -d "venv" ]; then
    run_as_user "python3 -m venv venv" || { print_error "Failed to create virtual environment"; exit 1; }
    print_success "Virtual environment created"
else
    print_info "Virtual environment already exists"
fi
echo ""

# Upgrade pip as actual user
print_info "Upgrading pip..."
run_as_user "venv/bin/pip install --upgrade pip -q" || print_warning "Pip upgrade failed, continuing..."
print_success "Pip upgraded"
echo ""

# Install requirements as actual user
print_info "Installing Python dependencies..."
if [ -f "requirements.txt" ]; then
    run_as_user "venv/bin/pip install -r requirements.txt" || { print_error "Failed to install dependencies"; exit 1; }
    print_success "Dependencies installed"
else
    print_error "requirements.txt not found!"
    exit 1
fi
echo ""

# Setup configuration files as actual user
print_info "Setting up configuration..."
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        run_as_user "cp .env.example .env"
        print_success ".env file created from template"
        print_warning "Please edit .env and add your TELEGRAM_BOT_TOKEN"
    else
        print_warning ".env.example not found, creating basic .env..."
        run_as_user "cat > .env << 'EOL'
TELEGRAM_BOT_TOKEN=your_token_here
DATABASE_URL=sqlite:///botlinkmaster.db
LOG_LEVEL=INFO
EOL"
        print_success "Basic .env file created"
    fi
else
    print_info ".env file already exists"
fi

if [ ! -f "config.py" ]; then
    if [ -f "config_example.py" ]; then
        run_as_user "cp config_example.py config.py"
        print_success "config.py created from template"
    fi
else
    print_info "config.py already exists"
fi
echo ""

# Fix permissions
print_info "Setting file permissions..."
chown -R "$ACTUAL_USER:$ACTUAL_USER" venv/ .env config.py 2>/dev/null || true
chmod 600 .env config.py 2>/dev/null || true
chmod +x install.sh docker-run.sh cli.py 2>/dev/null || true
print_success "Permissions set"
echo ""

# Test imports as actual user
print_info "Testing imports..."
if run_as_user "venv/bin/python3 -c 'import paramiko; import telegram; import sqlalchemy' 2>/dev/null"; then
    print_success "All core modules imported successfully"
else
    print_error "Import test failed"
    exit 1
fi
echo ""

# Initialize database as actual user
print_info "Initializing database..."
run_as_user "venv/bin/python3 << 'EOF'
from database import DatabaseManager
try:
    db = DatabaseManager()
    print('Database initialized successfully')
except Exception as e:
    print(f'Database initialization error: {e}')
    exit(1)
EOF
" && print_success "Database initialized" || print_error "Database initialization failed"
echo ""

echo "=================================="
print_success "Installation completed!"
echo "=================================="
echo ""
echo "📝 Next steps:"
echo "1. Edit .env file and add your TELEGRAM_BOT_TOKEN:"
echo "   ${YELLOW}nano .env${NC}"
echo ""
echo "2. Run the bot as user $ACTUAL_USER:"
echo "   ${YELLOW}su - $ACTUAL_USER${NC}"
echo "   ${YELLOW}cd $(pwd)${NC}"
echo "   ${YELLOW}source venv/bin/activate${NC}"
echo "   ${YELLOW}python telegram_bot.py${NC}"
echo ""
echo "Or use sudo to run as user:"
echo "   ${YELLOW}sudo -u $ACTUAL_USER bash -c 'cd $(pwd) && source venv/bin/activate && python telegram_bot.py'${NC}"
echo ""
echo "For help, visit: https://github.com/yourusername/botlinkmaster"
echo ""

# Show timezone info
print_info "Current timezone: $(timedatectl | grep 'Time zone' | awk '{print $3}' 2>/dev/null || cat /etc/timezone 2>/dev/null || echo 'Unknown')"
echo ""
