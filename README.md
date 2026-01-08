# BotLinkMaster v4.1.0

🤖 Bot Telegram untuk monitoring perangkat jaringan via SSH/Telnet

---

## 📋 Daftar Isi

- [Tentang](#-tentang)
- [Fitur](#-fitur)
- [Requirements](#-requirements)
- [Struktur File](#-struktur-file)
- [Instalasi Cepat](#-instalasi-cepat)
- [Konfigurasi](#-konfigurasi)
- [Penggunaan](#-penggunaan)
- [Command Bot](#-command-bot)
- [Troubleshooting](#-troubleshooting)

---

## 🎯 Tentang

**BotLinkMaster** adalah bot monitoring perangkat jaringan yang memungkinkan Anda:
- ✅ Cek status interface perangkat jaringan via SSH/Telnet
- ✅ Kelola kredensial perangkat dengan aman di database
- ✅ Monitoring melalui Telegram Bot
- ✅ Jalankan sebagai systemd service dengan auto-start
- ✅ Interface description tracking dan status caching

**Perubahan dari v3 (remonbot):**
- Protokol: SNMP → SSH/Telnet
- Database: File config → SQLAlchemy ORM
- Service: Manual → Systemd auto-start

---

## ✨ Fitur

### Core Features
- Koneksi SSH dan Telnet ke perangkat jaringan
- Database terintegrasi (SQLite default, support PostgreSQL/MySQL)
- Telegram Bot untuk monitoring
- Interface description tracking
- Multi-device management
- Connection pooling dan retry mechanism

### Service Features (v4.1.0)
- **Systemd service integration** - Auto-start saat boot
- **Service manager tool (botctl)** - Mudah manage service
- **Auto-restart** jika crash
- **Resource limits** - Memory dan CPU protection
- **Diagnostic tools** - Complete troubleshooting

### Bot Commands
- `/cek <device> <interface>` - Cek status interface
- `/list` - List semua perangkat
- `/add` - Tambah perangkat baru
- `/device <nama>` - Info detail perangkat
- `/delete <nama>` - Hapus perangkat
- `/myid` - Tampilkan Chat ID (untuk access control)
- `/help` - Bantuan lengkap

---

## 📋 Requirements

### System Requirements

**Minimum:**
- OS: Ubuntu 20.04+, Debian 10+
- RAM: 512 MB
- Storage: 150 MB
- Network: Internet untuk Telegram API

**Recommended:**
- OS: Ubuntu 22.04 LTS atau Debian 11+
- CPU: 2 Cores
- RAM: 1 GB
- Storage: 500 MB
- Network: Stable internet connection

### Software Requirements

**Otomatis terinstall oleh installer:**
- Python 3.8+ (recommended 3.11+)
- python3-pip, python3-venv
- git, curl, wget
- openssh-client, telnet

**Python Dependencies:**
```
paramiko==3.4.0          # SSH connections
python-telegram-bot==20.7 # Telegram Bot
SQLAlchemy==2.0.25       # Database ORM
click==8.1.7             # CLI
rich==13.7.0             # CLI formatting
python-dotenv==1.0.0     # .env support
```

### Network Requirements

**Outbound Ports (WAJIB):**
- Port 443 (HTTPS) → api.telegram.org
- Port 22 (SSH) → Network devices
- Port 23 (Telnet) → Network devices (optional)

**Inbound:** Tidak perlu (bot uses polling)

### Telegram Requirements

- Bot Token dari [@BotFather](https://t.me/botfather)
- Akun Telegram aktif

**Cara Dapatkan Token:**
1. Buka Telegram, cari @BotFather
2. Kirim: `/newbot`
3. Ikuti instruksi
4. Simpan token yang diberikan

### Target Device Requirements

Perangkat jaringan yang akan dimonitor:
- Support SSH dan/atau Telnet
- User account dengan privilege show commands
- Reachable dari server bot
- Standard command output (Cisco-like preferred)

**Supported Devices:**
- Cisco IOS/IOS-XE, Cisco NX-OS
- Juniper JunOS
- HP/Aruba
- MikroTik
- Huawei
- ZTE
- Fiber Home
- DCN
- H3C
- Nokia
- RUIJIE
- Generic SSH/Telnet devices

---

## ⚡ Instalasi Cepat

### 1. Download & Setup

* Clone repository
```bash
git clone https://github.com/Iyankz/botlinkmaster.git
cd ~/botlinkmaster/
```
* Run installer (akan meminta sudo otomatis)
```bash
sudo chmod +x install-complete.sh
./install-complete.sh
```

**Installer akan:**
- ✅ Install system dependencies
- ✅ Setup Python virtual environment
- ✅ Install Python packages
- ✅ Setup systemd service
- ✅ Enable auto-start on boot
- ✅ Configure timezone

### 3. Konfigurasi

```bash
# Edit .env file
sudo nano .env

# Tambahkan bot token:
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz

# Optional: Tambahkan allowed chat IDs
# ALLOWED_CHAT_IDS=123456789,987654321

# Save: Ctrl+O, Enter
# Exit: Ctrl+X
```

### 4. Start Service

```bash
# Start service
sudo systemctl start botlinkmaster

# Check status
sudo systemctl status botlinkmaster

# View logs
sudo journalctl -u botlinkmaster -f
```

### 5. Test Bot

- Buka Telegram
- Cari bot Anda
- Kirim: `/start`
- Bot harus merespon!

**Selesai!** ✅ Bot berjalan sebagai service dan auto-start saat boot.

---

## 🔧 Konfigurasi

### File .env

```bash
# Required
TELEGRAM_BOT_TOKEN=your_bot_token_here

# Optional - Access Control
ALLOWED_CHAT_IDS=123456789,987654321

# Optional - Database (default: SQLite)
DATABASE_URL=sqlite:///botlinkmaster.db
# DATABASE_URL=postgresql://user:pass@localhost/botlinkmaster
# DATABASE_URL=mysql://user:pass@localhost/botlinkmaster

# Optional - Logging
LOG_LEVEL=INFO
LOG_FILE=botlinkmaster.log

# Optional - Connection
SSH_TIMEOUT=30
TELNET_TIMEOUT=30
```

### Access Control

**Cara mendapatkan Chat ID:**
1. Kirim `/myid` ke bot
2. Bot akan reply dengan Chat ID Anda
3. Tambahkan ke .env: `ALLOWED_CHAT_IDS=123456789`
4. Restart service: `sudo systemctl restart botlinkmaster`

**Multiple users:**
```bash
ALLOWED_CHAT_IDS=123456789,987654321,555666777
```

---

## 🚀 Penggunaan

### Menggunakan Service (Recommended)

```bash
# Start service
sudo systemctl start botlinkmaster

# Stop service
sudo systemctl stop botlinkmaster

# Restart service
sudo systemctl restart botlinkmaster

# Check status
sudo systemctl status botlinkmaster

# View logs (realtime)
sudo journalctl -u botlinkmaster -f

# View logs (last 100 lines)
sudo journalctl -u botlinkmaster -n 100

# Enable auto-start (sudah enabled oleh installer)
sudo systemctl enable botlinkmaster

# Disable auto-start
sudo systemctl disable botlinkmaster
```

### Menggunakan botctl (Easy Way)

```bash
# Make executable (first time)
chmod +x botctl

# Start
sudo ./botctl start

# Stop
sudo ./botctl stop

# Restart
sudo ./botctl restart

# Status
sudo ./botctl status

# Logs (realtime)
sudo ./botctl logs

# Enable auto-start
sudo ./botctl enable

# Disable auto-start
sudo ./botctl disable
```

### Manual Mode (Development/Testing)

```bash
# Stop service first
sudo systemctl stop botlinkmaster

# Activate virtual environment
source venv/bin/activate

# Run manually
python telegram_bot.py

# Exit: Ctrl+C
# Deactivate: deactivate
```

---

## 💬 Command Bot

### Basic Commands

```
/start - Start bot dan lihat menu
/help - Bantuan lengkap
/myid - Tampilkan Chat ID Anda
```

### Device Management

```
/list - List semua perangkat
/add - Tambah perangkat baru (interactive)
/device <nama> - Info detail perangkat
/delete <nama> - Hapus perangkat
```

### Monitoring

```
/cek <device> <interface> - Cek status interface
/cek router1 gi0/1 - Contoh: cek interface GigabitEthernet0/1
```

### Example Usage

```
User: /add
Bot: [Interactive form untuk tambah device]

User: /list
Bot: [Menampilkan daftar semua devices]

User: /cek router1 gi0/1
Bot: [Menampilkan status interface GigabitEthernet0/1]
```

---

## 🔍 Troubleshooting

### Bot tidak merespon

```bash
# Check service status
sudo systemctl status botlinkmaster

# Check logs
sudo journalctl -u botlinkmaster -n 50

# Restart service
sudo systemctl restart botlinkmaster

# If still not working, run diagnostic
python diagnose.py
```

### Service tidak start

```bash
# Check logs for errors
sudo journalctl -u botlinkmaster -n 50

# Check .env file
cat .env | grep TOKEN

# Test bot manually
sudo systemctl stop botlinkmaster
source venv/bin/activate
python telegram_bot.py
# Watch for errors
```

### Connection to device failed

```bash
# Test SSH connection
ssh username@device-ip

# Test Telnet connection
telnet device-ip

# Check firewall
sudo ufw status

# Test from bot
python test_bot.py
```

### Database error

```bash
# Check database file
ls -la botlinkmaster.db

# Reset database (CAUTION: deletes all data!)
rm botlinkmaster.db
source venv/bin/activate
python -c "from database import init_db; init_db()"
```

### Common Issues

**Token error:**
```bash
# Check token in .env
cat .env | grep TOKEN

# Token format: 123456789:ABCdefGHIjklMNOpqrsTUVwxyz
# Make sure no extra spaces or quotes
```

**Permission error:**
```bash
# Fix file permissions
sudo chown -R $USER:$USER .
chmod 600 .env
chmod 755 *.sh botctl
```

**Python version:**
```bash
# Check Python version
python3 --version
# Must be 3.8+

# If too old, install newer Python
sudo apt update
sudo apt install python3.11
```

---

## 📚 Dokumentasi Lengkap

### Bahasa Indonesia
- **README_ID.md** - Dokumentasi lengkap (Indonesia)
- **QUICKSTART_ID.md** - Panduan cepat (Indonesia)
- **INSTALL_CARD_ID.txt** - Kartu instalasi (Indonesia)

### English
- **SERVICE_GUIDE.md** - Complete systemd service guide
- **BOTCTL_GUIDE.md** - Complete botctl documentation
- **REQUIREMENTS.md** - Detailed system requirements
- **TROUBLESHOOTING.md** - Complete troubleshooting guide

### Quick Reference
- **INSTALL_CARD.txt** - Installation quick reference
- **REQUIREMENTS_CARD.txt** - Requirements quick reference
- **RELEASE_v4.1.0.txt** - Release summary

---

## 🆘 Bantuan

### Diagnostic Tool

```bash
# Run complete diagnostic
python diagnose.py

# This will check:
# - Python version
# - Dependencies
# - Configuration files
# - Database
# - Network connectivity
# - Telegram API
# - Service status
```

### Need Help?

1. Read documentation in this repository
2. Run `python diagnose.py` for automatic diagnosis
3. Check `TROUBLESHOOTING.md` for common issues
4. View service logs: `sudo journalctl -u botlinkmaster -n 100`

---

## 📝 Lisensi

MIT License - See LICENSE file for details

---

## 👥 Contributors

- [Iyankz](https://github.com/Iyankz) - Developer
- [Gemini](https://gemini.google.com/) - AI Assistant
- [Claude](https://claude.ai/) - AI Assistant

---

## 📊 Version Info

**Current Version:** 4.1.0  
**Release Date:** January 7, 2026  
**Python Required:** 3.8+  
**OS Support:** Ubuntu, Debian, CentOS, RHEL, Fedora, Arch Linux

---

## 🔄 Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history.

See [RELEASE_NOTES_v4.1.0.md](RELEASE_NOTES_v4.1.0.md) for latest release details.

---

**BotLinkMaster v4.1.0** - Production-Ready Service Edition! 🚀
