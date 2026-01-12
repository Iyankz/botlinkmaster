#!/usr/bin/env python3
"""
BotLinkMaster v4.2 - Telegram Bot
Network device monitoring with multi-vendor optical power support

Author: BotLinkMaster
Version: 4.2
"""

import os
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

from botlinkmaster import BotLinkMaster, ConnectionConfig, Protocol
from database import DatabaseManager
from vendor_commands import get_supported_vendors, get_vendor_config, VENDOR_CONFIGS

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('botlinkmaster.log'), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

db = DatabaseManager()

ALLOWED_CHAT_IDS = os.getenv('ALLOWED_CHAT_IDS', '')
if ALLOWED_CHAT_IDS:
    ALLOWED_CHAT_IDS = [int(x.strip()) for x in ALLOWED_CHAT_IDS.split(',') if x.strip()]
else:
    ALLOWED_CHAT_IDS = []


def is_authorized(chat_id: int) -> bool:
    if not ALLOWED_CHAT_IDS:
        return True
    return chat_id in ALLOWED_CHAT_IDS


async def check_auth(update: Update) -> bool:
    chat_id = update.effective_chat.id
    if not is_authorized(chat_id):
        await update.message.reply_text(
            f"Access Denied\n\nYour Chat ID: {chat_id}\nHubungi admin untuk akses."
        )
        return False
    return True


# =============================================================================
# COMMAND HANDLERS
# =============================================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_auth(update):
        return
    await update.message.reply_text(
        "BotLinkMaster v4.2.0\n\n"
        "Bot monitoring perangkat jaringan dengan support optical power multi-vendor.\n\n"
        "Perintah:\n"
        "/start - Tampilkan pesan ini\n"
        "/help - Bantuan lengkap\n"
        "/list - Daftar perangkat\n"
        "/add - Tambah perangkat\n"
        "/device [nama] - Info perangkat\n"
        "/cek [device] [interface] - Cek status\n"
        "/redaman [device] [interface] - Cek optical power\n"
        "/vendors - Daftar vendor\n"
        "/delete [nama] - Hapus perangkat\n"
        "/myid - Chat ID Anda"
    )


async def myid_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    username = update.effective_user.username or "N/A"
    await update.message.reply_text(
        f"Chat ID: {chat_id}\n"
        f"Username: @{username}\n\n"
        f"Gunakan Chat ID ini untuk ALLOWED_CHAT_IDS di .env"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_auth(update):
        return
    await update.message.reply_text(
        "BANTUAN BOTLINKMASTER v4.2\n\n"
        "1. TAMBAH PERANGKAT (/add)\n"
        "/add\n"
        "nama: router-1\n"
        "host: 192.168.1.1\n"
        "username: admin\n"
        "password: pass123\n"
        "protocol: ssh\n"
        "port: 22\n"
        "vendor: cisco_ios\n"
        "description: Router utama\n\n"
        "2. CEK INTERFACE (/cek)\n"
        "/cek router-1 Gi0/0\n\n"
        "3. CEK REDAMAN/OPTICAL (/redaman)\n"
        "/redaman router-1 Gi0/0\n\n"
        "4. VENDOR DIDUKUNG (/vendors)\n"
        "cisco_ios, cisco_nxos, huawei, zte,\n"
        "juniper, mikrotik, nokia, hp_aruba,\n"
        "fiberhome, dcn, h3c, ruijie, bdcom,\n"
        "raisecom, fs, allied, datacom\n\n"
        "PENTING: Set vendor yang benar agar\n"
        "command optical sesuai dengan perangkat!"
    )


async def vendors_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show supported vendors with their commands"""
    if not await check_auth(update):
        return
    
    msg = "VENDOR YANG DIDUKUNG:\n\n"
    
    vendors_info = [
        ("cisco_ios", "Cisco IOS/IOS-XE", "show interface {int} transceiver"),
        ("cisco_nxos", "Cisco NX-OS", "show interface {int} transceiver details"),
        ("huawei", "Huawei VRP", "display transceiver interface {int}"),
        ("zte", "ZTE", "show transceiver interface {int}"),
        ("juniper", "Juniper JunOS", "show interfaces diagnostics optics {int}"),
        ("mikrotik", "MikroTik", "/interface ethernet monitor {int} once"),
        ("nokia", "Nokia SR-OS", "show port {int} optical"),
        ("hp_aruba", "HP/Aruba", "show interface {int} transceiver"),
        ("fiberhome", "FiberHome", "show transceiver interface {int}"),
        ("dcn", "DCN", "show transceiver interface {int}"),
        ("h3c", "H3C Comware", "display transceiver interface {int}"),
        ("ruijie", "Ruijie", "show transceiver interface {int}"),
        ("bdcom", "BDCOM", "show transceiver interface {int}"),
        ("raisecom", "Raisecom", "show transceiver {int}"),
        ("fs", "FS.COM", "show transceiver interface {int}"),
        ("allied", "Allied Telesis", "show system pluggable {int}"),
        ("datacom", "Datacom", "show interface {int} transceiver"),
    ]
    
    for vendor_key, name, cmd in vendors_info:
        msg += f"- {name}\n"
        msg += f"  vendor: {vendor_key}\n"
        msg += f"  cmd: {cmd}\n\n"
    
    msg += "Gunakan nilai 'vendor' saat /add perangkat"
    
    await update.message.reply_text(msg)


async def list_devices(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_auth(update):
        return
    
    devices = db.get_all_devices()
    if not devices:
        await update.message.reply_text("Belum ada perangkat. Gunakan /add")
        return
    
    msg = "DAFTAR PERANGKAT:\n\n"
    for d in devices:
        msg += f"- {d.name}\n"
        msg += f"  Host: {d.host}\n"
        msg += f"  Protocol: {d.protocol}"
        if d.port:
            msg += f":{d.port}"
        msg += "\n"
        vendor = getattr(d, 'vendor', 'generic') or 'generic'
        msg += f"  Vendor: {vendor}\n\n"
    
    msg += f"Total: {len(devices)} perangkat"
    await update.message.reply_text(msg)


async def add_device_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_auth(update):
        return
    
    text = update.message.text
    lines = text.split('\n')[1:]
    
    if not lines:
        await update.message.reply_text(
            "FORMAT TAMBAH PERANGKAT:\n\n"
            "/add\n"
            "nama: router-1\n"
            "host: 192.168.1.1\n"
            "username: admin\n"
            "password: pass123\n"
            "protocol: ssh\n"
            "port: 22\n"
            "vendor: cisco_ios\n"
            "description: Router utama\n\n"
            "Field wajib: nama, host, username, password\n"
            "Ketik /vendors untuk daftar vendor"
        )
        return
    
    data = {}
    for line in lines:
        line = line.strip()
        if ':' in line:
            key, value = line.split(':', 1)
            data[key.strip().lower()] = value.strip()
    
    required = ['nama', 'host', 'username', 'password']
    missing = [f for f in required if f not in data]
    if missing:
        await update.message.reply_text(f"Field belum lengkap: {', '.join(missing)}")
        return
    
    protocol = data.get('protocol', 'ssh').lower()
    port = data.get('port')
    if port:
        try:
            port = int(port)
        except ValueError:
            await update.message.reply_text("Port harus angka")
            return
    
    vendor = data.get('vendor', 'generic').lower()
    
    device = db.add_device(
        name=data['nama'],
        host=data['host'],
        username=data['username'],
        password=data['password'],
        protocol=protocol,
        port=port,
        description=data.get('description'),
        location=data.get('location'),
        vendor=vendor
    )
    
    if device:
        msg = f"Perangkat ditambahkan!\n\n"
        msg += f"Nama: {device.name}\n"
        msg += f"Host: {device.host}\n"
        msg += f"Protocol: {device.protocol}"
        if device.port:
            msg += f":{device.port}"
        msg += f"\nVendor: {vendor}\n"
        await update.message.reply_text(msg)
    else:
        await update.message.reply_text("Gagal menambah perangkat. Nama mungkin sudah ada.")


async def device_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_auth(update):
        return
    
    if not context.args:
        await update.message.reply_text("Gunakan: /device [nama]\nContoh: /device router-1")
        return
    
    device_name = ' '.join(context.args)
    device = db.get_device(device_name)
    
    if not device:
        await update.message.reply_text(f"Perangkat '{device_name}' tidak ditemukan")
        return
    
    vendor = getattr(device, 'vendor', 'generic') or 'generic'
    vendor_cfg = get_vendor_config(vendor)
    
    msg = f"INFO PERANGKAT: {device.name}\n\n"
    msg += f"Host: {device.host}\n"
    msg += f"Username: {device.username}\n"
    msg += f"Protocol: {device.protocol}"
    if device.port:
        msg += f":{device.port}"
    msg += f"\nVendor: {vendor} ({vendor_cfg.name})\n"
    if device.description:
        msg += f"Deskripsi: {device.description}\n"
    
    msg += f"\nOptical Command:\n{vendor_cfg.show_optical_interface}"
    
    await update.message.reply_text(msg)


async def check_interface(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_auth(update):
        return
    
    if len(context.args) < 2:
        await update.message.reply_text(
            "Gunakan: /cek [device] [interface]\n"
            "Contoh: /cek router-1 Gi0/0"
        )
        return
    
    device_name = context.args[0]
    interface_name = ' '.join(context.args[1:])
    
    device = db.get_device(device_name)
    if not device:
        await update.message.reply_text(f"Perangkat '{device_name}' tidak ditemukan")
        return
    
    checking_msg = await update.message.reply_text(
        f"Mengecek {interface_name} di {device_name}..."
    )
    
    try:
        vendor = getattr(device, 'vendor', 'generic') or 'generic'
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
                await checking_msg.edit_text(f"Gagal koneksi ke {device_name}")
                return
            
            info = bot.get_specific_interface(interface_name)
            
            if not info:
                await checking_msg.edit_text(f"Interface '{interface_name}' tidak ditemukan")
                return
            
            status = info.get('status', 'unknown')
            icon = "UP" if 'up' in status.lower() else "DOWN"
            
            msg = f"STATUS INTERFACE\n\n"
            msg += f"Device: {device_name}\n"
            msg += f"Interface: {interface_name}\n"
            msg += f"Status: {icon} ({status})\n"
            if info.get('description'):
                msg += f"Description: {info['description']}\n"
            
            msg += f"\nGunakan /redaman {device_name} {interface_name}\n"
            msg += f"untuk cek optical power"
            
            await checking_msg.edit_text(msg)
            
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        await checking_msg.edit_text(f"Error: {str(e)}")


async def check_optical(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """CEK REDAMAN / OPTICAL POWER - MAIN COMMAND"""
    if not await check_auth(update):
        return
    
    if len(context.args) < 2:
        await update.message.reply_text(
            "CEK OPTICAL POWER / REDAMAN\n\n"
            "Gunakan: /redaman [device] [interface]\n\n"
            "Contoh:\n"
            "/redaman router-1 Gi0/0\n"
            "/redaman switch-1 Te0/1\n"
            "/redaman olt-1 gpon-olt_1/1/1\n\n"
            "Data yang akan ditampilkan:\n"
            "- TX Power (dBm)\n"
            "- RX Power (dBm)\n"
            "- Temperature (C)\n"
            "- Signal Status"
        )
        return
    
    device_name = context.args[0]
    interface_name = ' '.join(context.args[1:])
    
    device = db.get_device(device_name)
    if not device:
        await update.message.reply_text(f"Perangkat '{device_name}' tidak ditemukan")
        return
    
    vendor = getattr(device, 'vendor', 'generic') or 'generic'
    vendor_cfg = get_vendor_config(vendor)
    
    checking_msg = await update.message.reply_text(
        f"Mengecek optical power...\n\n"
        f"Device: {device_name}\n"
        f"Interface: {interface_name}\n"
        f"Vendor: {vendor_cfg.name}\n\n"
        f"Command: {vendor_cfg.show_optical_interface.format(interface=interface_name)}\n\n"
        f"Mohon tunggu..."
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
                await checking_msg.edit_text(
                    f"GAGAL KONEKSI\n\n"
                    f"Device: {device_name}\n"
                    f"Host: {device.host}\n\n"
                    f"Periksa:\n"
                    f"- Host dan port benar\n"
                    f"- Kredensial valid\n"
                    f"- Device dapat dijangkau"
                )
                return
            
            # Get optical info
            optical = bot.check_interface_with_optical(interface_name)
            
            # Build response
            status = optical.get('status', 'unknown')
            link_icon = "[UP]" if 'up' in status.lower() else "[DOWN]"
            
            # Signal status
            signal = optical.get('optical_status', 'unknown')
            if signal == 'excellent':
                signal_icon = "[EXCELLENT]"
            elif signal == 'good':
                signal_icon = "[GOOD]"
            elif signal == 'fair':
                signal_icon = "[FAIR]"
            elif signal == 'weak':
                signal_icon = "[WEAK]"
            elif signal == 'critical':
                signal_icon = "[CRITICAL]"
            else:
                signal_icon = "[?]"
            
            msg = f"OPTICAL POWER STATUS\n"
            msg += f"{'='*30}\n\n"
            msg += f"Device: {device_name}\n"
            msg += f"Vendor: {vendor_cfg.name}\n"
            msg += f"Interface: {interface_name}\n"
            msg += f"Link Status: {link_icon} {status}\n\n"
            
            msg += f"OPTICAL READINGS:\n"
            msg += f"TX Power: {optical.get('tx_power_dbm', 'N/A')}\n"
            msg += f"RX Power: {optical.get('rx_power_dbm', 'N/A')}\n"
            
            if optical.get('temperature'):
                msg += f"Temperature: {optical['temperature']} C\n"
            
            msg += f"Signal: {signal_icon} {signal.upper()}\n\n"
            
            # Reference levels
            msg += f"REFERENSI LEVEL:\n"
            msg += f"Excellent: > -8 dBm\n"
            msg += f"Good: -8 to -14 dBm\n"
            msg += f"Fair: -14 to -20 dBm\n"
            msg += f"Weak: -20 to -25 dBm\n"
            msg += f"Critical: < -25 dBm\n"
            
            # If no data found
            if not optical.get('found'):
                msg += f"\n{'='*30}\n"
                msg += f"DATA TIDAK DITEMUKAN\n\n"
                msg += f"Kemungkinan:\n"
                msg += f"1. Interface bukan SFP/transceiver\n"
                msg += f"2. Vendor setting salah\n"
                msg += f"3. Command tidak didukung\n\n"
                msg += f"Command yang dicoba:\n"
                msg += f"{optical.get('command_used', 'unknown')}\n\n"
                msg += f"Coba update vendor dengan benar.\n"
                msg += f"Ketik /vendors untuk daftar."
            else:
                msg += f"\nCommand: {optical.get('command_used', 'N/A')}"
            
            await checking_msg.edit_text(msg)
            
    except Exception as e:
        logger.error(f"Optical error: {str(e)}")
        await checking_msg.edit_text(f"Error: {str(e)}")


async def delete_device(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_auth(update):
        return
    
    if not context.args:
        await update.message.reply_text("Gunakan: /delete [nama]")
        return
    
    device_name = ' '.join(context.args)
    device = db.get_device(device_name)
    
    if not device:
        await update.message.reply_text(f"Perangkat '{device_name}' tidak ditemukan")
        return
    
    if db.delete_device(device_name):
        await update.message.reply_text(f"Perangkat '{device_name}' dihapus")
    else:
        await update.message.reply_text(f"Gagal menghapus '{device_name}'")


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Error: {context.error}")


# =============================================================================
# MAIN
# =============================================================================

def main():
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not token:
        print("ERROR: TELEGRAM_BOT_TOKEN tidak ditemukan di .env")
        return
    
    logger.info("Starting BotLinkMaster v4.2...")
    
    application = Application.builder().token(token).build()
    
    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("myid", myid_command))
    application.add_handler(CommandHandler("list", list_devices))
    application.add_handler(CommandHandler("add", add_device_command))
    application.add_handler(CommandHandler("device", device_info))
    application.add_handler(CommandHandler("cek", check_interface))
    application.add_handler(CommandHandler("redaman", check_optical))
    application.add_handler(CommandHandler("optical", check_optical))
    application.add_handler(CommandHandler("vendors", vendors_command))
    application.add_handler(CommandHandler("delete", delete_device))
    
    application.add_error_handler(error_handler)
    
    logger.info("Bot started!")
    if ALLOWED_CHAT_IDS:
        logger.info(f"Access restricted to: {ALLOWED_CHAT_IDS}")
    
    print("\nBotLinkMaster v4.2 Started!")
    print("Commands: /start /help /list /add /cek /redaman /vendors")
    print("\n[Press Ctrl+C to stop]\n")
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()