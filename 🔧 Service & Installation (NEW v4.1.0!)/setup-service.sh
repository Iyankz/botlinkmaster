#!/bin/bash

# BotLinkMaster v4.0 - Service Setup Script
# Automatically configure and install systemd service

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

echo "============================================"
echo "BotLinkMaster - Service Setup"
echo "============================================"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    print_error "This script must be run as root"
    echo "Run: sudo $0"
    exit 1
fi

# Get actual user
if [ -n "$SUDO_USER" ]; then
    ACTUAL_USER="$SUDO_USER"
else
    print_error "Cannot determine actual user"
    echo "Run this script with: sudo ./setup-service.sh"
    exit 1
fi

# Get install directory
INSTALL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

print_info "Installation directory: $INSTALL_DIR"
print_info "User: $ACTUAL_USER"
echo ""

# Check if botlinkmaster files exist
if [ ! -f "$INSTALL_DIR/telegram_bot.py" ]; then
    print_error "telegram_bot.py not found in $INSTALL_DIR"
    exit 1
fi

if [ ! -f "$INSTALL_DIR/.env" ]; then
    print_warning ".env file not found"
    print_info "Creating .env from template..."
    cp "$INSTALL_DIR/.env.example" "$INSTALL_DIR/.env"
    chown "$ACTUAL_USER:$ACTUAL_USER" "$INSTALL_DIR/.env"
    chmod 600 "$INSTALL_DIR/.env"
    print_warning "Please edit .env and add your TELEGRAM_BOT_TOKEN"
fi

if [ ! -d "$INSTALL_DIR/venv" ]; then
    print_error "Virtual environment not found"
    print_info "Run ./install.sh first"
    exit 1
fi

# Configure service file
print_info "Configuring service file..."

SERVICE_FILE="/etc/systemd/system/botlinkmaster.service"
TEMP_SERVICE="/tmp/botlinkmaster.service.tmp"

# Read template and replace placeholders
sed -e "s|__USER__|$ACTUAL_USER|g" \
    -e "s|__INSTALL_DIR__|$INSTALL_DIR|g" \
    "$INSTALL_DIR/botlinkmaster.service" > "$TEMP_SERVICE"

# Install service file
cp "$TEMP_SERVICE" "$SERVICE_FILE"
rm "$TEMP_SERVICE"
chmod 644 "$SERVICE_FILE"

print_success "Service file installed: $SERVICE_FILE"

# Reload systemd
print_info "Reloading systemd daemon..."
systemctl daemon-reload
print_success "Systemd daemon reloaded"

# Enable service
print_info "Enabling service..."
systemctl enable botlinkmaster.service
print_success "Service enabled (will start on boot)"

echo ""
echo "============================================"
print_success "Service setup complete!"
echo "============================================"
echo ""
echo "📋 Service Commands:"
echo ""
echo "  Start service:"
echo "    ${GREEN}sudo systemctl start botlinkmaster${NC}"
echo ""
echo "  Stop service:"
echo "    ${YELLOW}sudo systemctl stop botlinkmaster${NC}"
echo ""
echo "  Restart service:"
echo "    ${BLUE}sudo systemctl restart botlinkmaster${NC}"
echo ""
echo "  Check status:"
echo "    ${BLUE}sudo systemctl status botlinkmaster${NC}"
echo ""
echo "  View logs:"
echo "    ${BLUE}sudo journalctl -u botlinkmaster -f${NC}"
echo ""
echo "  Disable auto-start:"
echo "    ${YELLOW}sudo systemctl disable botlinkmaster${NC}"
echo ""
echo "⚠️  IMPORTANT:"
echo "   Before starting, make sure .env contains valid TELEGRAM_BOT_TOKEN"
echo ""
echo "   Edit .env:"
echo "     sudo nano $INSTALL_DIR/.env"
echo ""
echo "   Then start the service:"
echo "     sudo systemctl start botlinkmaster"
echo ""
