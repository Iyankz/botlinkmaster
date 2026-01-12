#!/bin/bash
#
# BotLinkMaster v4.5 - Installation Script
# 
# Usage: bash install.sh
#

set -e

echo "=============================================="
echo "BotLinkMaster v4.5 - Installation Script"
echo "=============================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo -e "${RED}Please do not run as root. Run as normal user.${NC}"
    exit 1
fi

# Get current directory
INSTALL_DIR=$(pwd)
USER=$(whoami)

echo "Installation directory: $INSTALL_DIR"
echo "User: $USER"
echo ""

# Step 1: Check Python
echo -e "${YELLOW}[1/6] Checking Python...${NC}"
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo -e "${GREEN}✓ $PYTHON_VERSION${NC}"
else
    echo -e "${RED}✗ Python3 not found. Installing...${NC}"
    sudo apt update
    sudo apt install -y python3 python3-pip python3-venv
fi

# Step 2: Create virtual environment
echo ""
echo -e "${YELLOW}[2/6] Creating virtual environment...${NC}"
if [ -d "venv" ]; then
    echo "Virtual environment already exists"
else
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
fi

# Step 3: Install dependencies
echo ""
echo -e "${YELLOW}[3/6] Installing Python packages...${NC}"
source venv/bin/activate
pip install --upgrade pip
pip install python-telegram-bot python-dotenv paramiko pytz
echo -e "${GREEN}✓ Packages installed${NC}"

# Step 4: Create .env file
echo ""
echo -e "${YELLOW}[4/6] Setting up configuration...${NC}"
if [ -f ".env" ]; then
    echo ".env file already exists"
else
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo -e "${GREEN}✓ Created .env from .env.example${NC}"
        echo -e "${YELLOW}! Please edit .env and add your Telegram Bot Token${NC}"
    else
        echo "TELEGRAM_BOT_TOKEN=" > .env
        echo "ALLOWED_CHAT_IDS=" >> .env
        echo "TIMEZONE=Asia/Jakarta" >> .env
        echo -e "${GREEN}✓ Created .env file${NC}"
    fi
fi

# Step 5: Create systemd service
echo ""
echo -e "${YELLOW}[5/6] Creating systemd service...${NC}"

SERVICE_FILE="/etc/systemd/system/botlinkmaster.service"
SERVICE_CONTENT="[Unit]
Description=BotLinkMaster v4.5 - Network Device Monitoring Bot
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

# Step 6: Instructions
echo ""
echo -e "${YELLOW}[6/6] Setup complete!${NC}"
echo ""
echo "=============================================="
echo -e "${GREEN}Installation Complete!${NC}"
echo "=============================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Edit .env file and add your Telegram Bot Token:"
echo "   nano .env"
echo ""
echo "2. Get your Chat ID by sending /myid to @userinfobot"
echo "   Add it to ALLOWED_CHAT_IDS in .env"
echo ""
echo "3. Start the bot:"
echo "   sudo systemctl start botlinkmaster"
echo ""
echo "4. Check status:"
echo "   sudo systemctl status botlinkmaster"
echo ""
echo "5. View logs:"
echo "   sudo journalctl -u botlinkmaster -f"
echo ""
echo "6. Enable auto-start on boot:"
echo "   sudo systemctl enable botlinkmaster"
echo ""
echo "=============================================="
echo "Manual start (for testing):"
echo "   source venv/bin/activate"
echo "   python telegram_bot.py"
echo "=============================================="
