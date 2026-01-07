#!/usr/bin/env python3
"""
BotLinkMaster v4.1 - Telegram Bot Interface
Telegram bot for managing and monitoring network devices

Author: Yayang Ardiansyah
License: MIT
"""

import os
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters
)
from telegram.constants import ParseMode

from botlinkmaster import BotLinkMaster, ConnectionConfig, Protocol
from database import DatabaseManager

# Load environment variables from .env file
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('botlinkmaster.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize database
db = DatabaseManager()

# Load allowed chat IDs from environment
ALLOWED_CHAT_IDS = os.getenv('ALLOWED_CHAT_IDS', '')
if ALLOWED_CHAT_IDS:
    ALLOWED_CHAT_IDS = [int(chat_id.strip()) for chat_id in ALLOWED_CHAT_IDS.split(',') if chat_id.strip()]
else:
    ALLOWED_CHAT_IDS = []

logger.info(f"Allowed chat IDs: {ALLOWED_CHAT_IDS if ALLOWED_CHAT_IDS else 'All (no restriction)'}")


def is_authorized(chat_id: int) -> bool:
    """Check if chat ID is authorized to use the bot"""
    if not ALLOWED_CHAT_IDS:  # If empty, allow all
        return True
    return chat_id in ALLOWED_CHAT_IDS


async def check_authorization(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Check if user is authorized and send message if not"""
    chat_id = update.effective_chat.id
    
    if not is_authorized(chat_id):
        logger.warning(f"Unauthorized access attempt from chat ID: {chat_id}")
        await update.message.reply_text(
            "❌ *Access Denied*\n\n"
            "Anda tidak memiliki akses ke bot ini.\n\n"
            f"Your Chat ID: `{chat_id}`\n\n"
            "Hubungi administrator untuk mendapatkan akses.",
            parse_mode=ParseMode.MARKDOWN
        )
        return False
    return True


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /start is issued"""
    if not await check_authorization(update, context):
        return
    
    chat_id = update.effective_chat.id
    welcome_message = """
🤖 *BotLinkMaster v4\.1\.0*

Selamat datang\! Bot ini membantu Anda memonitor perangkat jaringan\.

📋 *Perintah yang tersedia:*
/start \- Tampilkan pesan ini
/help \- Bantuan lengkap
/list \- Daftar semua perangkat
/add \- Tambah perangkat baru
/device <nama> \- Info detail perangkat
/cek <device> <interface> \- Cek status interface
/delete <nama> \- Hapus perangkat
/myid \- Tampilkan Chat ID Anda

Gunakan /help untuk panduan lengkap\.
"""
    await update.message.reply_text(
        welcome_message,
        parse_mode=ParseMode.MARKDOWN_V2
    )
    logger.info(f"User {chat_id} started the bot")


async def myid_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show user's chat ID"""
    chat_id = update.effective_chat.id
    username = update.effective_user.username or "N/A"
    first_name = update.effective_user.first_name or "N/A"
    
    message = f"""
📱 *Informasi Anda*

*Chat ID:* `{chat_id}`
*Username:* @{username}
*Nama:* {first_name}

Gunakan Chat ID ini untuk konfigurasi ALLOWED\_CHAT\_IDS di file \.env
"""
    await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN_V2)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send help message"""
    if not await check_authorization(update, context):
        return
    
    help_text = """
📖 *Bantuan BotLinkMaster*

*1\. Menambah Perangkat \(/add\)*
Format multiline:
```
/add
nama: router\-1
host: 192\.168\.1\.1
username: admin
password: password123
protocol: ssh
port: 22
description: Router utama
location: Kantor pusat
```

*2\. Cek Interface \(/cek\)*
```
/cek router\-1 GigabitEthernet0/0
```

*3\. List Perangkat \(/list\)*
```
/list
```

*4\. Detail Perangkat \(/device\)*
```
/device router\-1
```

*5\. Hapus Perangkat \(/delete\)*
```
/delete router\-1
```

*6\. Chat ID \(/myid\)*
```
/myid
```

*Catatan:*
• Protocol: ssh atau telnet
• Port opsional \(default SSH:22, Telnet:23\)
• Description dan location opsional
"""
    await update.message.reply_text(
        help_text,
        parse_mode=ParseMode.MARKDOWN_V2
    )


async def list_devices(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """List all registered devices"""
    if not await check_authorization(update, context):
        return
    
    devices = db.get_all_devices()
    
    if not devices:
        await update.message.reply_text(
            "❌ Belum ada perangkat terdaftar.\n\n"
            "Gunakan /add untuk menambah perangkat."
        )
        return
    
    message = "📋 *Daftar Perangkat:*\n\n"
    for device in devices:
        message += f"🔹 *{device.name}*\n"
        message += f"   Host: `{device.host}`\n"
        message += f"   Protocol: {device.protocol.upper()}"
        if device.port:
            message += f":{device.port}"
        message += "\n"
        if device.description:
            message += f"   📝 {device.description}\n"
        if device.location:
            message += f"   📍 {device.location}\n"
        message += "\n"
    
    message += f"Total: {len(devices)} perangkat"
    
    await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)


async def add_device_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /add command - expects multiline input"""
    if not await check_authorization(update, context):
        return
    
    if context.args:
        await update.message.reply_text(
            "⚠️ Format salah!\n\n"
            "Gunakan format multiline:\n"
            "/add\n"
            "nama: router-1\n"
            "host: 192.168.1.1\n"
            "username: admin\n"
            "password: pass123\n"
            "protocol: ssh\n"
            "port: 22 (opsional)\n"
            "description: Router utama (opsional)\n"
            "location: Kantor (opsional)"
        )
        return
    
    # Get the full message text
    text = update.message.text
    lines = text.split('\n')[1:]  # Skip the /add line
    
    if not lines:
        await update.message.reply_text(
            "ℹ️ Masukkan data perangkat:\n\n"
            "Format:\n"
            "nama: router-1\n"
            "host: 192.168.1.1\n"
            "username: admin\n"
            "password: pass123\n"
            "protocol: ssh (or telnet)\n"
            "port: 22 (opsional)\n"
            "description: Router utama (opsional)\n"
            "location: Kantor pusat (opsional)"
        )
        return
    
    # Parse the input
    data = {}
    for line in lines:
        line = line.strip()
        if ':' not in line:
            continue
        key, value = line.split(':', 1)
        data[key.strip().lower()] = value.strip()
    
    # Validate required fields
    required = ['nama', 'host', 'username', 'password']
    missing = [f for f in required if f not in data]
    
    if missing:
        await update.message.reply_text(
            f"❌ Field wajib belum lengkap: {', '.join(missing)}\n\n"
            "Field wajib: nama, host, username, password"
        )
        return
    
    # Set defaults
    protocol = data.get('protocol', 'ssh').lower()
    if protocol not in ['ssh', 'telnet']:
        await update.message.reply_text(
            "❌ Protocol harus 'ssh' atau 'telnet'"
        )
        return
    
    port = data.get('port')
    if port:
        try:
            port = int(port)
        except ValueError:
            await update.message.reply_text("❌ Port harus berupa angka")
            return
    
    # Add device
    device = db.add_device(
        name=data['nama'],
        host=data['host'],
        username=data['username'],
        password=data['password'],
        protocol=protocol,
        port=port,
        description=data.get('description'),
        location=data.get('location')
    )
    
    if device:
        message = f"✅ Perangkat berhasil ditambahkan!\n\n"
        message += f"📱 Nama: *{device.name}*\n"
        message += f"🌐 Host: `{device.host}`\n"
        message += f"🔐 Protocol: {device.protocol.upper()}"
        if device.port:
            message += f":{device.port}"
        message += "\n"
        if device.description:
            message += f"📝 Deskripsi: {device.description}\n"
        if device.location:
            message += f"📍 Lokasi: {device.location}\n"
        
        await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
    else:
        await update.message.reply_text(
            "❌ Gagal menambah perangkat!\n"
            "Perangkat dengan nama tersebut mungkin sudah ada."
        )


async def device_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show device information and cached interfaces"""
    if not await check_authorization(update, context):
        return
    
    if not context.args:
        await update.message.reply_text(
            "ℹ️ Gunakan: /device <nama_perangkat>\n\n"
            "Contoh: /device router-1"
        )
        return
    
    device_name = ' '.join(context.args)
    device = db.get_device(device_name)
    
    if not device:
        await update.message.reply_text(
            f"❌ Perangkat '{device_name}' tidak ditemukan.\n\n"
            "Gunakan /list untuk melihat daftar perangkat."
        )
        return
    
    # Build device info message
    message = f"📱 *Informasi Perangkat*\n\n"
    message += f"*Nama:* {device.name}\n"
    message += f"*Host:* `{device.host}`\n"
    message += f"*Username:* {device.username}\n"
    message += f"*Protocol:* {device.protocol.upper()}"
    if device.port:
        message += f":{device.port}"
    message += "\n"
    if device.description:
        message += f"*Deskripsi:* {device.description}\n"
    if device.location:
        message += f"*Lokasi:* {device.location}\n"
    
    # Get cached interfaces
    interfaces = db.get_device_interfaces(device_name)
    if interfaces:
        message += f"\n📊 *Cached Interfaces:* ({len(interfaces)})\n"
        for iface in interfaces[:10]:  # Limit to 10
            status_icon = "🟢" if iface.status and "up" in iface.status.lower() else "🔴"
            message += f"{status_icon} `{iface.interface_name}` - {iface.status or 'unknown'}\n"
        
        if len(interfaces) > 10:
            message += f"\n_...dan {len(interfaces) - 10} interface lainnya_"
    else:
        message += "\nℹ️ Belum ada interface yang di-cache."
    
    await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)


async def check_interface(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Check interface status - main command"""
    if not await check_authorization(update, context):
        return
    
    if len(context.args) < 2:
        await update.message.reply_text(
            "ℹ️ Gunakan: /cek <device> <interface>\n\n"
            "Contoh: /cek router-1 GigabitEthernet0/0\n"
            "atau: /cek router-1 Gi0/0"
        )
        return
    
    device_name = context.args[0]
    interface_name = ' '.join(context.args[1:])
    
    # Get device from database
    device = db.get_device(device_name)
    if not device:
        await update.message.reply_text(
            f"❌ Perangkat '{device_name}' tidak ditemukan.\n\n"
            "Gunakan /list untuk melihat daftar perangkat."
        )
        return
    
    # Send checking message
    checking_msg = await update.message.reply_text(
        f"🔍 Mengecek interface {interface_name} di {device_name}...\n"
        "⏳ Mohon tunggu..."
    )
    
    try:
        # Create connection config
        config = ConnectionConfig(
            host=device.host,
            username=device.username,
            password=device.password,
            protocol=Protocol.SSH if device.protocol == 'ssh' else Protocol.TELNET,
            port=device.port
        )
        
        # Connect and get interface info
        with BotLinkMaster(config) as bot:
            if not bot.connected:
                await checking_msg.edit_text(
                    f"❌ Gagal koneksi ke {device_name}!\n\n"
                    "Periksa:\n"
                    "• Host dan port benar\n"
                    "• Kredensial valid\n"
                    "• Device dapat dijangkau"
                )
                return
            
            # Get specific interface
            interface_info = bot.get_specific_interface(interface_name)
            
            if not interface_info:
                await checking_msg.edit_text(
                    f"❌ Interface '{interface_name}' tidak ditemukan di {device_name}!\n\n"
                    "Periksa nama interface dengan benar."
                )
                return
            
            # Cache the interface
            db.cache_interface(
                device_name=device_name,
                interface_name=interface_name,
                status=interface_info.get('status'),
                protocol_status=interface_info.get('status'),
                description=interface_info.get('description')
            )
            
            # Build response message
            status = interface_info.get('status', 'unknown')
            status_icon = "🟢" if status and "up" in status.lower() else "🔴"
            
            message = f"{status_icon} *Interface Status*\n\n"
            message += f"*Device:* {device_name}\n"
            message += f"*Interface:* `{interface_name}`\n"
            message += f"*Status:* {status.upper()}\n"
            
            if 'description' in interface_info and interface_info['description']:
                message += f"*Description:* {interface_info['description']}\n"
            
            if 'ip_address' in interface_info:
                message += f"*IP Address:* `{interface_info['ip_address']}`\n"
            
            if 'mac_address' in interface_info:
                message += f"*MAC Address:* `{interface_info['mac_address']}`\n"
            
            message += f"\n✅ Interface dicek pada {update.message.date.strftime('%Y-%m-%d %H:%M:%S')}"
            
            await checking_msg.edit_text(message, parse_mode=ParseMode.MARKDOWN)
            
    except Exception as e:
        logger.error(f"Error checking interface: {str(e)}")
        await checking_msg.edit_text(
            f"❌ Error saat mengecek interface!\n\n"
            f"Error: {str(e)}"
        )


async def delete_device(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Delete a device"""
    if not await check_authorization(update, context):
        return
    
    if not context.args:
        await update.message.reply_text(
            "ℹ️ Gunakan: /delete <nama_perangkat>\n\n"
            "Contoh: /delete router-1"
        )
        return
    
    device_name = ' '.join(context.args)
    device = db.get_device(device_name)
    
    if not device:
        await update.message.reply_text(
            f"❌ Perangkat '{device_name}' tidak ditemukan."
        )
        return
    
    # Delete device
    if db.delete_device(device_name):
        await update.message.reply_text(
            f"✅ Perangkat '{device_name}' berhasil dihapus!\n\n"
            "Cache interface juga telah dihapus."
        )
    else:
        await update.message.reply_text(
            f"❌ Gagal menghapus perangkat '{device_name}'."
        )


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Log errors caused by Updates"""
    logger.error(f"Update {update} caused error {context.error}")


def main():
    """Start the bot"""
    # Get bot token from environment
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    
    if not token:
        logger.error("TELEGRAM_BOT_TOKEN not found in environment!")
        print("\n❌ ERROR: TELEGRAM_BOT_TOKEN tidak ditemukan!")
        print("\nPastikan:")
        print("1. File .env ada di directory yang sama")
        print("2. File .env berisi: TELEGRAM_BOT_TOKEN=your_token")
        print("3. Tidak ada spasi sebelum/sesudah =")
        print("\nContoh isi .env:")
        print("TELEGRAM_BOT_TOKEN=123456:ABCdefGHIjklMNOpqrsTUVwxyz")
        print("\nDapatkan token dari @BotFather di Telegram")
        print("\n🔧 Run diagnostic: python diagnose.py")
        return
    
    logger.info("Starting BotLinkMaster Telegram Bot...")
    logger.info(f"Token: {token[:10]}... (length: {len(token)})")
    
    # Verify token format
    if ':' not in token:
        logger.error("Invalid token format!")
        print("\n❌ ERROR: Token format tidak valid!")
        print("Token harus seperti: 123456789:ABCdefGHIjklMNOpqrsTUVwxyz")
        print("\n🔧 Run diagnostic: python diagnose.py")
        return
    
    # Create application
    try:
        application = Application.builder().token(token).build()
        logger.info("Application created successfully")
    except Exception as e:
        logger.error(f"Failed to create application: {e}")
        print(f"\n❌ ERROR: Gagal membuat application!")
        print(f"Error: {e}")
        print("\n🔧 Run diagnostic: python diagnose.py")
        return
    
    # Register command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("myid", myid_command))
    application.add_handler(CommandHandler("list", list_devices))
    application.add_handler(CommandHandler("add", add_device_command))
    application.add_handler(CommandHandler("device", device_info))
    application.add_handler(CommandHandler("cek", check_interface))
    application.add_handler(CommandHandler("delete", delete_device))
    logger.info("Command handlers registered")
    
    # Register error handler
    application.add_error_handler(error_handler)
    
    # Start the bot
    logger.info("Bot started successfully! Press Ctrl+C to stop.")
    print("\n✅ Bot started successfully!")
    print("📱 Buka Telegram dan mulai chat dengan bot Anda")
    print("⌨️  Ketik /start untuk memulai")
    
    if ALLOWED_CHAT_IDS:
        print(f"\n🔒 Access restriction enabled for {len(ALLOWED_CHAT_IDS)} chat ID(s)")
        logger.info(f"Access restricted to: {ALLOWED_CHAT_IDS}")
    else:
        print("\n⚠️  No access restriction (all users can use the bot)")
        logger.info("No access restriction - all users allowed")
    
    print("\n[Press Ctrl+C to stop]\n")
    print("📋 Troubleshooting:")
    print("   - If bot doesn't respond, check: tail -f botlinkmaster.log")
    print("   - Run diagnostic: python diagnose.py")
    print("   - Test basic bot: python test_bot.py")
    print()
    
    try:
        application.run_polling(allowed_updates=Update.ALL_TYPES)
    except Exception as e:
        logger.error(f"Error during polling: {e}")
        print(f"\n❌ ERROR: {e}")
        print("\n🔧 Run diagnostic: python diagnose.py")


if __name__ == '__main__':
    main()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /start is issued"""
    welcome_message = """
🤖 *BotLinkMaster v4\.0*

Selamat datang\! Bot ini membantu Anda memonitor perangkat jaringan\.

📋 *Perintah yang tersedia:*
/start \- Tampilkan pesan ini
/help \- Bantuan lengkap
/list \- Daftar semua perangkat
/add \- Tambah perangkat baru
/device <nama> \- Info detail perangkat
/cek <device> <interface> \- Cek status interface
/delete <nama> \- Hapus perangkat

Gunakan /help untuk panduan lengkap\.
"""
    await update.message.reply_text(
        welcome_message,
        parse_mode=ParseMode.MARKDOWN_V2
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send help message"""
    help_text = """
📖 *Bantuan BotLinkMaster*

*1\. Menambah Perangkat \(/add\)*
Format multiline:
```
/add
nama: router\-1
host: 192\.168\.1\.1
username: admin
password: password123
protocol: ssh
port: 22
description: Router utama
location: Kantor pusat
```

*2\. Cek Interface \(/cek\)*
```
/cek router\-1 GigabitEthernet0/0
```

*3\. List Perangkat \(/list\)*
```
/list
```

*4\. Detail Perangkat \(/device\)*
```
/device router\-1
```

*5\. Hapus Perangkat \(/delete\)*
```
/delete router\-1
```

*Catatan:*
• Protocol: ssh atau telnet
• Port opsional \(default SSH:22, Telnet:23\)
• Description dan location opsional
"""
    await update.message.reply_text(
        help_text,
        parse_mode=ParseMode.MARKDOWN_V2
    )


async def list_devices(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """List all registered devices"""
    devices = db.get_all_devices()
    
    if not devices:
        await update.message.reply_text(
            "❌ Belum ada perangkat terdaftar.\n\n"
            "Gunakan /add untuk menambah perangkat."
        )
        return
    
    message = "📋 *Daftar Perangkat:*\n\n"
    for device in devices:
        message += f"🔹 *{device.name}*\n"
        message += f"   Host: `{device.host}`\n"
        message += f"   Protocol: {device.protocol.upper()}"
        if device.port:
            message += f":{device.port}"
        message += "\n"
        if device.description:
            message += f"   📝 {device.description}\n"
        if device.location:
            message += f"   📍 {device.location}\n"
        message += "\n"
    
    message += f"Total: {len(devices)} perangkat"
    
    await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)


async def add_device_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /add command - expects multiline input"""
    if context.args:
        await update.message.reply_text(
            "⚠️ Format salah!\n\n"
            "Gunakan format multiline:\n"
            "/add\n"
            "nama: router-1\n"
            "host: 192.168.1.1\n"
            "username: admin\n"
            "password: pass123\n"
            "protocol: ssh\n"
            "port: 22 (opsional)\n"
            "description: Router utama (opsional)\n"
            "location: Kantor (opsional)"
        )
        return
    
    # Get the full message text
    text = update.message.text
    lines = text.split('\n')[1:]  # Skip the /add line
    
    if not lines:
        await update.message.reply_text(
            "ℹ️ Masukkan data perangkat:\n\n"
            "Format:\n"
            "nama: router-1\n"
            "host: 192.168.1.1\n"
            "username: admin\n"
            "password: pass123\n"
            "protocol: ssh (or telnet)\n"
            "port: 22 (opsional)\n"
            "description: Router utama (opsional)\n"
            "location: Kantor pusat (opsional)"
        )
        return
    
    # Parse the input
    data = {}
    for line in lines:
        line = line.strip()
        if ':' not in line:
            continue
        key, value = line.split(':', 1)
        data[key.strip().lower()] = value.strip()
    
    # Validate required fields
    required = ['nama', 'host', 'username', 'password']
    missing = [f for f in required if f not in data]
    
    if missing:
        await update.message.reply_text(
            f"❌ Field wajib belum lengkap: {', '.join(missing)}\n\n"
            "Field wajib: nama, host, username, password"
        )
        return
    
    # Set defaults
    protocol = data.get('protocol', 'ssh').lower()
    if protocol not in ['ssh', 'telnet']:
        await update.message.reply_text(
            "❌ Protocol harus 'ssh' atau 'telnet'"
        )
        return
    
    port = data.get('port')
    if port:
        try:
            port = int(port)
        except ValueError:
            await update.message.reply_text("❌ Port harus berupa angka")
            return
    
    # Add device
    device = db.add_device(
        name=data['nama'],
        host=data['host'],
        username=data['username'],
        password=data['password'],
        protocol=protocol,
        port=port,
        description=data.get('description'),
        location=data.get('location')
    )
    
    if device:
        message = f"✅ Perangkat berhasil ditambahkan!\n\n"
        message += f"📱 Nama: *{device.name}*\n"
        message += f"🌐 Host: `{device.host}`\n"
        message += f"🔐 Protocol: {device.protocol.upper()}"
        if device.port:
            message += f":{device.port}"
        message += "\n"
        if device.description:
            message += f"📝 Deskripsi: {device.description}\n"
        if device.location:
            message += f"📍 Lokasi: {device.location}\n"
        
        await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
    else:
        await update.message.reply_text(
            "❌ Gagal menambah perangkat!\n"
            "Perangkat dengan nama tersebut mungkin sudah ada."
        )


async def device_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show device information and cached interfaces"""
    if not context.args:
        await update.message.reply_text(
            "ℹ️ Gunakan: /device <nama_perangkat>\n\n"
            "Contoh: /device router-1"
        )
        return
    
    device_name = ' '.join(context.args)
    device = db.get_device(device_name)
    
    if not device:
        await update.message.reply_text(
            f"❌ Perangkat '{device_name}' tidak ditemukan.\n\n"
            "Gunakan /list untuk melihat daftar perangkat."
        )
        return
    
    # Build device info message
    message = f"📱 *Informasi Perangkat*\n\n"
    message += f"*Nama:* {device.name}\n"
    message += f"*Host:* `{device.host}`\n"
    message += f"*Username:* {device.username}\n"
    message += f"*Protocol:* {device.protocol.upper()}"
    if device.port:
        message += f":{device.port}"
    message += "\n"
    if device.description:
        message += f"*Deskripsi:* {device.description}\n"
    if device.location:
        message += f"*Lokasi:* {device.location}\n"
    
    # Get cached interfaces
    interfaces = db.get_device_interfaces(device_name)
    if interfaces:
        message += f"\n📊 *Cached Interfaces:* ({len(interfaces)})\n"
        for iface in interfaces[:10]:  # Limit to 10
            status_icon = "🟢" if iface.status and "up" in iface.status.lower() else "🔴"
            message += f"{status_icon} `{iface.interface_name}` - {iface.status or 'unknown'}\n"
        
        if len(interfaces) > 10:
            message += f"\n_...dan {len(interfaces) - 10} interface lainnya_"
    else:
        message += "\nℹ️ Belum ada interface yang di-cache."
    
    await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)


async def check_interface(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Check interface status - main command"""
    if len(context.args) < 2:
        await update.message.reply_text(
            "ℹ️ Gunakan: /cek <device> <interface>\n\n"
            "Contoh: /cek router-1 GigabitEthernet0/0\n"
            "atau: /cek router-1 Gi0/0"
        )
        return
    
    device_name = context.args[0]
    interface_name = ' '.join(context.args[1:])
    
    # Get device from database
    device = db.get_device(device_name)
    if not device:
        await update.message.reply_text(
            f"❌ Perangkat '{device_name}' tidak ditemukan.\n\n"
            "Gunakan /list untuk melihat daftar perangkat."
        )
        return
    
    # Send checking message
    checking_msg = await update.message.reply_text(
        f"🔍 Mengecek interface {interface_name} di {device_name}...\n"
        "⏳ Mohon tunggu..."
    )
    
    try:
        # Create connection config
        config = ConnectionConfig(
            host=device.host,
            username=device.username,
            password=device.password,
            protocol=Protocol.SSH if device.protocol == 'ssh' else Protocol.TELNET,
            port=device.port
        )
        
        # Connect and get interface info
        with BotLinkMaster(config) as bot:
            if not bot.connected:
                await checking_msg.edit_text(
                    f"❌ Gagal koneksi ke {device_name}!\n\n"
                    "Periksa:\n"
                    "• Host dan port benar\n"
                    "• Kredensial valid\n"
                    "• Device dapat dijangkau"
                )
                return
            
            # Get specific interface
            interface_info = bot.get_specific_interface(interface_name)
            
            if not interface_info:
                await checking_msg.edit_text(
                    f"❌ Interface '{interface_name}' tidak ditemukan di {device_name}!\n\n"
                    "Periksa nama interface dengan benar."
                )
                return
            
            # Cache the interface
            db.cache_interface(
                device_name=device_name,
                interface_name=interface_name,
                status=interface_info.get('status'),
                protocol_status=interface_info.get('status'),
                description=interface_info.get('description')
            )
            
            # Build response message
            status = interface_info.get('status', 'unknown')
            status_icon = "🟢" if status and "up" in status.lower() else "🔴"
            
            message = f"{status_icon} *Interface Status*\n\n"
            message += f"*Device:* {device_name}\n"
            message += f"*Interface:* `{interface_name}`\n"
            message += f"*Status:* {status.upper()}\n"
            
            if 'description' in interface_info and interface_info['description']:
                message += f"*Description:* {interface_info['description']}\n"
            
            if 'ip_address' in interface_info:
                message += f"*IP Address:* `{interface_info['ip_address']}`\n"
            
            if 'mac_address' in interface_info:
                message += f"*MAC Address:* `{interface_info['mac_address']}`\n"
            
            message += f"\n✅ Interface dicek pada {update.message.date.strftime('%Y-%m-%d %H:%M:%S')}"
            
            await checking_msg.edit_text(message, parse_mode=ParseMode.MARKDOWN)
            
    except Exception as e:
        logger.error(f"Error checking interface: {str(e)}")
        await checking_msg.edit_text(
            f"❌ Error saat mengecek interface!\n\n"
            f"Error: {str(e)}"
        )


async def delete_device(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Delete a device"""
    if not context.args:
        await update.message.reply_text(
            "ℹ️ Gunakan: /delete <nama_perangkat>\n\n"
            "Contoh: /delete router-1"
        )
        return
    
    device_name = ' '.join(context.args)
    device = db.get_device(device_name)
    
    if not device:
        await update.message.reply_text(
            f"❌ Perangkat '{device_name}' tidak ditemukan."
        )
        return
    
    # Delete device
    if db.delete_device(device_name):
        await update.message.reply_text(
            f"✅ Perangkat '{device_name}' berhasil dihapus!\n\n"
            "Cache interface juga telah dihapus."
        )
    else:
        await update.message.reply_text(
            f"❌ Gagal menghapus perangkat '{device_name}'."
        )


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Log errors caused by Updates"""
    logger.error(f"Update {update} caused error {context.error}")


def main():
    """Start the bot"""
    # Get bot token from environment
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    
    if not token:
        logger.error("TELEGRAM_BOT_TOKEN not found in environment!")
        print("\n❌ ERROR: TELEGRAM_BOT_TOKEN tidak ditemukan!")
        print("\nSet token dengan salah satu cara:")
        print("1. Export: export TELEGRAM_BOT_TOKEN='your_token'")
        print("2. File .env: TELEGRAM_BOT_TOKEN=your_token")
        print("\nDapatkan token dari @BotFather di Telegram")
        return
    
    logger.info("Starting BotLinkMaster Telegram Bot...")
    
    # Create application
    application = Application.builder().token(token).build()
    
    # Register command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("list", list_devices))
    application.add_handler(CommandHandler("add", add_device_command))
    application.add_handler(CommandHandler("device", device_info))
    application.add_handler(CommandHandler("cek", check_interface))
    application.add_handler(CommandHandler("delete", delete_device))
    
    # Register error handler
    application.add_error_handler(error_handler)
    
    # Start the bot
    logger.info("Bot started successfully! Press Ctrl+C to stop.")
    print("\n✅ Bot started successfully!")
    print("📱 Buka Telegram dan mulai chat dengan bot Anda")
    print("⌨️  Ketik /start untuk memulai")
    print("\n[Press Ctrl+C to stop]\n")
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
