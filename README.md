# BotLinkMaster v4.1.0

🤖 Bot monitoring perangkat jaringan via SSH/Telnet dengan integrasi Telegram

## 📋 Daftar Isi

- [Tentang](#-tentang)
- [Fitur](#-fitur)
- [Requirements](#-requirements)
- [Perubahan dari v3](#-perubahan-dari-v3-remonbot)
- [Struktur Direktori](#-struktur-direktori)
- [Instalasi](#-instalasi)
- [Konfigurasi](#-konfigurasi)
- [Penggunaan](#-penggunaan)
- [Command Bot Telegram](#-command-bot-telegram)
- [Troubleshooting](#-troubleshooting)
- [Lisensi](#-lisensi)

## 🎯 Tentang

**BotLinkMaster** adalah bot monitoring perangkat jaringan yang memungkinkan Anda untuk:
- Mengecek status interface perangkat jaringan
- Mengelola kredensial perangkat dengan aman di database
- Monitoring melalui Telegram Bot
- Mendukung protokol SSH dan Telnet
- Menyimpan description interface

## ✨ Fitur

### Core Features
- ✅ Koneksi SSH dan Telnet ke perangkat jaringan
- ✅ Database terintegrasi untuk menyimpan kredensial
- ✅ Telegram Bot untuk monitoring
- ✅ Interface description tracking
- ✅ Interface status caching
- ✅ Multi-device management
- ✅ Custom port configuration
- ✅ Connection pooling dan retry mechanism

### Bot Commands
- `/cek <device> <interface>` - Cek status interface
- `/list` - List semua perangkat
- `/add` - Tambah perangkat baru
- `/device <nama>` - Info detail perangkat
- `/delete <nama>` - Hapus perangkat
- `/myid` - Tampilkan Chat ID Anda (untuk konfigurasi akses)
- `/help` - Bantuan lengkap

## 📋 Requirements

### System Requirements

**Minimum:**
- **OS:** Ubuntu 20.04+, Debian 10+
- **CPU:** 1 Core
- **RAM:** 512 MB
- **Storage:** 100 MB (aplikasi) + 50-200 MB (database, tergantung jumlah perangkat)
- **Network:** Koneksi internet untuk Telegram API

**Direkomendasikan:**
- **OS:** Ubuntu 22.04 LTS atau Debian 11+
- **CPU:** 2 Cores
- **RAM:** 1 GB
- **Storage:** 500 MB
- **Network:** Koneksi internet stabil

### Software Requirements

**System Packages (otomatis terinstall oleh installer):**
- Python 3.8 atau lebih baru (direkomendasikan Python 3.11+)
- python3-pip, python3-venv
- git
- curl, wget
- openssh-client, telnet
- tzdata

**Python Packages (otomatis terinstall oleh installer):**
```
paramiko==3.4.0          # Untuk koneksi SSH
python-telegram-bot==20.7 # Untuk Telegram Bot
SQLAlchemy==2.0.25       # Untuk database ORM
click==8.1.7             # Untuk CLI
rich==13.7.0             # Untuk CLI formatting
python-dotenv==1.0.0     # Untuk .env file support
```

### Network Requirements

**Ports yang Dibutuhkan:**
- **Outbound:**
  - Port 443 (HTTPS) - Untuk Telegram API
  - Port 22 (SSH) - Untuk koneksi ke perangkat jaringan
  - Port 23 (Telnet) - Untuk koneksi ke perangkat jaringan (opsional)

**Tidak memerlukan inbound ports** - Bot menggunakan polling dari Telegram API

### Telegram Requirements

- **Bot Token** dari [@BotFather](https://t.me/botfather)
- Akun Telegram untuk menggunakan bot

### Target Device Requirements

Perangkat jaringan yang akan dimonitor harus:
- Support SSH dan/atau Telnet
- User account dengan akses ke show commands
- Reachable dari server bot
- Standard command output (Cisco-like preferred)

**Supported Devices:**
- Cisco IOS/IOS-XE
- Cisco NX-OS
- Juniper JunOS
- HP/Aruba
- MikroTik
- Generic SSH/Telnet devices

## 🔄 Perubahan dari v3 (remonbot)

| Aspek | v3 (remonbot) | v4 (botlinkmaster) |
|-------|---------------|---------------------|
| **Nama** | remonbot | botlinkmaster |
| **Protokol** | SNMP | SSH/Telnet |
| **Database** | File config | SQLAlchemy ORM |
| **Port** | Fixed | Configurable |
| **Deskripsi** | ❌ | ✅ Interface description |
| **Kredensial** | Manual config | Database storage |

## 📁 Struktur Direktori

### 📂 Di Git Repository (v4.1.0 - 35+ files)

```
botlinkmaster/
│
├── README.md                              # ⭐ Main documentation (root level!)
├── LICENSE                                # MIT License
│
├── 🐍 Core Python Modules
│   ├── telegram_bot.py                    # Main Telegram bot
│   ├── botlinkmaster.py                   # SSH/Telnet handler
│   ├── database.py                        # Database ORM
│   └── cli.py                             # CLI tool
│
├── 🔧 Service & Installation (NEW v4.1.0!)
│   ├── install-complete.sh                # 🆕 One-command installer
│   ├── botctl                             # 🆕 Service manager tool
│   ├── setup-service.sh                   # 🆕 Manual service setup
│   ├── install.sh                         # Legacy installer
│   ├── install-simple.sh                  # Simple installer (no colors)
│   └── botlinkmaster.service              # Systemd service file
│
├── 🔍 Diagnostic Tools (NEW v4.1.0!)
│   ├── diagnose.py                        # 🆕 Complete diagnostic
│   └── test_bot.py                        # 🆕 Connection tester
│
├── 🐳 Docker
│   ├── Dockerfile                         # Docker image
│   ├── docker-compose.yml                 # Docker Compose
│   └── docker-run.sh                      # Docker script
│
├── ⚙️ Configuration
│   ├── .env.example                       # Environment template
│   ├── env.example                        # Environment template backup
│   ├── config_example.py                  # Config template
│   └── requirements.txt                   # Python dependencies
│
├── 📚 Documentation Files (all at root level for easy access)
│   │
│   ├── 🇬🇧 English Documentation
│   │   ├── README_SERVICE.md              # 🆕 Service edition README
│   │   ├── QUICKSTART.md                  # Quick start guide
│   │   ├── QUICKSTART_SERVICE.md          # 🆕 Service quick start
│   │   ├── SERVICE_GUIDE.md               # 🆕 Complete service guide
│   │   ├── BOTCTL_GUIDE.md                # 🆕 botctl documentation
│   │   ├── REQUIREMENTS.md                # 🆕 Complete requirements
│   │   ├── TROUBLESHOOTING.md             # Troubleshooting guide
│   │   ├── QUICK_FIX.md                   # 🆕 Quick fixes
│   │   ├── EXAMPLES.md                    # Usage examples
│   │   ├── INSTALLATION_FLOW.md           # Installation flow
│   │   ├── PROJECT_STRUCTURE.md           # Project structure
│   │   ├── DEPLOYMENT_SUMMARY.md          # 🆕 Deployment info
│   │   ├── CHANGELOG.md                   # Version history
│   │   ├── MILESTONES.md                  # Roadmap
│   │   └── RELEASE_NOTES_v4.1.0.md        # 🆕 Release notes
│   │
│   ├── 🇮🇩 Indonesian Documentation (NEW v4.1.0!)
│   │   ├── README_ID.md                   # 🆕 Main docs (Indonesia)
│   │   ├── QUICKSTART_ID.md               # 🆕 Quick start (Indonesia)
│   │   ├── RELEASE_NOTES_v4.1.0_ID.md     # 🆕 Release notes (Indonesia)
│   │   └── FIX_SUMMARY_v4.0.1.md          # Fix summary
│   │
│   └── 📄 Quick Reference Cards (NEW v4.1.0!)
│       ├── INSTALL_CARD.txt               # 🆕 Installation reference
│       ├── INSTALL_CARD_ID.txt            # 🆕 Installation (Indonesia)
│       ├── REQUIREMENTS_CARD.txt          # 🆕 Requirements reference
│       ├── RELEASE_v4.1.0.txt             # 🆕 Release summary
│       └── FIXED_ISSUES.txt               # Fixed issues log
│
├── 📋 Meta Files
│   ├── .gitignore                         # Git ignore rules
│   └── VERSION                            # 🆕 Version number (4.1.0)
│
└── 🗑️ Legacy/Backup
    └── botlinkmaster.service.template     # Old service template

NOTE: Semua file dokumentasi ada di root directory (tidak di subfolder)
      sehingga mudah diakses dan README.md langsung tampil di GitHub.
```

### 🚀 Setelah Instalasi (Runtime Files)

```
botlinkmaster/
├── (Semua 35+ files dari Git Repository)
│
├── ✨ Generated Files
│   ├── .env                               # Environment vars (CREATED)
│   ├── config.py                          # Configuration (CREATED)
│   ├── venv/                              # Virtual environment (CREATED)
│   ├── botlinkmaster.db                   # SQLite database (CREATED)
│   ├── botlinkmaster.log                  # Application logs (CREATED)
│   └── __pycache__/                       # Python cache (CREATED)
│
└── 🔧 System Files
    └── /etc/systemd/system/
        └── botlinkmaster.service          # Installed service (CREATED)
```

**⚠️ PENTING - Privilege:**
- **Instalasi memerlukan root/sudo** untuk install system dependencies
- Script `install.sh` akan **otomatis request sudo** jika belum root
- Bot berjalan sebagai **user biasa** (tidak perlu root)

## 🚀 Instalasi

### Install Otomatis

* Clone repository
```bash
git clone https://github.com/Iyankz/botlinkmaster.git
cd /botlinkmaster/'Service & Installation (NEW v4.1.0!)'
```
* Run installer (akan meminta sudo otomatis)
```bash
chmod +x install-complete.sh
./install-complete.sh
```

**Installer akan:**
1. ✅ Install system dependencies (python3, pip, openssh, telnet)
2. ✅ Konfigurasi timezone (dengan pilihan)
3. ✅ Membuat virtual environment
4. ✅ Install Python packages
5. ✅ Setup file konfigurasi
6. ✅ Initialize database
7. ✅ Test imports

### Install Manual

```bash
# Install system dependencies (requires root)
sudo apt-get install python3 python3-pip python3-venv git openssh-client telnet

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Setup configuration
cp .env.example .env
cp config_example.py config.py
```

## ⚙️ Konfigurasi

### 1. Edit .env File

```bash
nano .env
```

Tambahkan bot token:
```
TELEGRAM_BOT_TOKEN=your_bot_token_from_botfather
DATABASE_URL=sqlite:///botlinkmaster.db
LOG_LEVEL=INFO
```

### 2. (Opsional) Batasi Akses Bot

Agar hanya user tertentu yang bisa akses:

```bash
# 1. Dapatkan Chat ID dengan kirim /myid ke bot
# 2. Tambahkan ke .env:
nano .env

# Single user:
ALLOWED_CHAT_IDS=123456789

# Multiple users (pisah dengan koma):
ALLOWED_CHAT_IDS=123456789,987654321,456789123
```

### 3. (Opsional) Edit config.py

```python
# Database
DATABASE_URL = "sqlite:///botlinkmaster.db"

# Timeouts
SSH_TIMEOUT = 30
TELNET_TIMEOUT = 30
```

## 📱 Penggunaan

### Jalankan sebagai System Service (Recommended)

**Cara termudah - Bot jalan otomatis di background:**

```bash
# Setup service (dilakukan sekali)
sudo ./setup-service.sh

# Start bot
sudo systemctl start botlinkmaster

# Enable auto-start on boot
sudo systemctl enable botlinkmaster

# Check status
sudo systemctl status botlinkmaster

# View logs
sudo journalctl -u botlinkmaster -f
```

**Atau gunakan script `botctl` untuk kemudahan:**

```bash
chmod +x botctl

# Start
sudo ./botctl start

# Stop  
sudo ./botctl stop

# Status
sudo ./botctl status

# Logs
sudo ./botctl logs
```

Lihat [SERVICE_GUIDE.md](SERVICE_GUIDE.md) untuk panduan lengkap.

### Jalankan Manual (Development)

```bash
# Activate virtual environment
source venv/bin/activate

# Run bot
python telegram_bot.py
```

### Jalankan dengan Docker

```bash
# Edit .env file
nano .env

# Run with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f
```

---

## 🤖 Command Bot Telegram

### /start
Menampilkan welcome message dan daftar perintah

### /help
Bantuan lengkap penggunaan bot

### /add
Tambah perangkat baru dengan format multiline:
```
/add
nama: router-1
host: 192.168.1.1
username: admin
password: password123
protocol: ssh
port: 22
description: Router utama
location: Kantor pusat
```

### /list
Tampilkan semua perangkat terdaftar

### /device <nama>
Info detail perangkat dan cached interfaces

### /cek <device> <interface>
Cek status interface (command utama):
```
/cek router-1 GigabitEthernet0/0
/cek switch-1 Gi0/1
```

### /delete <nama>
Hapus perangkat dari database

### /myid
Tampilkan Chat ID Anda untuk konfigurasi ALLOWED_CHAT_IDS

## 🐛 Troubleshooting

### Bot tidak bisa start - Token tidak ditemukan

```bash
# Pastikan .env ada dan berisi token
cat .env | grep TELEGRAM_BOT_TOKEN

# Pastikan venv aktif
source venv/bin/activate

# Test load .env
python3 -c "from dotenv import load_dotenv; import os; load_dotenv(); print(os.getenv('TELEGRAM_BOT_TOKEN'))"
```

**Penting:** Token TIDAK boleh ada spasi di sekitar `=`
- ❌ SALAH: `TELEGRAM_BOT_TOKEN = token`
- ✅ BENAR: `TELEGRAM_BOT_TOKEN=token`

Lihat [TROUBLESHOOTING.md](TROUBLESHOOTING.md) untuk guide lengkap

### Bot running tapi tidak bisa diakses

Cek apakah Chat ID Anda ada di ALLOWED_CHAT_IDS:

```bash
# Dapatkan Chat ID
# Kirim /myid ke bot

# Edit .env
nano .env

# Tambahkan Chat ID:
ALLOWED_CHAT_IDS=123456789
```

### Module not found

```bash
# Cek dependencies
source venv/bin/activate
python -c "import telegram; print('OK')"
```

### Connection failed
- Periksa host dan port benar
- Periksa kredensial valid
- Periksa device dapat dijangkau
- Periksa firewall

### Permission denied
```bash
chmod 600 .env config.py
chmod +x install.sh docker-run.sh cli.py
```

## 📝 Lisensi

MIT License - lihat file [LICENSE](LICENSE) untuk detail


---

## 👥 Credits & 👥 Contributors

* [**Iyankz**](https://github.com/Iyankz) (Developer & Tester)
* [**Gemini**](https://gemini.google.com/) (AI Partner & Technical Assistant)
* [**Claude**](https://claude.ai/) (AI Partner & Technical Assistant)

---

## ⭐ Support This Project

If remonbot helps you:
1. ⭐ Star this repository
2. 🐛 Report bugs to help improve
3. 💡 Suggest features
4. 🔄 Share with other network engineers
5. ☕ Buy me a coffee (optional)

---

**Made with ❤️ for Network Engineers**

🚀 **Auto Discovery • Multi-Vendor • Per-Interface Monitoring**


## 🙏 Penghargaan

- Paramiko untuk library SSH
- python-telegram-bot untuk integrasi Telegram
- SQLAlchemy untuk ORM database

---

**BotLinkMaster v4.1** - Monitoring Perangkat Jaringan Menjadi Mudah 🚀
