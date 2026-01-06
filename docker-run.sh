#!/bin/bash

# BotLinkMaster v4.0 - Docker Deployment Script

set -e

echo "=================================="
echo "BotLinkMaster Docker Deployment"
echo "=================================="
echo ""

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ Error: .env file not found!"
    echo ""
    echo "Please create .env file with your configuration:"
    echo "  cp .env.example .env"
    echo "  nano .env  # Add your TELEGRAM_BOT_TOKEN"
    echo ""
    exit 1
fi

# Source .env file
export $(grep -v '^#' .env | xargs)

# Check if TELEGRAM_BOT_TOKEN is set
if [ -z "$TELEGRAM_BOT_TOKEN" ]; then
    echo "❌ Error: TELEGRAM_BOT_TOKEN not set in .env file!"
    echo ""
    echo "Please edit .env and add your bot token:"
    echo "  TELEGRAM_BOT_TOKEN=your_token_here"
    echo ""
    exit 1
fi

# Create data directories if they don't exist
mkdir -p data logs

# Build and start containers
echo "🐳 Building Docker image..."
docker-compose build

echo ""
echo "🚀 Starting BotLinkMaster..."
docker-compose up -d

echo ""
echo "✅ BotLinkMaster is now running!"
echo ""
echo "📊 Check status:"
echo "  docker-compose ps"
echo ""
echo "📋 View logs:"
echo "  docker-compose logs -f"
echo ""
echo "⏹️  Stop the bot:"
echo "  docker-compose down"
echo ""
