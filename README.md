# BotLinkMaster v4.5

Bot Telegram untuk monitoring perangkat jaringan dengan dukungan multi-vendor dan optical power (redaman).

![Version](https://img.shields.io/badge/version-4.5.0-blue)
![Python](https://img.shields.io/badge/python-3.8+-green)
![License](https://img.shields.io/badge/license-MIT-orange)
![Ubuntu: 22.04+](https://img.shields.io/badge/Ubuntu-22.04+-orange.svg)

## Fitur Utama

- ✅ **22+ Vendor Support** - Cisco, Huawei, ZTE, Juniper, MikroTik, Nokia, dll
- ✅ **OLT/ONU Monitoring** - Cek redaman ONU pada ZTE, Huawei, BDCOM, FiberHome OLT
- ✅ **SSH & Telnet** - Dukungan kedua protokol dengan custom port
- ✅ **Multi Chat ID** - Support user dan group Telegram
- ✅ **Timezone IANA** - Konfigurasi timezone dengan format standar
- ✅ **Interface Monitoring** - Cek status UP/DOWN dan deskripsi interface
- ✅ **Port Forwarding** - Satu IP bisa untuk multiple device dengan port berbeda

```
## 📋 Requirements

- **OS:** Ubuntu 22.04 LTS atau lebih baru
- **RAM:** Minimum 1GB (2GB recommended)
- **Storage:** Minimum 2GB free space
- **Network:** Akses internet untuk Telegram API dan Akses ke Perangkat
- **Access:** Root/sudo privileges
- **Python** Versi 3.8+
- **pip3**
- **git** (opsional, untuk clone)

---

## Instalasi

Ada 2 cara instalasi: **Otomatis** (recommended) atau **Manual**.

---

### Cara 1: Instalasi Otomatis (Recommended)

#### Step 1: Download dan Extract

**Opsi A - Menggunakan Git:**

```bash
# Masuk ke home directory
cd ~

# Clone repository
git clone https://github.com/Iyankz/botlinkmaster.git

# Masuk ke folder
cd botlinkmaster

# Lanjut ke Step 2
```

**Opsi B - Download Manual (tanpa Git):**

```bash
# Masuk ke home directory
cd ~

# Download file (ganti URL sesuai lokasi file)
wget https://github.com/Iyankz/botlinkmaster/archive/refs/heads/main.zip

# Extract
unzip botlinkmaster.zip

# Masuk ke folder
cd botlinkmaster

# Lanjut ke Step 2
```

**Opsi C - Upload Manual via SCP/SFTP:**

```bash
# Dari komputer lokal, upload ke server
scp -r botlinkmaster/ user@server:~/

# Login ke server
ssh user@server

# Masuk folder
cd ~/botlinkmaster

# Lanjut ke Step 2
```

#### Step 2: Jalankan Script Instalasi

```bash
# Beri permission execute pada install.sh
chmod +x install.sh

# Jalankan installer
./install.sh
```

Script akan otomatis:

- Install Python dependencies
- Membuat virtual environment
- Membuat file .env
- Membuat systemd service

#### Step 3: Konfigurasi Bot Token

```bash
# Edit file .env
nano .env
```

Isi dengan token dari @BotFather:

```env
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
ALLOWED_CHAT_IDS=216481118
TIMEZONE=Asia/Jakarta
```

Simpan: `Ctrl+X`, lalu `Y`, lalu `Enter`

#### Step 4: Dapatkan Chat ID

1. Buka Telegram, cari `@userinfobot`
2. Kirim `/start`
3. Bot akan menampilkan Chat ID Anda
4. Masukkan Chat ID ke `ALLOWED_CHAT_IDS` di file `.env`

#### Step 5: Jalankan Bot

```bash
# Start service
sudo systemctl start botlinkmaster

# Cek status
sudo systemctl status botlinkmaster

# Enable auto-start saat boot
sudo systemctl enable botlinkmaster
```

#### Step 6: Verifikasi

1. Buka Telegram
2. Cari bot Anda (sesuai nama yang dibuat di @BotFather)
3. Kirim `/start`
4. Jika bot merespon, instalasi berhasil! 🎉

---

### Cara 2: Instalasi Manual (Step by Step)

#### Step 1: Install System Packages

```bash
# Update repository
sudo apt update

# Install Python dan pip
sudo apt install -y python3 python3-pip python3-venv git
```

#### Step 2: Buat Folder dan Download Files

```bash
# Buat folder
mkdir -p ~/botlinkmaster
cd ~/botlinkmaster

# Download files (atau upload manual)
# Pastikan semua file .py ada di folder ini
```

#### Step 3: Buat Virtual Environment

```bash
# Buat virtual environment
python3 -m venv venv

# Aktifkan virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip
```

#### Step 4: Install Python Dependencies

```bash
# Install packages
pip install python-telegram-bot python-dotenv paramiko pytz
```

Atau menggunakan requirements.txt:

```bash
pip install -r requirements.txt
```

#### Step 5: Konfigurasi Environment

```bash
# Copy template .env
cp .env.example .env

# Edit konfigurasi
nano .env
```

Isi file `.env`:

```env
# Token dari @BotFather (WAJIB)
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz

# Chat ID yang diizinkan (pisahkan dengan koma)
# User ID = angka positif
# Group ID = angka negatif (mulai dengan -100)
ALLOWED_CHAT_IDS=216481118

# Timezone (default: Asia/Jakarta)
TIMEZONE=Asia/Jakarta
```

#### Step 6: Test Bot Manual

```bash
# Pastikan virtual environment aktif
source venv/bin/activate

# Jalankan bot
python telegram_bot.py
```

Jika berhasil, akan muncul:

```
==================================================
BotLinkMaster v4.5 Started!
==================================================

Timezone: Asia/Jakarta
Time: 2025-01-12 22:30:45 WIB

Commands:
  /start /help /myid /time
  /list /add /device /delete
  /interfaces /cek /redaman
  /vendors /timezone /settz

[Press Ctrl+C to stop]
```

Tekan `Ctrl+C` untuk stop.

#### Step 7: Setup Systemd Service

```bash
# Buat file service
sudo nano /etc/systemd/system/botlinkmaster.service
```

Paste konten berikut (sesuaikan `User` dan `WorkingDirectory`):

```ini
[Unit]
Description=BotLinkMaster v4.5 - Network Device Monitoring Bot
After=network.target

[Service]
Type=simple
User=lab
WorkingDirectory=/home/lab/botlinkmaster
Environment=PATH=/home/lab/botlinkmaster/venv/bin
ExecStart=/home/lab/botlinkmaster/venv/bin/python /home/lab/botlinkmaster/telegram_bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Simpan: `Ctrl+X`, lalu `Y`, lalu `Enter`

#### Step 8: Aktifkan Service

```bash
# Reload systemd
sudo systemctl daemon-reload

# Start service
sudo systemctl start botlinkmaster

# Cek status
sudo systemctl status botlinkmaster

# Enable auto-start
sudo systemctl enable botlinkmaster
```

#### Step 9: Verifikasi

```bash
# Lihat log realtime
sudo journalctl -u botlinkmaster -f
```

Buka Telegram dan kirim `/start` ke bot.

---

## Mendapatkan Bot Token dari @BotFather

1. Buka Telegram, cari `@BotFather`
2. Kirim `/newbot`
3. Ikuti instruksi:
   - Masukkan nama bot (contoh: `My Network Monitor`)
   - Masukkan username bot (contoh: `mynetwork_bot`)
4. BotFather akan memberikan token seperti:

   ```
   123456789:ABCdefGHIjklMNOpqrsTUVwxyz
   ```

5. Copy token tersebut ke file `.env`

---

## Perintah Bot

### Info & Bantuan

| Command | Deskripsi |
|---------|-----------|
| `/start` | Tampilkan info bot |
| `/help` | Bantuan lengkap |
| `/help2` | Contoh penggunaan |
| `/myid` | Tampilkan Chat ID Anda |
| `/time` | Tampilkan waktu saat ini |

### Device Management

| Command | Deskripsi |
|---------|-----------|
| `/add` | Tambah perangkat baru |
| `/list` | Daftar semua perangkat |
| `/device [nama]` | Detail perangkat |
| `/delete [nama]` | Hapus perangkat |

### Monitoring

| Command | Deskripsi |
|---------|-----------|
| `/interfaces [device]` | List semua interface |
| `/cek [device] [interface]` | Cek status interface |
| `/redaman [device] [interface]` | Cek optical power |

### Konfigurasi

| Command | Deskripsi |
|---------|-----------|
| `/vendors` | Daftar vendor yang didukung |
| `/timezone` | Info timezone |
| `/timezone [continent]` | Timezone per benua |
| `/settz [timezone]` | Set timezone baru |

---

## Contoh Penggunaan

### Tambah Perangkat

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
vendor: cisco_ios

/add
nama: router-cabang-2
host: 10.0.0.1
username: admin
password: admin123
protocol: ssh
port: 2202
vendor: cisco_ios
```

### Cek Status Interface

```
/cek router-core GigabitEthernet0/0
```

### Cek Redaman/Optical Power

```
/redaman router-core Gi0/0
```

### Cek ONU pada ZTE OLT

```
/redaman olt-zte gpon-onu_1/2/1:10
```

Output:

```
OPTICAL POWER STATUS
==============================

Device: olt-zte
Vendor: ZTE OLT
Interface: gpon-onu_1/2/1:10
Link Status: [UP] up

OPTICAL READINGS:
  TX Power: 2.491 dBm
  RX Power: -32.285 dBm
  Attenuation: 34.776 dB
  Signal: [VERY WEAK] very_weak
```

### List Interface

```
/interfaces router-core
```

Output:

```
INTERFACE router-core
==============================

[UP] GigabitEthernet0/0
    Link to ISP
[UP] GigabitEthernet0/1
    Link to Switch Core
[DOWN] GigabitEthernet0/2
    Backup Link
[UP] Loopback0
    Management

Total: 4 interface
```

---

## Vendor yang Didukung

### Router & Switch

| Vendor | Kode | Command Optical |
|--------|------|-----------------|
| Cisco IOS/IOS-XE | `cisco_ios` | `show interface {int} transceiver` |
| Cisco NX-OS | `cisco_nxos` | `show interface {int} transceiver details` |
| Huawei VRP | `huawei` | `display transceiver interface {int}` |
| ZTE | `zte` | `show transceiver interface {int}` |
| Juniper JunOS | `juniper` | `show interfaces diagnostics optics {int}` |
| MikroTik | `mikrotik` | `/interface ethernet monitor {int} once` |
| Nokia SR-OS | `nokia` | `show port {int} optical` |
| HP/Aruba | `hp_aruba` | `show interface {int} transceiver` |
| H3C Comware | `h3c` | `display transceiver interface {int}` |
| Ruijie | `ruijie` | `show transceiver interface {int}` |
| DCN | `dcn` | `show transceiver interface {int}` |
| FS.COM | `fs` | `show transceiver interface {int}` |
| Allied Telesis | `allied` | `show system pluggable {int}` |
| Datacom | `datacom` | `show interface {int} transceiver` |
| Raisecom | `raisecom` | `show transceiver {int}` |
| BDCOM | `bdcom` | `show transceiver interface {int}` |

### OLT (Optical Line Terminal)

| Vendor | Kode | Command ONU Optical |
|--------|------|---------------------|
| ZTE OLT | `zte_olt` | `show pon power attenuation {interface}` |
| Huawei OLT | `huawei_olt` | `display ont optical-info {port} {onu_id}` |
| FiberHome OLT | `fiberhome_olt` | `show ont optical-info {interface}` |
| BDCOM OLT | `bdcom_olt` | `show epon optical-transceiver-diagnosis interface {int}` |
| VSOL OLT | `vsol_olt` | `show onu power {interface}` |

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

## Troubleshooting

### Error: "no matching host key type found"

Ini terjadi pada perangkat lama (Huawei, ZTE lama) yang menggunakan ssh-rsa.

**Solusi sudah built-in di v4.5.** Bot akan otomatis mencoba algoritma legacy.

Jika masih gagal, edit `/etc/ssh/ssh_config`:

```bash
sudo nano /etc/ssh/ssh_config
```

Tambahkan:

```
Host *
    HostKeyAlgorithms +ssh-rsa
    PubkeyAcceptedKeyTypes +ssh-rsa
```

### Error: Connection Timeout

1. Pastikan IP dan port benar
2. Cek firewall: `sudo ufw status`
3. Pastikan SSH/Telnet aktif di perangkat
4. Test manual: `ssh -p PORT user@host` atau `telnet host port`

### Error: Authentication Failed

1. Cek username dan password
2. Pastikan user memiliki akses SSH/Telnet
3. Beberapa perangkat perlu enable password

### Bot Tidak Merespon

1. Cek service status:

   ```bash
   sudo systemctl status botlinkmaster
   ```

2. Cek log:

   ```bash
   sudo journalctl -u botlinkmaster -f
   ```

3. Pastikan Chat ID ada di `ALLOWED_CHAT_IDS`

4. Restart bot:

   ```bash
   sudo systemctl restart botlinkmaster
   ```

### Data Optical Tidak Muncul

1. Pastikan vendor setting benar (`/device nama` untuk cek)
2. Interface harus berupa SFP/transceiver
3. Untuk ONU, gunakan format yang benar:
   - ZTE: `gpon-onu_1/2/1:10`
   - Huawei: gunakan format sesuai perangkat

### ModuleNotFoundError

```bash
# Aktifkan virtual environment
cd ~/botlinkmaster
source venv/bin/activate

# Install ulang dependencies
pip install -r requirements.txt
```

---

## Manajemen Service

### Start Bot

```bash
sudo systemctl start botlinkmaster
```

### Stop Bot

```bash
sudo systemctl stop botlinkmaster
```

### Restart Bot

```bash
sudo systemctl restart botlinkmaster
```

### Cek Status

```bash
sudo systemctl status botlinkmaster
```

### Lihat Log Realtime

```bash
sudo journalctl -u botlinkmaster -f
```

### Lihat Log File

```bash
tail -f ~/botlinkmaster/botlinkmaster.log
```

### Disable Auto-start

```bash
sudo systemctl disable botlinkmaster
```

---

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

### Step 3: Upload File Baru

Upload/replace file-file berikut:

- `telegram_bot.py`
```bash
cd ~/botlinkmaster
wget -N https://raw.githubusercontent.com/Iyankz/botlinkmaster/main/telegram_bot.py
```
- `botlinkmaster.py`
```bash
cd ~/botlinkmaster
wget -N https://raw.githubusercontent.com/Iyankz/botlinkmaster/main/botlinkmaster.py
```
- `database.py`
```bash
cd ~/botlinkmaster
wget -N https://raw.githubusercontent.com/Iyankz/botlinkmaster/main/database.py
```
- `vendor_commands.py`
```bash
cd ~/botlinkmaster
wget -N https://raw.githubusercontent.com/Iyankz/botlinkmaster/main/vendor_commands.py
```
- `timezone_config.py`
```bash
cd ~/botlinkmaster
wget -N https://raw.githubusercontent.com/Iyankz/botlinkmaster/main/timezone_config.py
```

### Step 4: Restart Service

```bash
sudo systemctl restart botlinkmaster
```

Database akan otomatis migrasi ke schema baru.

---


## Debug Mode

Untuk troubleshooting, aktifkan debug mode:

```bash
cd ~/botlinkmaster
source venv/bin/activate

# Edit file
nano telegram_bot.py
```

Ubah baris:

```python
logging.basicConfig(level=logging.INFO, ...)
```

Menjadi:

```python
logging.basicConfig(level=logging.DEBUG, ...)
```

Jalankan manual:

```bash
python telegram_bot.py
```

---

## Changelog

### v4.5.2 (Latest)

- ✅ Update Vendor vendor_command.py
- ✅ Update telegram_bot.py
- ✅ Update botlinkmaster.py

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

### Common Commands

```bash
# Start/Stop/Restart
sudo systemctl start botlinkmaster
sudo systemctl stop botlinkmaster
sudo systemctl restart botlinkmaster

# Logs
sudo journalctl -u botlinkmaster -f

# Edit config
nano ~/botlinkmaster/.env

# Manual run
cd ~/botlinkmaster
source venv/bin/activate
python telegram_bot.py
```

---

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
