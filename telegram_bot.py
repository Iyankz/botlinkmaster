#!/usr/bin/env python3
"""
BotLinkMaster v4.5 - Telegram Bot
Network device monitoring with multi-vendor optical power support

Features:
- Multi-vendor support (22+ vendors)
- OLT/ONU optical power monitoring
- Timezone configuration (IANA)
- Multiple chat ID and group support
- Interface listing with status and description

Author: BotLinkMaster
Version: 4.5
"""

import os
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

from botlinkmaster import BotLinkMaster, ConnectionConfig, Protocol
from database import DatabaseManager
from vendor_commands import get_supported_vendors, get_vendor_config, VENDOR_CONFIGS
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

# Load allowed chat IDs from env (supports multiple IDs and groups)
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
    """Check if chat ID is authorized (user or group)"""
    # If no restrictions, allow all
    if not ALLOWED_CHAT_IDS and not db.get_allowed_users():
        return True
    
    # Check env-based allowed IDs
    if chat_id in ALLOWED_CHAT_IDS:
        return True
    
    # Check database-based allowed users
    if db.is_user_allowed(chat_id):
        return True
    
    return False


async def check_auth(update: Update) -> bool:
    chat_id = update.effective_chat.id
    if not is_authorized(chat_id):
        chat_type = update.effective_chat.type
        await update.message.reply_text(
            f"Access Denied\n\n"
            f"Chat ID: {chat_id}\n"
            f"Type: {chat_type}\n\n"
            f"Hubungi admin untuk mendapatkan akses.\n"
            f"Tambahkan Chat ID ke ALLOWED_CHAT_IDS di .env"
        )
        return False
    return True


# =============================================================================
# COMMAND HANDLERS
# =============================================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_auth(update):
        return
    
    current_time = tz_manager.get_current_time()
    
    await update.message.reply_text(
        f"BotLinkMaster v4.5.0\n"
        f"{'='*30}\n\n"
        f"Bot monitoring perangkat jaringan.\n"
        f"Support 22+ vendor dengan optical power.\n\n"
        f"Waktu: {current_time}\n"
        f"Timezone: {tz_manager.get_timezone()}\n\n"
        f"Ketik /help untuk bantuan lengkap."
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_auth(update):
        return
    
    await update.message.reply_text(
        "BANTUAN BOTLINKMASTER v4.5\n"
        "="*30 + "\n\n"
        "PERINTAH TERSEDIA:\n\n"
        "INFO & BANTUAN:\n"
        "/start - Tampilkan info bot\n"
        "/help - Tampilkan bantuan ini\n"
        "/myid - Tampilkan Chat ID Anda\n"
        "/time - Tampilkan waktu saat ini\n\n"
        "DEVICE MANAGEMENT:\n"
        "/add - Tambah perangkat baru\n"
        "/list - Daftar semua perangkat\n"
        "/device [nama] - Detail perangkat\n"
        "/delete [nama] - Hapus perangkat\n\n"
        "MONITORING:\n"
        "/cek [device] [interface] - Cek status\n"
        "/interfaces [device] - List interface\n"
        "/redaman [device] [interface] - Cek optical\n\n"
        "KONFIGURASI:\n"
        "/vendors - Daftar vendor\n"
        "/timezone - Info timezone\n"
        "/settz [timezone] - Set timezone\n\n"
        "Ketik /help2 untuk contoh penggunaan."
    )


async def help2_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_auth(update):
        return
    
    await update.message.reply_text(
        "CONTOH PENGGUNAAN:\n"
        "="*30 + "\n\n"
        "1. TAMBAH PERANGKAT:\n"
        "/add\n"
        "nama: router-core\n"
        "host: 192.168.1.1\n"
        "username: admin\n"
        "password: admin123\n"
        "protocol: ssh\n"
        "port: 22\n"
        "vendor: cisco_ios\n\n"
        "2. CEK INTERFACE:\n"
        "/cek router-core Gi0/0\n\n"
        "3. CEK REDAMAN:\n"
        "/redaman router-core Gi0/0\n\n"
        "4. CEK ONU (ZTE OLT):\n"
        "/redaman olt-zte gpon-onu_1/2/1:10\n\n"
        "5. LIST INTERFACE:\n"
        "/interfaces router-core\n\n"
        "6. SET TIMEZONE:\n"
        "/settz Asia/Jakarta"
    )


async def myid_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    chat_type = update.effective_chat.type
    username = update.effective_user.username or "N/A"
    first_name = update.effective_user.first_name or "N/A"
    
    await update.message.reply_text(
        f"INFO CHAT\n"
        f"{'='*30}\n\n"
        f"Chat ID: {chat_id}\n"
        f"Type: {chat_type}\n"
        f"Username: @{username}\n"
        f"Name: {first_name}\n\n"
        f"Untuk akses bot, tambahkan Chat ID\n"
        f"ke ALLOWED_CHAT_IDS di file .env\n\n"
        f"Contoh:\n"
        f"ALLOWED_CHAT_IDS={chat_id}\n\n"
        f"Untuk multiple users/groups:\n"
        f"ALLOWED_CHAT_IDS={chat_id},-100123456789"
    )


async def time_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_auth(update):
        return
    
    current_time = tz_manager.get_current_time()
    timezone = tz_manager.get_timezone()
    
    await update.message.reply_text(
        f"WAKTU SAAT INI\n"
        f"{'='*30}\n\n"
        f"Waktu: {current_time}\n"
        f"Timezone: {timezone}\n\n"
        f"Gunakan /settz untuk mengubah timezone"
    )


async def timezone_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_auth(update):
        return
    
    if context.args:
        continent = context.args[0]
        text = get_timezone_by_continent(continent)
    else:
        text = get_timezone_examples_text()
    
    await update.message.reply_text(text)


async def settz_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_auth(update):
        return
    
    if not context.args:
        await update.message.reply_text(
            "SET TIMEZONE\n\n"
            "Gunakan: /settz [timezone]\n\n"
            "Contoh:\n"
            "/settz Asia/Jakarta\n"
            "/settz Asia/Makassar\n"
            "/settz Europe/London\n\n"
            "Ketik /timezone untuk daftar lengkap"
        )
        return
    
    new_tz = context.args[0]
    
    if not validate_timezone(new_tz):
        await update.message.reply_text(
            f"Timezone '{new_tz}' tidak valid.\n\n"
            f"Format: Continent/City\n"
            f"Contoh: Asia/Jakarta\n\n"
            f"Ketik /timezone untuk daftar"
        )
        return
    
    if tz_manager.save_timezone(new_tz):
        current_time = get_current_time(new_tz)
        await update.message.reply_text(
            f"Timezone berhasil diubah!\n\n"
            f"Timezone: {new_tz}\n"
            f"Waktu sekarang: {current_time}"
        )
    else:
        await update.message.reply_text("Gagal menyimpan timezone")


async def vendors_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_auth(update):
        return
    
    vendors_info = [
        ("cisco_ios", "Cisco IOS/IOS-XE"),
        ("cisco_nxos", "Cisco NX-OS"),
        ("huawei", "Huawei VRP"),
        ("huawei_olt", "Huawei OLT"),
        ("zte", "ZTE Switch"),
        ("zte_olt", "ZTE OLT"),
        ("juniper", "Juniper JunOS"),
        ("mikrotik", "MikroTik"),
        ("nokia", "Nokia SR-OS"),
        ("hp_aruba", "HP/Aruba"),
        ("fiberhome", "FiberHome"),
        ("fiberhome_olt", "FiberHome OLT"),
        ("dcn", "DCN"),
        ("h3c", "H3C Comware"),
        ("ruijie", "Ruijie"),
        ("bdcom", "BDCOM Switch"),
        ("bdcom_olt", "BDCOM OLT"),
        ("raisecom", "Raisecom"),
        ("fs", "FS.COM"),
        ("allied", "Allied Telesis"),
        ("datacom", "Datacom"),
        ("vsol_olt", "VSOL OLT"),
    ]
    
    msg = "VENDOR YANG DIDUKUNG\n"
    msg += "="*30 + "\n\n"
    
    for vendor_key, name in vendors_info:
        msg += f"- {vendor_key}: {name}\n"
    
    msg += "\nGunakan nilai vendor saat /add\n"
    msg += "Contoh: vendor: zte_olt"
    
    await update.message.reply_text(msg)


async def list_devices(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_auth(update):
        return
    
    devices = db.get_all_devices()
    if not devices:
        await update.message.reply_text("Belum ada perangkat.\nGunakan /add untuk menambah.")
        return
    
    msg = "DAFTAR PERANGKAT\n"
    msg += "="*30 + "\n\n"
    
    for d in devices:
        msg += f"[{d.name}]\n"
        msg += f"  Host: {d.host}:{d.port or (22 if d.protocol=='ssh' else 23)}\n"
        msg += f"  Protocol: {d.protocol.upper()}\n"
        msg += f"  Vendor: {d.vendor or 'generic'}\n"
        if d.description:
            msg += f"  Desc: {d.description}\n"
        msg += "\n"
    
    msg += f"Total: {len(devices)} perangkat"
    await update.message.reply_text(msg)


async def add_device_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_auth(update):
        return
    
    text = update.message.text
    lines = text.split('\n')[1:]
    
    if not lines:
        await update.message.reply_text(
            "TAMBAH PERANGKAT\n"
            "="*30 + "\n\n"
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
            "Field wajib: nama, host, username, password\n\n"
            "Protocol: ssh (default) atau telnet\n"
            "Port: 22 (ssh) atau 23 (telnet) atau custom\n\n"
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
    if protocol not in ['ssh', 'telnet']:
        await update.message.reply_text("Protocol harus 'ssh' atau 'telnet'")
        return
    
    port = data.get('port')
    if port:
        try:
            port = int(port)
        except ValueError:
            await update.message.reply_text("Port harus angka")
            return
    else:
        port = 22 if protocol == 'ssh' else 23
    
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
        await update.message.reply_text(
            f"Perangkat ditambahkan!\n\n"
            f"Nama: {device.name}\n"
            f"Host: {device.host}:{device.port}\n"
            f"Protocol: {device.protocol.upper()}\n"
            f"Vendor: {vendor}"
        )
    else:
        await update.message.reply_text("Gagal menambah.\nNama mungkin sudah ada.")


async def device_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_auth(update):
        return
    
    if not context.args:
        await update.message.reply_text("Gunakan: /device [nama]")
        return
    
    device_name = ' '.join(context.args)
    device = db.get_device(device_name)
    
    if not device:
        await update.message.reply_text(f"Perangkat '{device_name}' tidak ditemukan")
        return
    
    vendor_cfg = get_vendor_config(device.vendor or 'generic')
    
    msg = f"INFO PERANGKAT\n"
    msg += "="*30 + "\n\n"
    msg += f"Nama: {device.name}\n"
    msg += f"Host: {device.host}:{device.port}\n"
    msg += f"Protocol: {device.protocol.upper()}\n"
    msg += f"Vendor: {device.vendor} ({vendor_cfg.name})\n"
    if device.description:
        msg += f"Deskripsi: {device.description}\n"
    if device.location:
        msg += f"Lokasi: {device.location}\n"
    
    msg += f"\nOptical Cmd: {vendor_cfg.show_optical_interface}"
    
    await update.message.reply_text(msg)


async def delete_device(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_auth(update):
        return
    
    if not context.args:
        await update.message.reply_text("Gunakan: /delete [nama]")
        return
    
    device_name = ' '.join(context.args)
    
    if db.delete_device(device_name):
        await update.message.reply_text(f"Perangkat '{device_name}' dihapus")
    else:
        await update.message.reply_text(f"Perangkat '{device_name}' tidak ditemukan")


async def list_interfaces(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """List all interfaces on a device"""
    if not await check_auth(update):
        return
    
    if not context.args:
        await update.message.reply_text(
            "LIST INTERFACE\n\n"
            "Gunakan: /interfaces [device]\n\n"
            "Contoh: /interfaces router-1"
        )
        return
    
    device_name = context.args[0]
    device = db.get_device(device_name)
    
    if not device:
        await update.message.reply_text(f"Perangkat '{device_name}' tidak ditemukan")
        return
    
    checking_msg = await update.message.reply_text(
        f"Mengambil daftar interface dari {device_name}..."
    )
    
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
                await checking_msg.edit_text(f"Gagal koneksi ke {device_name}")
                return
            
            interfaces = bot.get_interfaces()
            
            if not interfaces:
                await checking_msg.edit_text(
                    f"Tidak dapat mengambil daftar interface.\n"
                    f"Coba gunakan /cek untuk interface spesifik."
                )
                return
            
            msg = f"INTERFACE {device_name}\n"
            msg += "="*30 + "\n\n"
            
            for iface in interfaces[:30]:  # Limit 30
                status_icon = "[UP]" if iface['status'] == 'up' else "[DOWN]" if iface['status'] == 'down' else "[?]"
                msg += f"{status_icon} {iface['name']}\n"
                if iface.get('description'):
                    msg += f"    {iface['description']}\n"
            
            if len(interfaces) > 30:
                msg += f"\n... dan {len(interfaces) - 30} interface lainnya"
            
            msg += f"\n\nTotal: {len(interfaces)} interface"
            
            await checking_msg.edit_text(msg)
            
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        await checking_msg.edit_text(f"Error: {str(e)}")


async def check_interface(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_auth(update):
        return
    
    if len(context.args) < 2:
        await update.message.reply_text(
            "CEK STATUS INTERFACE\n\n"
            "Gunakan: /cek [device] [interface]\n\n"
            "Contoh:\n"
            "/cek router-1 Gi0/0\n"
            "/cek switch-1 Te0/1"
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
                await checking_msg.edit_text(f"Gagal koneksi ke {device_name}")
                return
            
            info = bot.get_interface_status(interface_name)
            
            status = info.get('status', 'unknown')
            icon = "[UP]" if status == 'up' else "[DOWN]" if status == 'down' else "[?]"
            
            msg = f"STATUS INTERFACE\n"
            msg += "="*30 + "\n\n"
            msg += f"Device: {device_name}\n"
            msg += f"Interface: {interface_name}\n"
            msg += f"Status: {icon} {status.upper()}\n"
            
            if info.get('description'):
                msg += f"Description: {info['description']}\n"
            
            msg += f"\nGunakan /redaman {device_name} {interface_name}\n"
            msg += f"untuk cek optical power"
            
            await checking_msg.edit_text(msg)
            
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        await checking_msg.edit_text(f"Error: {str(e)}")


async def check_optical(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Check optical power / redaman including ONU"""
    if not await check_auth(update):
        return
    
    if len(context.args) < 2:
        await update.message.reply_text(
            "CEK OPTICAL POWER / REDAMAN\n"
            "="*30 + "\n\n"
            "Gunakan: /redaman [device] [interface]\n\n"
            "Contoh Interface Biasa:\n"
            "/redaman router-1 Gi0/0\n"
            "/redaman switch-1 Te0/1\n\n"
            "Contoh OLT/ONU:\n"
            "/redaman olt-zte gpon-olt_1/2/1\n"
            "/redaman olt-zte gpon-onu_1/2/1:10\n\n"
            "Data yang ditampilkan:\n"
            "- TX Power (dBm)\n"
            "- RX Power (dBm)\n"
            "- Attenuation (dB) untuk ONU\n"
            "- Signal Status"
        )
        return
    
    device_name = context.args[0]
    interface_name = ' '.join(context.args[1:])
    
    device = db.get_device(device_name)
    if not device:
        await update.message.reply_text(f"Perangkat '{device_name}' tidak ditemukan")
        return
    
    vendor = device.vendor or 'generic'
    vendor_cfg = get_vendor_config(vendor)
    
    checking_msg = await update.message.reply_text(
        f"Mengecek optical power...\n\n"
        f"Device: {device_name}\n"
        f"Interface: {interface_name}\n"
        f"Vendor: {vendor_cfg.name}\n\n"
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
                    f"Host: {device.host}:{device.port}\n\n"
                    f"Periksa:\n"
                    f"- Host dan port benar\n"
                    f"- Kredensial valid\n"
                    f"- Device dapat dijangkau"
                )
                return
            
            optical = bot.check_interface_with_optical(interface_name)
            
            status = optical.get('status', 'unknown')
            link_icon = "[UP]" if status == 'up' else "[DOWN]" if status == 'down' else "[?]"
            
            signal = optical.get('optical_status', 'unknown')
            signal_icons = {
                'excellent': '[EXCELLENT]',
                'good': '[GOOD]',
                'fair': '[FAIR]',
                'weak': '[WEAK]',
                'very_weak': '[VERY WEAK]',
                'critical': '[CRITICAL]',
            }
            signal_icon = signal_icons.get(signal, '[?]')
            
            msg = f"OPTICAL POWER STATUS\n"
            msg += "="*30 + "\n\n"
            msg += f"Device: {device_name}\n"
            msg += f"Vendor: {vendor_cfg.name}\n"
            msg += f"Interface: {interface_name}\n"
            msg += f"Link Status: {link_icon} {status.upper()}\n\n"
            
            msg += f"OPTICAL READINGS:\n"
            msg += f"  TX Power: {optical.get('tx_power_dbm', 'N/A')}\n"
            msg += f"  RX Power: {optical.get('rx_power_dbm', 'N/A')}\n"
            
            if optical.get('attenuation'):
                msg += f"  Attenuation: {optical.get('attenuation_db', 'N/A')}\n"
            
            msg += f"  Signal: {signal_icon} {signal.upper()}\n\n"
            
            msg += f"REFERENSI LEVEL:\n"
            msg += f"  Excellent: > -8 dBm\n"
            msg += f"  Good: -8 to -14 dBm\n"
            msg += f"  Fair: -14 to -20 dBm\n"
            msg += f"  Weak: -20 to -25 dBm\n"
            msg += f"  Critical: < -25 dBm\n"
            
            if not optical.get('found'):
                msg += f"\n{'='*30}\n"
                msg += f"DATA TIDAK DITEMUKAN\n\n"
                msg += f"Kemungkinan:\n"
                msg += f"1. Interface bukan SFP\n"
                msg += f"2. Vendor setting salah\n"
                msg += f"3. Untuk ONU gunakan format:\n"
                msg += f"   gpon-onu_1/2/1:10\n\n"
                msg += f"Command: {optical.get('command_used', 'N/A')}"
            else:
                msg += f"\nCommand: {optical.get('command_used', 'N/A')}"
            
            await checking_msg.edit_text(msg)
            
    except Exception as e:
        logger.error(f"Optical error: {str(e)}")
        await checking_msg.edit_text(f"Error: {str(e)}")


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Error: {context.error}")


# =============================================================================
# MAIN
# =============================================================================

def main():
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not token:
        print("ERROR: TELEGRAM_BOT_TOKEN tidak ditemukan!")
        print("Tambahkan ke file .env:")
        print("TELEGRAM_BOT_TOKEN=your_token_here")
        return
    
    logger.info("Starting BotLinkMaster v4.5...")
    logger.info(f"Timezone: {tz_manager.get_timezone()}")
    
    if ALLOWED_CHAT_IDS:
        logger.info(f"Allowed Chat IDs (env): {ALLOWED_CHAT_IDS}")
    
    application = Application.builder().token(token).build()
    
    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("help2", help2_command))
    application.add_handler(CommandHandler("myid", myid_command))
    application.add_handler(CommandHandler("time", time_command))
    application.add_handler(CommandHandler("timezone", timezone_command))
    application.add_handler(CommandHandler("settz", settz_command))
    application.add_handler(CommandHandler("vendors", vendors_command))
    application.add_handler(CommandHandler("list", list_devices))
    application.add_handler(CommandHandler("add", add_device_command))
    application.add_handler(CommandHandler("device", device_info))
    application.add_handler(CommandHandler("delete", delete_device))
    application.add_handler(CommandHandler("interfaces", list_interfaces))
    application.add_handler(CommandHandler("cek", check_interface))
    application.add_handler(CommandHandler("redaman", check_optical))
    application.add_handler(CommandHandler("optical", check_optical))
    
    application.add_error_handler(error_handler)
    
    print("\n" + "="*50)
    print("BotLinkMaster v4.5 Started!")
    print("="*50)
    print(f"\nTimezone: {tz_manager.get_timezone()}")
    print(f"Time: {tz_manager.get_current_time()}")
    print("\nCommands:")
    print("  /start /help /myid /time")
    print("  /list /add /device /delete")
    print("  /interfaces /cek /redaman")
    print("  /vendors /timezone /settz")
    print("\n[Press Ctrl+C to stop]\n")
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
