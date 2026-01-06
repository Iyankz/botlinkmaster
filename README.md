# BotLinkMaster v4.0

🤖 Bot monitoring perangkat jaringan via SSH/Telnet dengan integrasi Telegram

## 📋 Daftar Isi

- [Tentang](#-tentang)
- [Fitur](#-fitur)
- [Perubahan dari v3](#-perubahan-dari-v3-remonbot)
- [Struktur Direktori](#-struktur-direktori)
- [Instalasi](#-instalasi)

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
- `/help` - Bantuan lengkap

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

### 📂 Di Git Repository (20 files)

```
botlinkmaster/
├── botlinkmaster.py                   # Main SSH/Telnet module
├── database.py                        # Database ORM
├── telegram_bot.py                    # Telegram bot interface
├── cli.py                             # CLI tool
├── config_example.py                  # Config template
├── .env.example                       # Env template
├── .gitignore                         # Git ignore
├── Dockerfile                         # Docker image
├── docker-compose.yml                 # Docker Compose
├── docker-run.sh                      # Docker script
├── install.sh                         # Installer
├── requirements.txt                   # Dependencies
├── botlinkmaster.service.template     # Systemd template
├── README.md                          # Main docs
├── QUICKSTART.md                      # Quick guide
├── EXAMPLES.md                        # Examples
├── INSTALLATION_FLOW.md               # Install flow
├── PROJECT_STRUCTURE.md               # Structure docs
├── MILESTONES.md                      # Roadmap
├── CHANGELOG.md                       # Version history
└── LICENSE                            # MIT License
```

### 🚀 Setelah Instalasi

```
botlinkmaster/
├── (all 20 files from Git)
├── .env                               # ✨ Environment vars (CREATED)
├── config.py                          # ✨ Configuration (CREATED)
├── venv/                              # ✨ Virtual environment (CREATED)
├── botlinkmaster.db                   # ✨ Database (CREATED on first run)
├── botlinkmaster.log                  # ✨ Logs (CREATED on running)
└── __pycache__/                       # ✨ Python cache (CREATED)
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
cd botlinkmaster
```
* Run installer (akan meminta sudo otomatis)
```bash
chmod +x install.sh
./install.sh
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

### 2. (Opsional) Edit config.py

```python
# Database
DATABASE_URL = "sqlite:///botlinkmaster.db"

# Timeouts
SSH_TIMEOUT = 30
TELNET_TIMEOUT = 30
```

## 📱 Penggunaan

### Jalankan Bot

```bash
# Activate virtual environment
source venv/bin/activate

# Run bot
python telegram_bot.py
```

### Jalankan sebagai Service

```bash
# Copy service file
sudo cp botlinkmaster.service.template /etc/systemd/system/botlinkmaster.service

# Edit paths
sudo nano /etc/systemd/system/botlinkmaster.service

# Enable and start
sudo systemctl enable botlinkmaster
sudo systemctl start botlinkmaster
sudo systemctl status botlinkmaster
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

## 🐛 Troubleshooting

### Bot tidak bisa start
```bash
# Cek token
cat .env | grep TELEGRAM_BOT_TOKEN

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


## 👥 Credits

* [**Iyankz**](https://github.com/Iyankz) (Developer & Tester)
* [**Gemini**](https://gemini.google.com/) (AI Partner & Technical Assistant)
* [**Claude**](https://claude.ai/) (AI Partner & Technical Assistant)

## 👥 Contributors


- [Iyankz](https://github.com/Iyankz) - Developer
- [Gemini](https://gemini.google.com/) - AI Assistant
- [Claude](https://claude.ai/) - AI Assistant

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

**BotLinkMaster v4.0** - Monitoring Perangkat Jaringan Menjadi Mudah 🚀
