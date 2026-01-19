# BotLinkMaster v4.7.0

Bot Telegram untuk monitoring perangkat jaringan (router dan switch) dengan dukungan multi-vendor dan optical power monitoring.

![Release](https://img.shields.io/github/v/release/Iyankz/botlinkmaster?style=for-the-badge)
![Release Date](https://img.shields.io/github/release-date/Iyankz/botlinkmaster?style=for-the-badge)
![Last Commit](https://img.shields.io/github/last-commit/Iyankz/botlinkmaster?style=for-the-badge)
![Stability](https://img.shields.io/badge/Release-Stable-success?style=for-the-badge)
![Non Breaking](https://img.shields.io/badge/API-Non--Breaking-success?style=for-the-badge)
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

> 📌 **Note:** OLT support akan tersedia di v5.x.x

## 📋 Requirements

- **OS:** Ubuntu 22.04 LTS 
- **RAM:** Minimum 1GB (2GB recommended)
- **Storage:** Minimum 2GB free space
- **Network:** Akses internet untuk Telegram API dan Akses ke Perangkat
- **Access:** Root/sudo privileges
- **Python** Versi 3.8+
- **pip3**
- **git** (opsional, untuk clone)


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
2. kirim `/start`di group
3. Kirim `/myid` di group
4. Group ID akan ditampilkan (angka negatif)

---
## Perintah Bot

### Info & Bantuan
| Command | Deskripsi |
|---------|-----------|
| `/start` | Info bot |
| `/help` | Bantuan lengkap |
| `/help2` | Contoh penggunaan |
| `/myid` | Chat ID Anda |
| `/time` | Waktu saat ini |

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
| `/interfaces [device]` | List semua interface |
| `/interfaces [device] [page]` | Interface dengan pagination |
| `/cek [device] [interface]` | Cek status interface |
| `/redaman [device] [interface]` | Cek optical power |

### Konfigurasi
| Command | Deskripsi |
|---------|-----------|
| `/vendors` | Daftar vendor |
| `/timezone` | Info timezone |
| `/settz [timezone]` | Set timezone |

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
protocol: telnet
port: 2202
vendor: mikrotik
```

### Cek Interface list
```
/interfaces [device]
```
### Cek Status Interface
```
/cek [device] [interface]
```
### Cek Optical Power
```
/redaman [device] [interface]
```

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

### Contoh Timezone per Benua

**Asia:**

- `Asia/Jakarta` - WIB (UTC+7)
- `Asia/Makassar` - WITA (UTC+8)
- `Asia/Jayapura` - WIT (UTC+9)
- `Asia/Singapore` - Singapore (UTC+8)
- `Asia/Tokyo` - Japan (UTC+9)

**Europe:**

- `Europe/London` - UK (UTC+0/+1)
- `Europe/Paris` - France (UTC+1/+2)
- `Europe/Berlin` - Germany (UTC+1/+2)

**America:**

- `America/New_York` - US Eastern (UTC-5/-4)
- `America/Los_Angeles` - US Pacific (UTC-8/-7)
- `America/Sao_Paulo` - Brazil (UTC-3)

**Australia:**

- `Australia/Sydney` - Sydney (UTC+10/+11)
- `Australia/Perth` - Perth (UTC+8)

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

## Troubleshooting

### Error: "no matching host key type found"
Ini sudah di-fix di v4.6.0. Bot otomatis mencoba algoritma legacy untuk perangkat lama.

### MikroTik Interface Tidak Muncul
Pastikan:
1. Vendor diset ke `mikrotik`
2. User memiliki akses ke `/interface print`

### Data Optical Tidak Muncul
1. Pastikan interface memiliki SFP/transceiver
2. Untuk MikroTik, gunakan nama interface yang benar (sesuai interface list)

### Error: Connection Timeout

1. Pastikan IP dan port benar
2. Cek firewall: `sudo ufw status`
3. Pastikan SSH/Telnet aktif di perangkat
4. Test manual: `ssh -p PORT user@host` atau `telnet host port`

### Error: Authentication Failed

1. Cek username dan password
2. Pastikan user memiliki akses SSH/Telnet
3. Beberapa perangkat perlu enable password

## Systemd Service

```bash
sudo systemctl start botlinkmaster    # Start
sudo systemctl stop botlinkmaster     # Stop
sudo systemctl restart botlinkmaster  # Restart
sudo systemctl status botlinkmaster   # Status
sudo journalctl -u botlinkmaster -f   # Log
```

## 📝 Changelog

### v4.6.1 — Stabilitas MikroTik SSH
**Release Type:** Bug Fix (Non-breaking)

#### Fixed
- Memperbaiki masalah **partial SSH output pada perangkat MikroTik**
  (contoh: hanya sebagian interface yang terbaca).
- Mekanisme pembacaan output SSH kini menggunakan **idle-time based read**
  untuk memastikan seluruh data diterima sebelum parsing.

#### Improved
- Stabilitas pengambilan data interface pada MikroTik dengan jumlah interface banyak.
- Keandalan monitoring tanpa memerlukan konfigurasi tambahan di sisi perangkat.

#### Notes
- Tidak ada perubahan API.
- Tidak memengaruhi vendor lain (Cisco, Huawei, Generic).
- Aman untuk upgrade dari v4.6.1.
  
### v4.6.0 — Initial Stable Release
**Release Type:** Stable

#### Added
- Dukungan multi-vendor (MikroTik, Cisco, Huawei, Generic).
- Monitoring status interface (up/down).
- Optical power monitoring (RX/TX).
- Dukungan koneksi SSH dan Telnet.
- Kompatibilitas dengan perangkat legacy.

#### Notes
- Fokus pada kestabilan dan kebutuhan operasional NOC.

## Update dari Versi Sebelumnya

### Step 1: Backup

```bash
cd ~/botlinkmaster

# Backup database
cp botlinkmaster.db botlinkmaster.db.bak

# Backup config
cp .env .env.bak
```

### Step 2: Stop Service

```bash
sudo systemctl stop botlinkmaster
```

### Step 3: Replace File

Replace file-file berikut:

- `telegram_bot.py`
```bash
cd ~/botlinkmaster
wget -O telegram_bot.py https://raw.githubusercontent.com/Iyankz/botlinkmaster/main/telegram_bot.py
```
- `botlinkmaster.py`
```bash
cd ~/botlinkmaster
wget -O botlinkmaster.py https://raw.githubusercontent.com/Iyankz/botlinkmaster/main/botlinkmaster.py
```
- `database.py`
```bash
cd ~/botlinkmaster
wget -O database.py https://raw.githubusercontent.com/Iyankz/botlinkmaster/main/database.py
```
- `vendor_commands.py`
```bash
cd ~/botlinkmaster
wget -O vendor_commands.py https://raw.githubusercontent.com/Iyankz/botlinkmaster/main/vendor_commands.py
```

### Step 4: Restart Service

```bash
sudo systemctl restart botlinkmaster
```

Database akan otomatis migrasi ke schema baru.

---

## Quick Reference

### File Locations

| File | Path |
|------|------|
| Bot files | `~/botlinkmaster/` |
| Database | `~/botlinkmaster/botlinkmaster.db` |
| Config | `~/botlinkmaster/.env` |
| Log | `~/botlinkmaster/botlinkmaster.log` |
| Service | `/etc/systemd/system/botlinkmaster.service` |

## Kontribusi

Pull request dan issue welcome di GitHub repository.

---

**Catatan:** Untuk bantuan lebih lanjut, gunakan `/help` dan `/help2` di bot.

## Dibuat dengan ❤️ oleh [Iyankz](https://github.com/Iyankz) & [Claude](https://claude.ai)

- **Iyankz** (Inisiator , Developer & Tester)
- **Claude** (AI Partner & Technical Assistant)

## Lisensi

Proyek ini dilisensikan di bawah **MIT License** - lihat file [LICENSE](LICENSE) untuk detailnya.

## Dukung Proyek Ini

Jika repositori ini membantu memudahkan pekerjaan Anda atau bermanfaat bagi tim IT Anda, mohon berikan bintang (Star) ⭐ pada repositori ini sebagai bentuk dukungan bagi kami untuk terus mengembangkan script ini.
