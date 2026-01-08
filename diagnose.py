#!/usr/bin/env python3
"""
BotLinkMaster - Diagnostic Script
Check bot configuration and connectivity
"""

import os
import sys
from dotenv import load_dotenv
import requests

print("=" * 60)
print("BotLinkMaster Diagnostic Tool")
print("=" * 60)
print()

# Step 1: Check .env file
print("1. Checking .env file...")
if not os.path.exists('.env'):
    print("   ❌ FAIL: .env file not found!")
    print("   Solution: cp .env.example .env")
    sys.exit(1)
else:
    print("   ✅ PASS: .env file exists")

# Step 2: Load environment variables
print("\n2. Loading environment variables...")
load_dotenv()
token = os.getenv('TELEGRAM_BOT_TOKEN')

if not token or token == 'your_bot_token_here':
    print("   ❌ FAIL: TELEGRAM_BOT_TOKEN not set or invalid!")
    print("   Current value:", repr(token))
    print("   Solution: Edit .env and add your real bot token")
    sys.exit(1)
else:
    print(f"   ✅ PASS: Token loaded ({token[:10]}...)")

# Step 3: Check token format
print("\n3. Checking token format...")
if ':' not in token:
    print("   ❌ FAIL: Invalid token format!")
    print("   Token should be like: 123456789:ABCdefGHIjklMNOpqrsTUVwxyz")
    sys.exit(1)
else:
    bot_id = token.split(':')[0]
    print(f"   ✅ PASS: Token format valid (Bot ID: {bot_id})")

# Step 4: Test bot API connection
print("\n4. Testing Telegram API connection...")
try:
    url = f"https://api.telegram.org/bot{token}/getMe"
    response = requests.get(url, timeout=10)
    
    if response.status_code == 200:
        data = response.json()
        if data.get('ok'):
            bot_info = data.get('result', {})
            print("   ✅ PASS: API connection successful!")
            print(f"   Bot ID: {bot_info.get('id')}")
            print(f"   Bot Username: @{bot_info.get('username')}")
            print(f"   Bot Name: {bot_info.get('first_name')}")
        else:
            print("   ❌ FAIL: API returned error")
            print(f"   Error: {data.get('description')}")
            sys.exit(1)
    elif response.status_code == 401:
        print("   ❌ FAIL: Invalid bot token!")
        print("   The token is not recognized by Telegram")
        print("   Solution: Get a new token from @BotFather")
        sys.exit(1)
    else:
        print(f"   ❌ FAIL: HTTP {response.status_code}")
        print(f"   Response: {response.text}")
        sys.exit(1)
        
except requests.exceptions.RequestException as e:
    print("   ❌ FAIL: Network error!")
    print(f"   Error: {e}")
    print("   Check your internet connection")
    sys.exit(1)

# Step 5: Check for pending updates
print("\n5. Checking for pending updates...")
try:
    url = f"https://api.telegram.org/bot{token}/getUpdates"
    response = requests.get(url, timeout=10)
    
    if response.status_code == 200:
        data = response.json()
        if data.get('ok'):
            updates = data.get('result', [])
            print(f"   ✅ PASS: {len(updates)} pending update(s)")
            
            if len(updates) > 0:
                print("\n   📨 Recent messages:")
                for update in updates[-5:]:  # Show last 5
                    msg = update.get('message', {})
                    chat = msg.get('chat', {})
                    text = msg.get('text', 'N/A')
                    print(f"      - Chat ID: {chat.get('id')}, Message: {text}")
            else:
                print("   ℹ️  No pending messages")
                print("   Try sending /start to your bot in Telegram")
        else:
            print("   ❌ FAIL: Cannot get updates")
            print(f"   Error: {data.get('description')}")
    else:
        print(f"   ❌ FAIL: HTTP {response.status_code}")
        
except Exception as e:
    print(f"   ⚠️  WARNING: {e}")

# Step 6: Check dependencies
print("\n6. Checking Python dependencies...")
try:
    import telegram
    print(f"   ✅ python-telegram-bot: {telegram.__version__}")
except ImportError:
    print("   ❌ FAIL: python-telegram-bot not installed")
    print("   Solution: pip install -r requirements.txt")
    sys.exit(1)

try:
    import paramiko
    print(f"   ✅ paramiko: {paramiko.__version__}")
except ImportError:
    print("   ❌ FAIL: paramiko not installed")
    sys.exit(1)

try:
    import sqlalchemy
    print(f"   ✅ sqlalchemy: {sqlalchemy.__version__}")
except ImportError:
    print("   ❌ FAIL: sqlalchemy not installed")
    sys.exit(1)

# Step 7: Check database
print("\n7. Checking database...")
try:
    from database import DatabaseManager
    db = DatabaseManager()
    stats = db.get_statistics()
    print(f"   ✅ PASS: Database initialized")
    print(f"   Total devices: {stats['total_devices']}")
    print(f"   Cached interfaces: {stats['total_cached_interfaces']}")
except Exception as e:
    print(f"   ❌ FAIL: Database error")
    print(f"   Error: {e}")

# Step 8: Check ALLOWED_CHAT_IDS
print("\n8. Checking access control...")
allowed_ids = os.getenv('ALLOWED_CHAT_IDS', '')
if allowed_ids:
    ids = [id.strip() for id in allowed_ids.split(',') if id.strip()]
    print(f"   ℹ️  Access restricted to {len(ids)} chat ID(s)")
    print(f"   Allowed: {', '.join(ids)}")
else:
    print("   ℹ️  No access restriction (all users allowed)")

# Summary
print("\n" + "=" * 60)
print("✅ ALL CHECKS PASSED!")
print("=" * 60)
print("\n📋 Next Steps:")
print("1. Start the bot:")
print("   python telegram_bot.py")
print("\n2. Open Telegram and find your bot:")
print(f"   Search: @{bot_info.get('username')}")
print("\n3. Send /start to begin")
print("\n4. If bot doesn't respond:")
print("   - Check bot is running (look for 'Bot started successfully')")
print("   - Make sure you're chatting with the correct bot")
print("   - Check your Chat ID is in ALLOWED_CHAT_IDS (if enabled)")
print("   - Check bot logs: tail -f botlinkmaster.log")
print()
