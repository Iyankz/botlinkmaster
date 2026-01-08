#!/usr/bin/env python3
"""
BotLinkMaster - Simple Test Bot
Minimal bot to test if Telegram connection works
"""

import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Load environment
load_dotenv()
token = os.getenv('TELEGRAM_BOT_TOKEN')

if not token:
    print("❌ ERROR: TELEGRAM_BOT_TOKEN not found!")
    print("Run: python diagnose.py")
    exit(1)

print("=" * 60)
print("BotLinkMaster - Test Bot")
print("=" * 60)
print(f"\nToken: {token[:10]}...")
print("\nStarting bot...\n")

# Simple handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    chat_id = update.effective_chat.id
    username = update.effective_user.username or "Unknown"
    
    message = f"""
✅ Bot is WORKING!

Your Info:
• Chat ID: {chat_id}
• Username: @{username}
• Name: {update.effective_user.first_name}

The bot is receiving your messages correctly.
If you see this, the main bot should work too.

Next step: Run the main bot with 'python telegram_bot.py'
"""
    
    print(f"📨 Received /start from Chat ID: {chat_id} (@{username})")
    await update.message.reply_text(message)

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Echo any message"""
    chat_id = update.effective_chat.id
    text = update.message.text
    
    print(f"📨 Received message from {chat_id}: {text}")
    await update.message.reply_text(f"✅ Received: {text}")

def main():
    """Start the test bot"""
    try:
        # Create application
        app = Application.builder().token(token).build()
        
        # Add handlers
        app.add_handler(CommandHandler("start", start))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
        
        print("✅ Test bot started!")
        print("📱 Send /start to your bot in Telegram")
        print("⌨️  Or send any message to test")
        print("\n[Press Ctrl+C to stop]\n")
        
        # Start polling
        app.run_polling(allowed_updates=Update.ALL_TYPES)
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        print("\nPossible issues:")
        print("1. Invalid token - Run: python diagnose.py")
        print("2. Network issue - Check internet connection")
        print("3. Telegram API down - Try again later")

if __name__ == '__main__':
    main()
