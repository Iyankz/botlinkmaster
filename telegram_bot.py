#!/usr/bin/env python3
"""
BotLinkMaster v4.6.0 - Telegram Bot
Network device monitoring with multi-vendor optical power support

Note: OLT support will be available in v5.0.0

Author: BotLinkMaster
Version: 4.6.0
"""

import os
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

from botlinkmaster import BotLinkMaster, ConnectionConfig, Protocol
from database import DatabaseManager
from vendor_commands import get_supported_vendors, get_vendor_config
from timezone_config import (
    tz_manager, get_timezone_examples_text, get_timezone_by_continent,
    validate_timezone, get_current_time
)

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('botlinkmaster.log'), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

db = DatabaseManager()

ALLOWED_CHAT_IDS = []
env_ids = os.getenv('ALLOWED_CHAT_IDS', '')
if env_ids:
    for cid in env_ids.split(','):
        cid = cid.strip()
        if cid:
            try:
                ALLOWED_CHAT_IDS.append(int(cid))
            except ValueError:
                pass


def is_authorized(chat_id: int) -> bool:
    if not ALLOWED_CHAT_IDS and not db.get_allowed_users():
        return True
    if chat_id in ALLOWED_CHAT_IDS:
        return True
    if db.is_user_allowed(chat_id):
        return True
    return False


async def check_auth(update: Update) -> bool:
    chat_id = update.effective_chat.id
    if not is_authorized(chat_id):
        await update.message.reply_text(
            f"⛔ Akses Ditolak\n\n"
            f"Chat ID: {chat_id}\n"
            f"Hubungi admin untuk akses."
        )
        return False
    return True


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_auth(update):
        return
    
    await update.message.reply_text(
        f"🤖 BotLinkMaster v4.6.0\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"Bot monitoring perangkat jaringan.\n"
        f"Support 18 vendor router & switch.\n\n"
        f"⏰ {tz_manager.get_current_time()}\n"
        f"🌍 {tz_manager.get_timezone()}\n\n"
        f"Ketik /help untuk bantuan."
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_auth(update):
        return
    
    await update.message.reply_text(
        "🔧 BANTUAN BOTLINKMASTER v4.6.0\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "📋 INFO:\n"
        "/start - Info bot\n"
        "/help - Bantuan ini\n"
        "/help2 - Contoh penggunaan\n"
        "/myid - Chat ID Anda\n"
        "/time - Waktu saat ini\n\n"
        "📦 DEVICE:\n"
        "/add - Tambah perangkat\n"
        "/list - Daftar perangkat\n"
        "/device [nama] - Detail\n"
        "/delete [nama] - Hapus\n\n"
        "📡 MONITORING:\n"
        "/interfaces [device] - List interface\n"
        "/interfaces [device] [page] - Halaman\n"
        "/cek [device] [interface] - Status\n"
        "/redaman [device] [interface] - Optical\n\n"
        "⚙️ CONFIG:\n"
        "/vendors - Daftar vendor\n"
        "/timezone - Info timezone\n"
        "/settz [tz] - Set timezone"
    )


async def help2_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_auth(update):
        return
    
    await update.message.reply_text(
        "📖 CONTOH PENGGUNAAN\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "1️⃣ TAMBAH DEVICE:\n"
        "/add\n"
        "nama: router-1\n"
        "host: 192.168.1.1\n"
        "username: admin\n"
        "password: admin123\n"
        "protocol: ssh\n"
        "port: 22\n"
        "vendor: cisco_ios\n\n"
        "2️⃣ CEK INTERFACE:\n"
        "/cek router-1 Gi0/0\n\n"
        "3️⃣ CEK REDAMAN:\n"
        "/redaman router-1 Gi0/0\n\n"
        "4️⃣ LIST INTERFACE:\n"
        "/interfaces router-1\n"
        "/interfaces router-1 2"
    )


async def myid_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    await update.message.reply_text(
        f"📋 INFO CHAT\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🆔 Chat ID: {chat_id}\n"
        f"📱 Type: {update.effective_chat.type}\n"
        f"👤 Username: @{update.effective_user.username or 'N/A'}\n\n"
        f"Tambahkan ke ALLOWED_CHAT_IDS di .env"
    )


async def time_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_auth(update):
        return
    await update.message.reply_text(
        f"⏰ {tz_manager.get_current_time()}\n"
        f"🌍 {tz_manager.get_timezone()}"
    )


async def timezone_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_auth(update):
        return
    if context.args:
        text = get_timezone_by_continent(context.args[0])
    else:
        text = get_timezone_examples_text()
    await update.message.reply_text(text)


async def settz_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_auth(update):
        return
    
    if not context.args:
        await update.message.reply_text(
            "Gunakan: /settz [timezone]\n"
            "Contoh: /settz Asia/Jakarta\n\n"
            "Ketik /timezone untuk daftar"
        )
        return
    
    new_tz = context.args[0]
    if not validate_timezone(new_tz):
        await update.message.reply_text(f"❌ Timezone '{new_tz}' tidak valid")
        return
    
    if tz_manager.save_timezone(new_tz):
        await update.message.reply_text(
            f"✅ Timezone: {new_tz}\n"
            f"⏰ {get_current_time(new_tz)}"
        )


async def vendors_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_auth(update):
        return
    
    await update.message.reply_text(
        "📦 VENDOR YANG DIDUKUNG\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "cisco_ios     - Cisco IOS/IOS-XE\n"
        "cisco_nxos    - Cisco NX-OS\n"
        "huawei        - Huawei VRP\n"
        "zte           - ZTE Router/Switch\n"
        "juniper       - Juniper JunOS\n"
        "mikrotik      - MikroTik RouterOS\n"
        "nokia         - Nokia SR-OS\n"
        "hp_aruba      - HP/Aruba\n"
        "h3c           - H3C Comware\n"
        "ruijie        - Ruijie\n"
        "fiberhome     - FiberHome\n"
        "dcn           - DCN\n"
        "bdcom         - BDCOM\n"
        "raisecom      - Raisecom\n"
        "fs            - FS.COM\n"
        "allied        - Allied Telesis\n"
        "datacom       - Datacom\n"
        "generic       - Generic\n\n"
        "📌 OLT support: v5.0.0"
    )


async def list_devices(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_auth(update):
        return
    
    devices = db.get_all_devices()
    if not devices:
        await update.message.reply_text("📭 Belum ada perangkat. Gunakan /add")
        return
    
    msg = "📦 DAFTAR PERANGKAT\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    for d in devices:
        port = d.port or (22 if d.protocol == 'ssh' else 23)
        msg += f"🔹 {d.name}\n"
        msg += f"   {d.host}:{port} ({d.protocol.upper()})\n"
        msg += f"   Vendor: {d.vendor or 'generic'}\n\n"
    
    msg += f"📊 Total: {len(devices)} perangkat"
    await update.message.reply_text(msg)


async def add_device_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_auth(update):
        return
    
    text = update.message.text
    lines = text.split('\n')[1:]
    
    if not lines:
        await update.message.reply_text(
            "➕ TAMBAH PERANGKAT\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "Format:\n"
            "/add\n"
            "nama: router-1\n"
            "host: 192.168.1.1\n"
            "username: admin\n"
            "password: pass123\n"
            "protocol: ssh\n"
            "port: 22\n"
            "vendor: cisco_ios\n"
            "description: Router utama\n\n"
            "📌 Wajib: nama, host, username, password\n"
            "📌 Protocol: ssh atau telnet\n\n"
            "Ketik /vendors untuk daftar vendor"
        )
        return
    
    data = {}
    for line in lines:
        if ':' in line:
            key, value = line.split(':', 1)
            data[key.strip().lower()] = value.strip()
    
    required = ['nama', 'host', 'username', 'password']
    missing = [f for f in required if f not in data]
    if missing:
        await update.message.reply_text(f"❌ Field belum lengkap: {', '.join(missing)}")
        return
    
    protocol = data.get('protocol', 'ssh').lower()
    if protocol not in ['ssh', 'telnet']:
        await update.message.reply_text("❌ Protocol harus 'ssh' atau 'telnet'")
        return
    
    port = data.get('port')
    try:
        port = int(port) if port else (22 if protocol == 'ssh' else 23)
    except ValueError:
        await update.message.reply_text("❌ Port harus angka")
        return
    
    device = db.add_device(
        name=data['nama'],
        host=data['host'],
        username=data['username'],
        password=data['password'],
        protocol=protocol,
        port=port,
        description=data.get('description'),
        vendor=data.get('vendor', 'generic').lower()
    )
    
    if device:
        await update.message.reply_text(
            f"✅ Perangkat ditambahkan!\n\n"
            f"📛 Nama: {device.name}\n"
            f"🌐 Host: {device.host}:{device.port}\n"
            f"📦 Vendor: {device.vendor}"
        )
    else:
        await update.message.reply_text("❌ Gagal. Nama mungkin sudah ada.")


async def device_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_auth(update):
        return
    
    if not context.args:
        await update.message.reply_text("Gunakan: /device [nama]")
        return
    
    device = db.get_device(' '.join(context.args))
    if not device:
        await update.message.reply_text("❌ Perangkat tidak ditemukan")
        return
    
    cfg = get_vendor_config(device.vendor or 'generic')
    await update.message.reply_text(
        f"📦 {device.name}\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🌐 Host: {device.host}:{device.port}\n"
        f"🔌 Protocol: {device.protocol.upper()}\n"
        f"📦 Vendor: {device.vendor} ({cfg.name})\n"
        f"📝 {device.description or '-'}"
    )


async def delete_device(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_auth(update):
        return
    
    if not context.args:
        await update.message.reply_text("Gunakan: /delete [nama]")
        return
    
    name = ' '.join(context.args)
    if db.delete_device(name):
        await update.message.reply_text(f"✅ '{name}' dihapus")
    else:
        await update.message.reply_text(f"❌ '{name}' tidak ditemukan")


async def list_interfaces(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_auth(update):
        return
    
    if not context.args:
        await update.message.reply_text(
            "📡 LIST INTERFACE\n\n"
            "Gunakan: /interfaces [device]\n"
            "Atau: /interfaces [device] [page]\n\n"
            "Contoh:\n"
            "/interfaces router-1\n"
            "/interfaces router-1 2"
        )
        return
    
    device_name = context.args[0]
    page = 1
    if len(context.args) >= 2:
        try:
            page = max(1, int(context.args[1]))
        except ValueError:
            page = 1
    
    device = db.get_device(device_name)
    if not device:
        await update.message.reply_text(f"❌ '{device_name}' tidak ditemukan")
        return
    
    msg = await update.message.reply_text(f"⏳ Mengambil interface dari {device_name}...")
    
    try:
        config = ConnectionConfig(
            host=device.host,
            username=device.username,
            password=device.password,
            protocol=Protocol.SSH if device.protocol == 'ssh' else Protocol.TELNET,
            port=device.port,
            vendor=device.vendor or 'generic'
        )
        
        with BotLinkMaster(config) as bot:
            if not bot.connected:
                await msg.edit_text(f"❌ Gagal koneksi ke {device_name}")
                return
            
            interfaces = bot.get_interfaces()
            
            if not interfaces:
                await msg.edit_text(
                    f"❌ Tidak dapat mengambil interface.\n"
                    f"Coba /cek untuk interface spesifik."
                )
                return
            
            per_page = 20
            total = len(interfaces)
            total_pages = (total + per_page - 1) // per_page
            page = min(page, total_pages)
            
            start = (page - 1) * per_page
            end = min(start + per_page, total)
            
            up_count = sum(1 for i in interfaces if i['status'] == 'up')
            down_count = sum(1 for i in interfaces if i['status'] == 'down')
            
            text = f"📡 INTERFACE {device_name}\n"
            text += "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            text += f"📊 Total: {total} | 🟢 Up: {up_count} | 🔴 Down: {down_count}\n"
            text += f"📄 Halaman {page}/{total_pages}\n"
            text += "━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            
            for iface in interfaces[start:end]:
                status = iface['status']
                flags = iface.get('flags', '')
                icon = "🟢" if status == 'up' else "🔴" if status == 'down' else "⚪"
                
                if flags:
                    text += f"{icon} {iface['name']} [{flags}]\n"
                else:
                    text += f"{icon} {iface['name']}\n"
                
                if iface.get('description'):
                    desc = iface['description'][:30]
                    text += f"   {desc}\n"
            
            if total_pages > 1:
                text += f"\n📄 Halaman lain: /interfaces {device_name} [1-{total_pages}]"
            
            await msg.edit_text(text)
            
    except Exception as e:
        logger.error(f"Error: {e}")
        await msg.edit_text(f"❌ Error: {str(e)}")


async def check_interface(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_auth(update):
        return
    
    if len(context.args) < 2:
        await update.message.reply_text(
            "📡 CEK STATUS\n\n"
            "Gunakan: /cek [device] [interface]\n\n"
            "Contoh:\n"
            "/cek router-1 Gi0/0\n"
            "/cek SW-MIKROTIK sfp-sfpplus1"
        )
        return
    
    device_name = context.args[0]
    interface_name = ' '.join(context.args[1:])
    
    device = db.get_device(device_name)
    if not device:
        await update.message.reply_text(f"❌ '{device_name}' tidak ditemukan")
        return
    
    msg = await update.message.reply_text(f"⏳ Mengecek {interface_name}...")
    
    try:
        config = ConnectionConfig(
            host=device.host,
            username=device.username,
            password=device.password,
            protocol=Protocol.SSH if device.protocol == 'ssh' else Protocol.TELNET,
            port=device.port,
            vendor=device.vendor or 'generic'
        )
        
        with BotLinkMaster(config) as bot:
            if not bot.connected:
                await msg.edit_text(f"❌ Gagal koneksi ke {device_name}")
                return
            
            info = bot.get_interface_status(interface_name)
            status = info.get('status', 'unknown')
            flags = info.get('flags', '')
            icon = "🟢 UP" if status == 'up' else "🔴 DOWN" if status == 'down' else "⚪ UNKNOWN"
            
            text = f"📡 STATUS INTERFACE\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            text += f"📦 Device: {device_name}\n"
            text += f"🔌 Interface: {interface_name}\n"
            text += f"📶 Status: {icon}\n"
            if flags:
                text += f"🏷️ Flags: {flags}\n"
            if info.get('description'):
                text += f"📝 {info['description']}\n"
            text += f"\n💡 /redaman {device_name} {interface_name}"
            
            await msg.edit_text(text)
            
    except Exception as e:
        logger.error(f"Error: {e}")
        await msg.edit_text(f"❌ Error: {str(e)}")


async def check_optical(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_auth(update):
        return
    
    if len(context.args) < 2:
        await update.message.reply_text(
            "🔍 CEK OPTICAL / REDAMAN\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "Gunakan: /redaman [device] [interface]\n\n"
            "Contoh:\n"
            "/redaman router-1 Gi0/0\n"
            "/redaman SW-MIKROTIK sfp-sfpplus1"
        )
        return
    
    device_name = context.args[0]
    interface_name = ' '.join(context.args[1:])
    
    device = db.get_device(device_name)
    if not device:
        await update.message.reply_text(f"❌ '{device_name}' tidak ditemukan")
        return
    
    vendor = device.vendor or 'generic'
    vendor_cfg = get_vendor_config(vendor)
    
    msg = await update.message.reply_text(
        f"⏳ Mengecek optical...\n\n"
        f"📦 {device_name} ({vendor_cfg.name})\n"
        f"🔌 {interface_name}"
    )
    
    try:
        config = ConnectionConfig(
            host=device.host,
            username=device.username,
            password=device.password,
            protocol=Protocol.SSH if device.protocol == 'ssh' else Protocol.TELNET,
            port=device.port,
            vendor=vendor
        )
        
        with BotLinkMaster(config) as bot:
            if not bot.connected:
                await msg.edit_text(
                    f"❌ GAGAL KONEKSI\n\n"
                    f"📦 {device_name}\n"
                    f"🌐 {device.host}:{device.port}"
                )
                return
            
            optical = bot.check_interface_with_optical(interface_name)
            
            status = optical.get('status', 'unknown')
            flags = optical.get('flags', '')
            description = optical.get('description', '')
            link_icon = "🟢 UP" if status == 'up' else "🔴 DOWN" if status == 'down' else "⚪ UNKNOWN"
            
            signal = optical.get('optical_status', 'unknown')
            signal_map = {
                'excellent': '🟢 EXCELLENT',
                'good': '🟢 GOOD',
                'fair': '🟡 FAIR',
                'weak': '🟠 WEAK',
                'very_weak': '🔴 VERY WEAK',
                'critical': '🔴 CRITICAL',
            }
            signal_icon = signal_map.get(signal, '⚪ UNKNOWN')
            
            text = f"🔍 OPTICAL POWER\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            text += f"📦 {device_name} ({vendor_cfg.name})\n"
            text += f"🔌 {interface_name}\n"
            if description:
                text += f"📝 {description}\n"
            text += f"📶 Link: {link_icon}\n"
            if flags:
                text += f"🏷️ Flags: {flags}\n"
            text += "\n"
            
            text += f"📊 OPTICAL:\n"
            text += f"   TX Power: {optical.get('tx_power_dbm', 'N/A')}\n"
            text += f"   RX Power: {optical.get('rx_power_dbm', 'N/A')}\n"
            text += f"   Signal: {signal_icon}\n\n"
            
            text += f"📋 REFERENSI:\n"
            text += f"   Excellent: > -8 dBm\n"
            text += f"   Good: -8 to -14 dBm\n"
            text += f"   Fair: -14 to -20 dBm\n"
            text += f"   Weak: -20 to -25 dBm\n"
            text += f"   Critical: < -25 dBm\n"
            
            if not optical.get('found'):
                text += f"\n⚠️ Data optical tidak ditemukan.\n"
                text += f"Pastikan interface memiliki SFP.\n"
            
            await msg.edit_text(text)
            
    except Exception as e:
        logger.error(f"Error: {e}")
        await msg.edit_text(f"❌ Error: {str(e)}")


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Error: {context.error}")


def main():
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not token:
        print("ERROR: TELEGRAM_BOT_TOKEN tidak ditemukan di .env")
        return
    
    logger.info("Starting BotLinkMaster v4.6.0...")
    
    app = Application.builder().token(token).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("help2", help2_command))
    app.add_handler(CommandHandler("myid", myid_command))
    app.add_handler(CommandHandler("time", time_command))
    app.add_handler(CommandHandler("timezone", timezone_command))
    app.add_handler(CommandHandler("settz", settz_command))
    app.add_handler(CommandHandler("vendors", vendors_command))
    app.add_handler(CommandHandler("list", list_devices))
    app.add_handler(CommandHandler("add", add_device_command))
    app.add_handler(CommandHandler("device", device_info))
    app.add_handler(CommandHandler("delete", delete_device))
    app.add_handler(CommandHandler("interfaces", list_interfaces))
    app.add_handler(CommandHandler("cek", check_interface))
    app.add_handler(CommandHandler("redaman", check_optical))
    app.add_handler(CommandHandler("optical", check_optical))
    
    app.add_error_handler(error_handler)
    
    print("\n" + "=" * 50)
    print("BotLinkMaster v4.6.0 Started!")
    print("=" * 50)
    print(f"\nTimezone: {tz_manager.get_timezone()}")
    print(f"Time: {tz_manager.get_current_time()}")
    print("\nNote: OLT support will be available in v5.0.0")
    print("\n[Press Ctrl+C to stop]\n")
    
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()