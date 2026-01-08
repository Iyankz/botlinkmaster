# 🤖 BotLinkMaster v4.1.0 - Service Edition

Bot monitoring perangkat jaringan via SSH/Telnet dengan fitur **auto-start service**

## ⚡ Mulai Cepat (3 Perintah)

```bash
# 1. Install (otomatis setup service)
chmod +x install-complete.sh
sudo ./install-complete.sh

# 2. Tambahkan bot token
sudo nano .env
# Isi: TELEGRAM_BOT_TOKEN=token_anda

# 3. Jalankan service
sudo systemctl start botlinkmaster
```

**Selesai!** ✅ Bot berjalan di background, otomatis start saat boot.

---

## 📋 Requirements

### System Requirements

**Minimum:**
- **OS:** Ubuntu 20.04+, Debian 10+, CentOS 7+, RHEL 7+, Fedora 30+, Arch Linux
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
- python3-pip
- python3-venv
- git
- curl, wget
- openssh-client
- telnet
- tzdata

**Python Packages (otomatis terinstall oleh installer):**
```
paramiko==3.4.0          # Untuk koneksi SSH
python-telegram-bot==20.7 # Untuk Telegram Bot
SQLAlchemy==2.0.25       # Untuk database ORM
click==8.1.7             # Untuk CLI
rich==13.7.0             # Untuk CLI formatting
python-dotenv==1.0.0     # Untuk .env file
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

**Device yang Didukung:**
- Cisco IOS/IOS-XE
- Cisco NX-OS
- Juniper JunOS
- HP/Aruba
- MikroTik
- Generic SSH/Telnet devices

---

## 📋 Penggunaan Sehari-hari

```bash
# Cek status
sudo systemctl status botlinkmaster

# Lihat log (realtime)
sudo journalctl -u botlinkmaster -f

# Restart jika perlu
sudo systemctl restart botlinkmaster
```

---

## 🎮 Manajemen Mudah dengan `botctl`

```bash
sudo ./botctl start      # Jalankan service
sudo ./botctl stop       # Hentikan service  
sudo ./botctl restart    # Restart service
sudo ./botctl status     # Cek status
sudo ./botctl logs       # Lihat log
```

---

## ✨ Fitur Utama

- ✅ **SSH & Telnet** support
- ✅ **Auto-start** saat boot (systemd)
- ✅ **Background** service
- ✅ **Auto-restart** jika crash
- ✅ **Logging terintegrasi** (journalctl)
- ✅ **Batas resource** (CPU/Memory)
- ✅ **Database** (SQLAlchemy ORM)
- ✅ **Telegram Bot** interface
- ✅ **CLI tools** included
- ✅ **Pembatasan Chat ID** untuk keamanan

---

## 🤖 Perintah Bot

| Perintah | Keterangan |
|---------|-------------|
| `/start` | Pesan selamat datang |
| `/help` | Bantuan lengkap |
| `/myid` | Dapatkan Chat ID Anda |
| `/list` | Daftar semua perangkat |
| `/add` | Tambah perangkat baru |
| `/device <nama>` | Detail perangkat |
| `/cek <device> <interface>` | Cek status interface |
| `/delete <nama>` | Hapus perangkat |

---

## 📝 Menambah Perangkat

```
/add
nama: router-1
host: 192.168.1.1
username: admin
password: pass123
protocol: ssh
port: 22
description: Router utama
location: Data center
```

---

## 🔒 Kontrol Akses (Opsional)

Batasi bot hanya untuk pengguna tertentu:

```bash
# 1. Dapatkan Chat ID Anda
# Kirim /myid ke bot

# 2. Edit .env
sudo nano .env

# Tambahkan:
ALLOWED_CHAT_IDS=123456789,987654321

# 3. Restart
sudo systemctl restart botlinkmaster
```

---

## 🛠️ Manajemen Service

### Perintah System

```bash
# Jalankan service
sudo systemctl start botlinkmaster

# Hentikan service  
sudo systemctl stop botlinkmaster

# Restart service
sudo systemctl restart botlinkmaster

# Cek status
sudo systemctl status botlinkmaster

# Enable auto-start (sudah enabled oleh installer)
sudo systemctl enable botlinkmaster

# Disable auto-start
sudo systemctl disable botlinkmaster

# Lihat log (realtime)
sudo journalctl -u botlinkmaster -f

# Lihat log (100 baris terakhir)
sudo journalctl -u botlinkmaster -n 100

# Lihat log (hari ini)
sudo journalctl -u botlinkmaster --since today
```

### Perintah botctl

```bash
# Buat executable (pertama kali)
chmod +x botctl

# Jalankan
sudo ./botctl start

# Hentikan
sudo ./botctl stop

# Restart
sudo ./botctl restart

# Status
sudo ./botctl status

# Log (realtime)
sudo ./botctl logs

# Enable auto-start
sudo ./botctl enable

# Disable auto-start
sudo ./botctl disable

# Uninstall service
sudo ./botctl uninstall
```

---

## 📊 Cek Apakah Berjalan

```bash
# Metode 1: Status
sudo systemctl status botlinkmaster
# Cari: Active: active (running)

# Metode 2: Process
ps aux | grep telegram_bot.py

# Metode 3: botctl
sudo ./botctl status
```

---

## 🔧 Update Konfigurasi

```bash
# 1. Edit .env
sudo nano .env

# 2. Restart service
sudo systemctl restart botlinkmaster

# 3. Verifikasi
sudo systemctl status botlinkmaster
```

---

## 📦 Update Kode Bot

```bash
# 1. Hentikan service
sudo systemctl stop botlinkmaster

# 2. Pull update
git pull

# 3. Update dependencies (jika perlu)
source venv/bin/activate
pip install -r requirements.txt

# 4. Jalankan service
sudo systemctl start botlinkmaster
```

---

## 🐛 Troubleshooting

### Service tidak mau start

```bash
# Cek status
sudo systemctl status botlinkmaster

# Lihat log
sudo journalctl -u botlinkmaster -n 100

# Cek .env
cat .env | grep TOKEN

# Jalankan diagnostic
python diagnose.py
```

### Bot tidak merespon

```bash
# Restart service
sudo systemctl restart botlinkmaster

# Cek log
sudo journalctl -u botlinkmaster -f

# Test manual
sudo systemctl stop botlinkmaster
source venv/bin/activate
python telegram_bot.py
```

### Lihat error saja

```bash
sudo journalctl -u botlinkmaster -p err
```

---

## 📚 Dokumentasi

- **[SERVICE_GUIDE.md](SERVICE_GUIDE.md)** - Panduan service lengkap
- **[QUICKSTART_SERVICE.md](QUICKSTART_SERVICE.md)** - Panduan mulai cepat
- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Perbaiki masalah umum
- **[EXAMPLES.md](EXAMPLES.md)** - Contoh penggunaan

---

## 🔄 Informasi System Service

**File service:** `/etc/systemd/system/botlinkmaster.service`

**Pengaturan:**
- Auto-restart jika gagal
- Maksimal 512MB memory
- Maksimal 100% CPU (1 core)
- Log ke systemd journal
- Security hardening enabled

**Lihat konfigurasi service:**
```bash
systemctl cat botlinkmaster
```

---

## 📁 Struktur File

```
botlinkmaster/
│
├── README.md                    # ⭐ Dokumentasi utama (harus di root!)
├── README_ID.md                 # ⭐ Dokumentasi Indonesia (di root!)
│
├── 🐍 Core Python Modules
│   ├── telegram_bot.py          # Bot utama
│   ├── botlinkmaster.py         # SSH/Telnet handler
│   ├── database.py              # Database ORM
│   └── cli.py                   # CLI tool
│
├── 🔧 Service & Instalasi (v4.1.0)
│   ├── install-complete.sh      # Installer lengkap (GUNAKAN INI!)
│   ├── botctl                   # Service manager tool
│   ├── setup-service.sh         # Setup service manual
│   ├── install.sh               # Legacy installer
│   └── botlinkmaster.service    # Systemd service file
│
├── 🔍 Tool Diagnostic (v4.1.0)
│   ├── diagnose.py              # Diagnostic lengkap
│   └── test_bot.py              # Test koneksi
│
├── 🐳 Docker
│   ├── Dockerfile               # Docker image
│   ├── docker-compose.yml       # Docker Compose
│   └── docker-run.sh            # Docker script
│
├── ⚙️ Konfigurasi
│   ├── .env                     # Konfigurasi (TAMBAHKAN TOKEN!)
│   ├── .env.example             # Template konfigurasi
│   ├── config.py                # Config Python
│   └── requirements.txt         # Dependencies Python
│
├── 📚 Dokumentasi (Semua di root level)
│   │
│   ├── 🇮🇩 Indonesia
│   │   ├── QUICKSTART_ID.md
│   │   ├── INSTALL_CARD_ID.txt
│   │   └── RELEASE_NOTES_v4.1.0_ID.md
│   │
│   ├── 🇬🇧 English
│   │   ├── README_SERVICE.md
│   │   ├── SERVICE_GUIDE.md
│   │   ├── BOTCTL_GUIDE.md
│   │   ├── REQUIREMENTS.md
│   │   ├── TROUBLESHOOTING.md
│   │   ├── QUICKSTART_SERVICE.md
│   │   ├── DEPLOYMENT_SUMMARY.md
│   │   ├── CHANGELOG.md
│   │   └── Dan lainnya...
│   │
│   └── 📄 Reference Cards
│       ├── INSTALL_CARD.txt
│       ├── REQUIREMENTS_CARD.txt
│       └── RELEASE_v4.1.0.txt
│
├── 📋 Meta Files
│   ├── .gitignore
│   ├── LICENSE
│   └── VERSION (4.1.0)
│
└── 🚀 Runtime Files (dibuat otomatis saat install)
    ├── venv/                    # Virtual environment
    ├── botlinkmaster.db         # Database SQLite
    ├── botlinkmaster.log        # Log file
    └── __pycache__/             # Python cache

CATATAN PENTING:
📌 Semua file dokumentasi ada di ROOT DIRECTORY (tidak di subfolder)
📌 README.md HARUS di root agar GitHub bisa tampilkan otomatis
📌 Struktur di atas hanya pengelompokan visual, bukan folder nyata
```

**File Penting di Root:**
- 🔑 **README.md** - Dokumentasi utama (tampil di GitHub)
- 🔑 **README_ID.md** - Dokumentasi Indonesia
- 🔑 **install-complete.sh** - Installer utama
- 🎮 **botctl** - Tool manage service
- 📝 **diagnose.py** - Tool diagnostic
- ⚙️ **.env** - File konfigurasi

---

## ✅ Checklist Instalasi

Setelah `install-complete.sh`:

- [ ] Service terinstall: `systemctl status botlinkmaster`
- [ ] Service enabled: `systemctl is-enabled botlinkmaster`
- [ ] .env ada: `ls -la .env`
- [ ] Token ditambahkan: `cat .env | grep TOKEN`
- [ ] Service dijalankan: `sudo systemctl start botlinkmaster`
- [ ] Bot merespon di Telegram: `/start`
- [ ] Log berfungsi: `sudo journalctl -u botlinkmaster -f`

---

## 🆘 Bantuan Cepat

**Bot tidak merespon?**
```bash
sudo systemctl restart botlinkmaster
sudo journalctl -u botlinkmaster -f
```

**Service tidak start?**
```bash
sudo journalctl -u botlinkmaster -n 50
python diagnose.py
```

**Lupa perintah?**
```bash
sudo ./botctl status
```

---

## 🎯 Referensi Cepat

| Tugas | Perintah |
|------|---------|
| **Jalankan** | `sudo systemctl start botlinkmaster` |
| **Hentikan** | `sudo systemctl stop botlinkmaster` |
| **Restart** | `sudo systemctl restart botlinkmaster` |
| **Status** | `sudo systemctl status botlinkmaster` |
| **Log** | `sudo journalctl -u botlinkmaster -f` |
| **Edit config** | `sudo nano .env` |
| **Diagnostic** | `python diagnose.py` |

---

## 👥 Kontributor

- [Iyankz](https://github.com/Iyankz) - Developer
- [Gemini](https://gemini.google.com/) - AI Assistant
- [Claude](https://claude.ai/) - AI Assistant

---

## 📄 Lisensi

MIT License - Lihat [LICENSE](LICENSE)

---

## 🚀 Ringkasan

**Install sekali:**
```bash
sudo ./install-complete.sh     # Setup semuanya
sudo nano .env                 # Tambah token
sudo systemctl start botlinkmaster
```

**Penggunaan harian:**
```bash
sudo systemctl status botlinkmaster
sudo journalctl -u botlinkmaster -f
```

**Auto-start:** ✅ Sudah enabled  
**Background:** ✅ Service mode  
**Restart otomatis:** ✅ Otomatis  

---

**BotLinkMaster v4.1.0** - Deployment tanpa ribet! 🎉
