# BotLinkMaster v4.8.7

Bot Telegram untuk monitoring perangkat jaringan (router dan switch) dengan dukungan multi-vendor dan optical power monitoring.

![Version](https://img.shields.io/badge/Version-4.8.7-blue?style=for-the-badge)
![Release](https://img.shields.io/github/v/release/Iyankz/botlinkmaster?style=for-the-badge)
![Release Date](https://img.shields.io/github/release-date/Iyankz/botlinkmaster?style=for-the-badge)
![Last Commit](https://img.shields.io/github/last-commit/Iyankz/botlinkmaster?style=for-the-badge)
![Stability](https://img.shields.io/badge/Release-Stable-success?style=for-the-badge)
![NOC Ready](https://img.shields.io/badge/NOC-Ready-critical?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge&logo=python)
![Ubuntu](https://img.shields.io/badge/Ubuntu-22.04%2B-orange?style=for-the-badge&logo=ubuntu)
![Telegram Bot](https://img.shields.io/badge/Telegram-Bot-blue?style=for-the-badge&logo=telegram)
![Protocol](https://img.shields.io/badge/Protocol-SSH%20%7C%20Telnet-darkgreen?style=for-the-badge)
![Multi Vendor](https://img.shields.io/badge/Vendor-18%2B-success?style=for-the-badge)
![License](https://img.shields.io/github/license/Iyankz/botlinkmaster?style=for-the-badge)


## Fitur Utama

- ✅ **18 Vendor Support** - Cisco, Huawei, ZTE, Juniper, MikroTik, Nokia, dll
- ✅ **Optical Power Monitoring** - Cek TX/RX power dengan level indicator
- ✅ **SSH & Telnet** - Dukungan kedua protokol dengan custom port
- ✅ **Multi Chat ID** - Support user dan group Telegram
- ✅ **Timezone IANA** - Konfigurasi timezone dengan format standar
- ✅ **Interface Monitoring** - Cek status UP/DOWN dan deskripsi
- ✅ **Port Forwarding** - Satu IP bisa untuk multiple device
- ✅ **Auto Update** - Version checking, auto backup, dan rollback support

> 📌 **Note:** OLT support akan tersedia di v5.x.x

---

## 📋 Requirements

- **OS:** Ubuntu 22.04 LTS atau Debian 11+
- **RAM:** Minimum 1GB (2GB recommended)
- **Storage:** Minimum 2GB free space
- **Network:** Akses internet untuk Telegram API dan Akses ke Perangkat
- **Access:** Root/sudo privileges
- **Python:** Versi 3.8+
- **pip3**
- **git** (opsional, untuk clone)

---

## Instalasi

### Cara 1: Otomatis (Recommended)

```bash
cd ~
git clone https://github.com/Iyankz/botlinkmaster.git
cd botlinkmaster
chmod +x install.sh
./install.sh
```

Edit konfigurasi:
```bash
nano .env
```

Start service:
```bash
sudo systemctl start botlinkmaster
sudo systemctl status botlinkmaster
```

### Cara 2: Manual

```bash
# 1. Install system packages
sudo apt update
sudo apt install -y python3 python3-pip python3-venv

# 2. Clone repository
cd ~
git clone https://github.com/Iyankz/botlinkmaster.git
cd botlinkmaster

# 3. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 4. Install dependencies
pip install python-telegram-bot python-dotenv paramiko pytz

# 5. Configure
cp .env.example .env
nano .env

# 6. Test
python telegram_bot.py
```

---

## Konfigurasi .env

```env
# Telegram Bot Token (dari @BotFather)
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz

# Allowed Chat IDs (pisahkan dengan koma)
# Kosongkan untuk allow semua
ALLOWED_CHAT_IDS=216481118,-1001234567890

# Timezone (default: Asia/Jakarta)
TIMEZONE=Asia/Jakarta
```

---

## Update dari Versi Sebelumnya

### Metode 1: Auto Update (Recommended)

```bash
cd ~/botlinkmaster
chmod +x update.sh
./update.sh
```

Script akan otomatis:
- ✅ Cek versi lokal vs remote (via file `VERSION`)
- ✅ Backup semua file sebelum update
- ✅ Download file terbaru dari GitHub
- ✅ Preserve database dan konfigurasi
- ✅ Restart service

### Opsi Update Script

```bash
# Cek update saja (tanpa install)
./update.sh --check

# Force update tanpa cek versi
./update.sh --force

# Rollback ke backup terakhir
./update.sh --rollback

# Rollback ke backup spesifik
./update.sh --rollback backup_20250122_123456

# Bantuan
./update.sh --help
```

### Metode 2: Manual Update

**Dari v4.5.x / v4.6.x / v4.7.x / v4.8.x ke v4.8.7:**

```bash
cd ~/botlinkmaster

# 1. Stop service
sudo systemctl stop botlinkmaster

# 2. Backup
cp botlinkmaster.db botlinkmaster.db.bak
cp .env .env.bak

# 3. Update files
wget -O telegram_bot.py https://raw.githubusercontent.com/YOUR_USERNAME/botlinkmaster/main/telegram_bot.py
wget -O botlinkmaster.py https://raw.githubusercontent.com/YOUR_USERNAME/botlinkmaster/main/botlinkmaster.py
wget -O database.py https://raw.githubusercontent.com/YOUR_USERNAME/botlinkmaster/main/database.py
wget -O vendor_commands.py https://raw.githubusercontent.com/YOUR_USERNAME/botlinkmaster/main/vendor_commands.py
wget -O timezone_config.py https://raw.githubusercontent.com/YOUR_USERNAME/botlinkmaster/main/timezone_config.py

# 4. Restart
sudo systemctl restart botlinkmaster
sudo systemctl status botlinkmaster
```

### File yang DIUPDATE vs DIPERTAHANKAN

| Update (Replace) | Preserve (Jangan Replace) |
|------------------|---------------------------|
| telegram_bot.py | botlinkmaster.db |
| botlinkmaster.py | .env |
| vendor_commands.py | timezone.conf |
| database.py | botlinkmaster.log |
| timezone_config.py | |
| update.sh | |
| install.sh | |
| README.md | |
| CHANGELOG.md | |
| VERSION | |

---

## Multiple Chat ID & Group

Bot mendukung multiple user dan group. Tambahkan Chat ID di `.env`:

```env
# Single user
ALLOWED_CHAT_IDS=216481118

# Multiple users
ALLOWED_CHAT_IDS=216481118,123456789

# Users dan groups (group ID negatif)
ALLOWED_CHAT_IDS=216481118,-1001234567890,-1009876543210
```

### Cara Mendapatkan Chat ID

**Untuk User:**
1. Kirim `/myid` ke bot setelah bot berjalan, atau
2. Kirim pesan ke `@userinfobot`

**Untuk Group:**
1. Tambahkan bot ke group
2. Kirim `/start` di group
3. Kirim `/myid` di group
4. Group ID akan ditampilkan (angka negatif)

---

## Perintah Bot

### Info & Bantuan
| Command | Deskripsi |
|---------|-----------|
| `/start` | Info bot + Chat ID Anda |
| `/help` | Bantuan lengkap |
| `/help2` | Contoh penggunaan |
| `/myid` | Chat ID lengkap |
| `/time` | Waktu saat ini |

> 💡 **Tip:** Chat ID langsung muncul saat `/start`, tidak perlu `/myid` lagi

### Device Management
| Command | Deskripsi |
|---------|-----------|
| `/add` | Tambah perangkat |
| `/list` | Daftar perangkat |
| `/device [nama]` | Detail perangkat |
| `/delete [nama]` | Hapus perangkat |

### Monitoring
| Command | Deskripsi |
|---------|-----------|
| `/int [device]` | List semua interface |
| `/int [device] [page]` | Interface dengan pagination |
| `/cek [device] [interface]` | Cek status interface |
| `/redaman [device] [interface]` | Cek optical power |

> 💡 **Alias:** `/int` = `/interfaces` (keduanya sama, /int lebih singkat)

### Konfigurasi
| Command | Deskripsi |
|---------|-----------|
| `/vendors` | Daftar vendor |
| `/timezone` | Info timezone |
| `/settz [timezone]` | Set timezone |

---

## Contoh Penggunaan

### Tambah Perangkat dengan SSH

```
/add
nama: router-core
host: 192.168.1.1
username: admin
password: admin123
protocol: ssh
port: 22
vendor: cisco_ios
description: Router Core Kantor Pusat
```

### Tambah Perangkat dengan Telnet

```
/add
nama: switch-old
host: 192.168.1.10
username: admin
password: admin123
protocol: telnet
port: 23
vendor: huawei
```

### Tambah Perangkat dengan Port Forward

```
/add
nama: router-cabang-1
host: 10.0.0.1
username: admin
password: admin123
protocol: ssh
port: 2201
vendor: cisco_nxos

/add
nama: router-cabang-2
host: 10.0.0.1
username: admin
password: admin123
protocol: ssh
port: 2202
vendor: mikrotik
```

### Cek Interface List
```
/int router-1
/int router-1 2
```

> 💡 Bisa juga pakai `/interfaces router-1` (sama dengan /int)

### Cek Status Interface
```
/cek router-1 Gi0/0
```

### Cek Optical Power
```
/redaman router-1 Gi0/0
```

---

## Vendor yang Didukung

| Vendor | Kode | Notes |
|--------|------|-------|
| Cisco IOS/IOS-XE | `cisco_ios` | Router & Switch |
| Cisco NX-OS | `cisco_nxos` | Nexus |
| Huawei VRP | `huawei` | Router & Switch |
| ZTE | `zte` | Router & Switch |
| Juniper JunOS | `juniper` | Router & Switch |
| MikroTik RouterOS | `mikrotik` | RouterOS v6/v7 |
| Nokia SR-OS | `nokia` | Service Router |
| HP/Aruba | `hp_aruba` | ProCurve & Aruba |
| H3C Comware | `h3c` | H3C Switch |
| Ruijie | `ruijie` | Ruijie Switch |
| FiberHome | `fiberhome` | FH Switch |
| DCN | `dcn` | DCN Switch |
| BDCOM | `bdcom` | BDCOM Switch |
| Raisecom | `raisecom` | Raisecom |
| FS.COM | `fs` | FS Switch |
| Allied Telesis | `allied` | AT Switch |
| Datacom | `datacom` | Datacom Switch |
| Generic | `generic` | Fallback |

---

## Konfigurasi Timezone

Default timezone: `Asia/Jakarta`

### Contoh Timezone Indonesia

- `Asia/Jakarta` - WIB (UTC+7)
- `Asia/Makassar` - WITA (UTC+8)
- `Asia/Jayapura` - WIT (UTC+9)

### Contoh Timezone Lainnya

- `Asia/Singapore` - Singapore (UTC+8)
- `Asia/Tokyo` - Japan (UTC+9)
- `Europe/London` - UK (UTC+0/+1)
- `America/New_York` - US Eastern (UTC-5/-4)

### Set Timezone via Bot

```
/settz Asia/Jakarta
```

Lihat daftar timezone:
```
/timezone
/timezone Asia
/timezone Europe
```

---

## Troubleshooting

### Service tidak jalan

```bash
# Cek status
sudo systemctl status botlinkmaster

# Cek log
sudo journalctl -u botlinkmaster -f

# Restart
sudo systemctl restart botlinkmaster
```

### Error: Connection Timeout

1. Pastikan IP dan port benar
2. Cek firewall: `sudo ufw status`
3. Pastikan SSH/Telnet aktif di perangkat
4. Test manual: `ssh -p PORT user@host`

### Error: Authentication Failed

1. Cek username dan password
2. Pastikan user memiliki akses SSH/Telnet
3. Beberapa perangkat perlu enable password

---

## Systemd Service

```bash
sudo systemctl start botlinkmaster    # Start
sudo systemctl stop botlinkmaster     # Stop
sudo systemctl restart botlinkmaster  # Restart
sudo systemctl status botlinkmaster   # Status
sudo systemctl enable botlinkmaster   # Auto-start on boot
sudo journalctl -u botlinkmaster -f   # Live log
```

---

## 📝 [Changelog](CHANGELOG.md)

### v4.8.7 — Bug Fixes & Compatibility
**Release Type:** Bug Fix (Non-breaking)

#### Fixed
- **MikroTik CRS326-24S+2Q+RM**: SSH algorithm compatibility untuk RouterOS 7.16.x
- **MikroTik**: Extended timeout (30s → 60s) untuk switch dengan banyak interface
- **Huawei CE6855**: Menggunakan `display interface description` untuk list interface yang lebih akurat
- **Cisco IOS**: Perbaikan command `show interface brief` (sebelumnya salah: `show ip interface brief`)

#### Improved
- Prompt detection untuk berbagai vendor
- Hard timeout meningkat untuk perangkat dengan respons lambat
- Konsistensi versi di semua file

#### Notes
- Tidak ada perubahan API
- Aman untuk upgrade dari v4.5.x, v4.6.x, v4.7.x, v4.8.x
- Database compatible dengan versi sebelumnya

---

## Quick Reference

### File Locations

| File | Path | Keterangan |
|------|------|------------|
| Bot files | `~/botlinkmaster/` | Semua file bot |
| Database | `~/botlinkmaster/botlinkmaster.db` | SQLite database |
| Config | `~/botlinkmaster/.env` | Konfigurasi (token, chat id) |
| Log | `~/botlinkmaster/botlinkmaster.log` | Log file |
| Version | `~/botlinkmaster/VERSION` | File versi untuk update |
| Changelog | `~/botlinkmaster/CHANGELOG.md` | History perubahan |
| Service | `/etc/systemd/system/botlinkmaster.service` | Systemd service |
| Backup | `~/botlinkmaster/backup_*/` | Backup dari update.sh |

---

## Kontribusi

Pull request dan issue welcome di GitHub repository.

---

**Catatan:** Untuk bantuan lebih lanjut, gunakan `/help` dan `/help2` di bot.

## Dibuat dengan ❤️ oleh [Iyankz](https://github.com/Iyankz)

## Lisensi

Proyek ini dilisensikan di bawah **MIT License** - lihat file [LICENSE](LICENSE) untuk detailnya.

## Dukung Proyek Ini

Jika repositori ini membantu memudahkan pekerjaan Anda, mohon berikan bintang (Star) ⭐ pada repositori ini.
