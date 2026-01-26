#!/bin/bash
#
# BotLinkMaster v4.8.8 - Installation Script
# 
# Usage: chmod +x install.sh && ./install.sh
#

set -e

VERSION="4.8.7"

echo "=============================================="
echo "BotLinkMaster v${VERSION} - Installation Script"
echo "=============================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo -e "${RED}Please do not run as root. Run as normal user.${NC}"
    echo "Usage: ./install.sh"
    exit 1
fi

# Get current directory
INSTALL_DIR=$(pwd)
USER=$(whoami)

echo "Installation directory: $INSTALL_DIR"
echo "User: $USER"
echo ""

# Step 1: Install System Dependencies
echo -e "${YELLOW}[1/7] Installing system dependencies...${NC}"

# Check if apt is available
if command -v apt &> /dev/null; then
    echo "Updating package list..."
    sudo apt update
    
    echo "Installing Python and required packages..."
    sudo apt install -y python3 python3-pip python3-venv
    
    # Get Python version and install specific venv package
    PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
    echo "Python version detected: $PYTHON_VERSION"
    
    # Install version-specific venv package (fixes ensurepip error)
    sudo apt install -y python${PYTHON_VERSION}-venv || true
    
    echo -e "${GREEN}✓ System dependencies installed${NC}"
else
    echo -e "${RED}apt not found. Please install manually:${NC}"
    echo "  - python3"
    echo "  - python3-pip"
    echo "  - python3-venv"
    exit 1
fi

# Step 2: Check Python
echo ""
echo -e "${YELLOW}[2/7] Checking Python...${NC}"
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo -e "${GREEN}✓ $PYTHON_VERSION${NC}"
else
    echo -e "${RED}✗ Python3 not found!${NC}"
    exit 1
fi

# Step 3: Create virtual environment
echo ""
echo -e "${YELLOW}[3/7] Creating virtual environment...${NC}"

# Remove old venv if exists and broken
if [ -d "venv" ]; then
    if [ ! -f "venv/bin/activate" ]; then
        echo "Removing broken virtual environment..."
        rm -rf venv
    fi
fi

if [ -d "venv" ]; then
    echo "Virtual environment already exists"
else
    echo "Creating new virtual environment..."
    python3 -m venv venv
    
    if [ ! -f "venv/bin/activate" ]; then
        echo -e "${RED}Failed to create virtual environment!${NC}"
        echo ""
        echo "Try running manually:"
        echo "  sudo apt install python3.10-venv  # or your Python version"
        echo "  python3 -m venv venv"
        exit 1
    fi
    
    echo -e "${GREEN}✓ Virtual environment created${NC}"
fi

# Step 4: Install Python dependencies
echo ""
echo -e "${YELLOW}[4/7] Installing Python packages...${NC}"
source venv/bin/activate
pip install --upgrade pip
pip install python-telegram-bot python-dotenv paramiko pytz
echo -e "${GREEN}✓ Python packages installed${NC}"

# Step 5: Create .env file
echo ""
echo -e "${YELLOW}[5/7] Setting up configuration...${NC}"
if [ -f ".env" ]; then
    echo ".env file already exists, skipping..."
else
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo -e "${GREEN}✓ Created .env from .env.example${NC}"
    else
        cat > .env << 'EOF'
# BotLinkMaster v4.8.8 Configuration

# Telegram Bot Token from @BotFather (REQUIRED)
TELEGRAM_BOT_TOKEN=

# Allowed Chat IDs (comma separated)
# Leave empty to allow all
# User ID: positive number (e.g., 216481118)
# Group ID: negative number (e.g., -1001234567890)
ALLOWED_CHAT_IDS=

# Timezone (default: Asia/Jakarta)
TIMEZONE=Asia/Jakarta
EOF
        echo -e "${GREEN}✓ Created .env file${NC}"
    fi
fi

# Step 6: Create systemd service
echo ""
echo -e "${YELLOW}[6/7] Creating systemd service...${NC}"

SERVICE_FILE="/etc/systemd/system/botlinkmaster.service"

# Create service content
SERVICE_CONTENT="[Unit]
Description=BotLinkMaster v${VERSION} - Network Device Monitoring Bot
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$INSTALL_DIR
Environment=PATH=$INSTALL_DIR/venv/bin
ExecStart=$INSTALL_DIR/venv/bin/python $INSTALL_DIR/telegram_bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target"

echo "$SERVICE_CONTENT" | sudo tee $SERVICE_FILE > /dev/null
sudo systemctl daemon-reload
echo -e "${GREEN}✓ Systemd service created${NC}"

# Step 7: Set permissions
echo ""
echo -e "${YELLOW}[7/7] Setting file permissions...${NC}"
chmod 755 *.py 2>/dev/null || true
chmod 755 *.sh 2>/dev/null || true
chmod 600 .env 2>/dev/null || true
echo -e "${GREEN}✓ Permissions set${NC}"

# Done!
echo ""
echo "=============================================="
echo -e "${GREEN}Installation Complete!${NC}"
echo -e "${BLUE}BotLinkMaster v${VERSION}${NC}"
echo "=============================================="
echo ""
echo -e "${YELLOW}NEXT STEPS:${NC}"
echo ""
echo "1. Get your Bot Token from @BotFather on Telegram"
echo "   - Open Telegram and search for @BotFather"
echo "   - Send /newbot and follow instructions"
echo "   - Copy the token"
echo ""
echo "2. Edit .env file and add your Bot Token:"
echo -e "   ${GREEN}nano .env${NC}"
echo ""
echo "   Add your token:"
echo "   TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz"
echo ""
echo "3. Get your Chat ID:"
echo "   - Search @userinfobot on Telegram"
echo "   - Send /start to get your Chat ID"
echo "   - Add it to ALLOWED_CHAT_IDS in .env"
echo ""
echo "4. Start the bot:"
echo -e "   ${GREEN}sudo systemctl start botlinkmaster${NC}"
echo ""
echo "5. Check status:"
echo -e "   ${GREEN}sudo systemctl status botlinkmaster${NC}"
echo ""
echo "6. View logs:"
echo -e "   ${GREEN}sudo journalctl -u botlinkmaster -f${NC}"
echo ""
echo "7. Enable auto-start on boot:"
echo -e "   ${GREEN}sudo systemctl enable botlinkmaster${NC}"
echo ""
echo "=============================================="
echo "For manual testing:"
echo -e "   ${GREEN}source venv/bin/activate${NC}"
echo -e "   ${GREEN}python telegram_bot.py${NC}"
echo "=============================================="
echo ""
echo -e "${YELLOW}Need help? Use /help command in bot${NC}"
echo ""
