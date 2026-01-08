# ⚡ Mulai Cepat - Mode Service

## Setup Bot sebagai System Service (5 Menit)

Bot akan berjalan otomatis di background dan start saat boot.

**BotLinkMaster v4.1.0** - Deployment production-ready!

---

## 📦 Langkah 1: Install

```bash
# Clone repository
git clone https://github.com/Iyankz/botlinkmaster.git
cd botlinkmaster

# Jalankan installer
chmod +x install-complete.sh
./install-complete.sh

# Saat ditanya "Setup as system service?", pilih: y
```

---

## 🔑 Langkah 2: Konfigurasi Token

```bash
# Edit .env
sudo nano .env

# Tambahkan token (TIDAK ADA SPASI):
TELEGRAM_BOT_TOKEN=123456:ABCdefGHIjklMNOpqrsTUVwxyz

# Simpan: Ctrl+X, Y, Enter
```

---

## 🚀 Langkah 3: Jalankan Service

```bash
# Metode 1: Menggunakan botctl (mudah)
chmod +x botctl
sudo ./botctl start

# Metode 2: Menggunakan systemctl
sudo systemctl start botlinkmaster

# Cek apakah berjalan
sudo ./botctl status
# atau
sudo systemctl status botlinkmaster
```

**Output yang benar:**
```
● botlinkmaster.service - BotLinkMaster v4.1.0
   Loaded: loaded
   Active: active (running)
   ...
```

---

## 📱 Langkah 4: Test Bot

1. Buka Telegram
2. Cari bot Anda
3. Kirim: `/start`
4. Bot harus reply dengan pesan selamat datang

---

## 📋 Perintah Harian

### Start/Stop/Restart

```bash
# Jalankan
sudo ./botctl start

# Hentikan
sudo ./botctl stop

# Restart
sudo ./botctl restart
```

### Cek Status

```bash
sudo ./botctl status
```

### Lihat Log

```bash
# Log realtime (Ctrl+C untuk keluar)
sudo ./botctl logs

# 50 baris terakhir
sudo journalctl -u botlinkmaster -n 50
```

### Enable/Disable Auto-Start

```bash
# Enable (start saat boot)
sudo ./botctl enable

# Disable
sudo ./botctl disable
```

---

## 🔧 Tugas Umum

### Update Konfigurasi

```bash
# 1. Edit .env
sudo nano .env

# 2. Restart service
sudo ./botctl restart
```

### Update Kode Bot

```bash
# 1. Hentikan service
sudo ./botctl stop

# 2. Pull update
git pull

# 3. Update dependencies
source venv/bin/activate
pip install -r requirements.txt

# 4. Jalankan service
sudo ./botctl start
```

### Lihat Log Berdasarkan Waktu

```bash
# 1 jam terakhir
sudo journalctl -u botlinkmaster --since "1 hour ago"

# Hari ini
sudo journalctl -u botlinkmaster --since today

# Waktu spesifik
sudo journalctl -u botlinkmaster --since "2024-01-07 10:00"
```

---

## 🐛 Troubleshooting

### Service Tidak Mau Start

```bash
# 1. Cek status
sudo systemctl status botlinkmaster

# 2. Lihat log
sudo journalctl -u botlinkmaster -n 100

# 3. Cek .env
cat .env | grep TOKEN

# 4. Test manual
sudo systemctl stop botlinkmaster
source venv/bin/activate
python telegram_bot.py
```

### Bot Tidak Merespon

```bash
# 1. Cek apakah berjalan
sudo ./botctl status

# 2. Restart service
sudo ./botctl restart

# 3. Lihat log
sudo ./botctl logs
```

### Cek Penggunaan Resource

```bash
sudo systemctl status botlinkmaster

# Menampilkan penggunaan CPU dan Memory
```

---

## ⚙️ Advanced

### Modifikasi Pengaturan Service

```bash
# Edit file service
sudo nano /etc/systemd/system/botlinkmaster.service

# Reload systemd
sudo systemctl daemon-reload

# Restart service
sudo systemctl restart botlinkmaster
```

### Backup Service & Data

```bash
# Backup file service
sudo cp /etc/systemd/system/botlinkmaster.service \
     botlinkmaster.service.backup

# Backup data
tar czf backup-$(date +%Y%m%d).tar.gz \
    .env config.py botlinkmaster.db botlinkmaster.log
```

### Uninstall Service

```bash
sudo ./botctl uninstall
```

---

## ✅ Checklist

Setup berhasil jika:

- [ ] `sudo ./botctl status` menampilkan "active (running)"
- [ ] Bot merespon `/start` di Telegram
- [ ] `sudo ./botctl logs` menampilkan "Bot started successfully"
- [ ] Auto-start enabled: `systemctl is-enabled botlinkmaster`
- [ ] Tidak ada error di: `sudo journalctl -u botlinkmaster -p err`

---

## 📚 Dokumentasi

- [SERVICE_GUIDE.md](SERVICE_GUIDE.md) - Dokumentasi service lengkap
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Perbaiki masalah umum
- [README_ID.md](README_ID.md) - Dokumentasi lengkap (Indonesia)

---

## 🎯 Ringkasan

**Setup sekali:**
```bash
./install-complete.sh           # Install & setup service
sudo nano .env                  # Tambah bot token
sudo ./botctl start             # Jalankan service
```

**Penggunaan harian:**
```bash
sudo ./botctl status            # Cek jika berjalan
sudo ./botctl logs              # Lihat log
sudo ./botctl restart           # Restart jika perlu
```

**Selesai!** Bot akan berjalan otomatis di background dan start saat server reboot.

---

**BotLinkMaster v4.1.0** - Instalasi tanpa ribet! 🚀
