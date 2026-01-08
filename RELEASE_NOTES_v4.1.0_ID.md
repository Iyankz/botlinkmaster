# 🎉 BotLinkMaster v4.1.0 - Service Edition

**Tanggal Rilis:** 7 Januari 2026  
**Status:** Rilis Stabil  
**Tipe:** Update Versi Minor (Fitur Baru)

---

## 📢 Yang Baru

BotLinkMaster v4.1.0 adalah **update fitur besar** yang mengubah bot menjadi **system service production-ready** dengan auto-start, auto-restart, dan manajemen yang sangat mudah!

### 🎯 Highlight Utama

✨ **Instalasi 1 Perintah** - Setup semuanya dengan 1 script  
🚀 **Background Service** - Jalan di background, tidak perlu terminal  
🔄 **Auto-Start saat Boot** - Otomatis start saat server reboot  
♻️ **Auto-Restart jika Crash** - Restart otomatis jika bot crash  
🎮 **Manajemen Mudah** - Kelola dengan systemctl atau botctl  
📊 **Logging Terintegrasi** - Log terintegrasi dengan systemd journal  
🔒 **Kontrol Akses** - Batasi akses bot dengan Chat ID  
🔧 **Diagnostic Lengkap** - Tools untuk troubleshoot masalah  

---

## 🆕 Fitur Baru

### 1. Integrasi Systemd Service

**Support system service lengkap:**
- Bot berjalan sebagai background systemd service
- Tidak perlu terminal
- Dikelola oleh system service manager
- Auto-start saat boot (enabled secara default)
- Auto-restart jika crash (bisa dikonfigurasi)
- Batas resource (512MB RAM, 100% CPU)
- Security hardening diterapkan

**File service:**
```
/etc/systemd/system/botlinkmaster.service
```

### 2. Installer 1 Perintah

**Script `install-complete.sh` yang baru:**
- Install semua system dependencies
- Konfigurasi timezone
- Buat Python virtual environment
- Install Python packages
- Setup file konfigurasi
- Inisialisasi database
- **Install systemd service**
- **Enable auto-start**
- Set permission yang benar

**Penggunaan:**
```bash
chmod +x install-complete.sh
sudo ./install-complete.sh
```

### 3. Tool Manajemen Service

**Script `botctl` baru untuk manajemen mudah:**
```bash
sudo ./botctl start      # Jalankan service
sudo ./botctl stop       # Hentikan service
sudo ./botctl restart    # Restart service
sudo ./botctl status     # Cek status
sudo ./botctl logs       # Lihat log (realtime)
sudo ./botctl enable     # Enable auto-start
sudo ./botctl disable    # Disable auto-start
sudo ./botctl uninstall  # Hapus service
```

### 4. Dukungan Environment File

**Perbaikan loading .env:**
- Sekarang loading environment variables dengan benar menggunakan python-dotenv
- Konfigurasi via file .env
- Tidak ada lagi error "Token not found"

**Variabel .env baru:**
- `TELEGRAM_BOT_TOKEN` - Token bot Anda (wajib)
- `ALLOWED_CHAT_IDS` - Chat ID yang diizinkan, dipisah koma (opsional)
- `DATABASE_URL` - String koneksi database
- `LOG_LEVEL` - Level logging

### 5. Kontrol Akses

**Pembatasan berbasis Chat ID:**
- Batasi akses bot ke pengguna Telegram tertentu
- Konfigurasi via `ALLOWED_CHAT_IDS` di .env
- Kosongkan untuk izinkan semua pengguna

**Perintah `/myid` baru:**
- Pengguna bisa dapatkan Chat ID mereka
- Gunakan ID ini di ALLOWED_CHAT_IDS
- Menampilkan username dan nama juga

**Pengecekan otorisasi:**
- Semua perintah sekarang cek otorisasi
- Pengguna tidak terotorisasi dapat pesan "Access Denied" yang jelas
- Menampilkan Chat ID pengguna untuk konfigurasi mudah

### 6. Tool Diagnostic

**Script `diagnose.py` baru:**
- Tool diagnostic komprehensif
- Cek keberadaan file .env
- Verifikasi validitas bot token
- Test koneksi Telegram API
- Verifikasi dependencies terinstall
- Cek koneksi database
- Tampilkan informasi bot

**Script `test_bot.py` baru:**
- Test bot minimal
- Verifikasi koneksi cepat
- Echo pesan kembali
- Berguna untuk troubleshooting

### 7. Logging yang Lebih Baik

**Logging startup verbose:**
- Tampilkan panjang token (bukan token lengkap)
- Verifikasi format token
- Log pembuatan aplikasi
- Log registrasi handler
- Tampilkan status kontrol akses

**Integrasi systemd journal:**
- Semua log masuk ke systemd journal
- Lihat dengan `journalctl -u botlinkmaster -f`
- Filter berdasarkan tanggal, waktu, level
- Persistent melewati reboot

### 8. Dokumentasi Lengkap

**File dokumentasi baru:**
- `README_ID.md` - README fokus service (Bahasa Indonesia)
- `SERVICE_GUIDE.md` - Panduan service lengkap
- `QUICKSTART_SERVICE.md` - Mulai cepat 5 menit
- `DEPLOYMENT_SUMMARY.md` - Ringkasan deployment lengkap
- `INSTALL_CARD.txt` - Kartu referensi cepat
- `TROUBLESHOOTING.md` yang diperbaiki
- `QUICK_FIX.md` - Resolusi masalah cepat

---

## 🔧 Perbaikan

### Perbaikan Installer
- `install.sh` diperbaiki dengan opsi setup service
- Dibuat `install-simple.sh` untuk terminal tanpa warna
- Perbaikan rendering output warna
- Pesan error yang lebih baik
- Pemilihan timezone interaktif

### Perbaikan Bot
- Pesan error lebih detail
- Pengecekan startup lebih baik
- Validasi token sebelum start
- Logging ditingkatkan di semua bagian

### Perbaikan Keamanan
- Service berjalan sebagai non-root user
- Akses file system terbatas
- Directory system dilindungi
- Tidak boleh privilege baru
- Directory temporary private

---

## 🐛 Bug yang Diperbaiki

### Perbaikan Kritis

1. **Perbaikan .env tidak loading** (#KRITIS)
   - Ditambahkan `from dotenv import load_dotenv`
   - Ditambahkan pemanggilan `load_dotenv()` di telegram_bot.py
   - Bot sekarang baca file .env dengan benar

2. **Perbaikan error "Token not found"** (#KRITIS)
   - Terkait dengan perbaikan loading .env
   - Bot sekarang temukan TELEGRAM_BOT_TOKEN dengan benar

### Perbaikan Minor

3. **Perbaikan output warna di install.sh**
   - Ditambahkan flag `-e` ke perintah echo
   - ANSI escape codes sekarang render dengan benar
   - Tidak ada lagi `\033[...` di output

4. **Perbaikan permission file**
   - Semua script di-set executable dengan benar
   - Permission yang benar pada .env (600)
   - Ownership yang benar untuk file user

---

## 📊 Detail Teknis

### Kebutuhan Sistem

**Minimum:**
- Python 3.8+
- 512MB RAM
- 1 CPU core
- 100MB ruang disk (+ database)

**Direkomendasikan:**
- Python 3.11+
- 1GB RAM
- 2 CPU cores
- 500MB ruang disk

**OS yang Didukung:**
- Ubuntu 20.04+
- Debian 10+
- CentOS 7+
- RHEL 7+
- Fedora 30+
- Arch Linux

### Dependencies

**Package system:**
- python3, python3-pip, python3-venv
- git, curl, wget
- openssh-client, telnet
- tzdata

**Package Python:**
- paramiko==3.4.0
- python-telegram-bot==20.7
- SQLAlchemy==2.0.25
- click==8.1.7
- rich==13.7.0
- python-dotenv==1.0.0

### Konfigurasi Service

**Lokasi:**
```
/etc/systemd/system/botlinkmaster.service
```

**Pengaturan Utama:**
- Type: simple
- Restart: always (delay 10s)
- StartLimitBurst: 5
- StartLimitInterval: 200s
- MemoryMax: 512M
- CPUQuota: 100%

**Keamanan:**
- NoNewPrivileges=true
- PrivateTmp=true
- ProtectSystem=strict
- ProtectHome=true
- ReadWritePaths: directory install saja

---

## 🚀 Panduan Migrasi

### Dari v4.0.0 ke v4.1.0

**Kabar baik:** Tidak ada breaking changes! Data dan config Anda kompatibel.

**Langkah-langkah:**

1. **Hentikan bot saat ini:**
   ```bash
   # Jika berjalan manual:
   Ctrl+C
   
   # Jika berjalan dengan script lama:
   pkill -f telegram_bot.py
   ```

2. **Backup data:**
   ```bash
   cp .env .env.backup
   cp config.py config.py.backup
   cp botlinkmaster.db botlinkmaster.db.backup
   ```

3. **Pull update:**
   ```bash
   git pull origin main
   ```

4. **Jalankan installer baru:**
   ```bash
   chmod +x install-complete.sh
   sudo ./install-complete.sh
   ```

5. **Restore konfigurasi:**
   ```bash
   cp .env.backup .env
   # Atau edit: sudo nano .env
   ```

6. **Jalankan service:**
   ```bash
   sudo systemctl start botlinkmaster
   ```

7. **Verifikasi:**
   ```bash
   sudo systemctl status botlinkmaster
   sudo journalctl -u botlinkmaster -f
   ```

**Selesai!** Bot Anda sekarang berjalan sebagai service.

---

## 📚 Dokumentasi

### Mulai Cepat

```bash
# 1. Install
chmod +x install-complete.sh
sudo ./install-complete.sh

# 2. Tambah token
sudo nano .env
# Set: TELEGRAM_BOT_TOKEN=token_anda

# 3. Jalankan
sudo systemctl start botlinkmaster

# 4. Cek
sudo systemctl status botlinkmaster
```

### Penggunaan Harian

```bash
# Start/Stop/Restart
sudo systemctl start botlinkmaster
sudo systemctl stop botlinkmaster
sudo systemctl restart botlinkmaster

# Cek status
sudo systemctl status botlinkmaster

# Lihat log
sudo journalctl -u botlinkmaster -f

# Atau gunakan botctl
sudo ./botctl start
sudo ./botctl logs
```

### File Dokumentasi

- **INSTALL_CARD.txt** - Referensi cepat
- **README_ID.md** - Dokumentasi utama (Bahasa Indonesia)
- **QUICKSTART_SERVICE.md** - Panduan 5 menit
- **SERVICE_GUIDE.md** - Panduan lengkap
- **DEPLOYMENT_SUMMARY.md** - Ringkasan lengkap
- **CHANGELOG.md** - Riwayat versi
- **MILESTONES.md** - Roadmap

---

## 🎯 Selanjutnya

### v4.2.0 - Stabilitas & Peningkatan (Q1 2026)

Fitur yang direncanakan:
- Dukungan multi-vendor (Cisco, Huawei, Juniper, Mikrotik)
- Import/export perangkat bulk
- Monitoring bandwidth interface
- Peningkatan performance
- Unit tests dan CI/CD

### v4.3.0 - Monitoring Advanced (Q2 2026)

Fitur yang direncanakan:
- Notifikasi alert
- Alert multi-channel (Email, Webhook, Slack)
- Tracking data historical
- Dashboard di Telegram
- Integrasi Grafana

---

## 🐛 Masalah yang Diketahui

### Tidak ada!

Semua masalah yang diketahui dari v4.0.0 sudah diselesaikan di v4.1.0.

Jika Anda menemukan masalah, mohon:
1. Jalankan `python diagnose.py`
2. Cek log: `sudo journalctl -u botlinkmaster -f`
3. Baca `TROUBLESHOOTING.md`
4. Buka issue di GitHub

---

## 👥 Kontributor

- [Iyankz](https://github.com/Iyankz) - Developer & Maintainer
- [Gemini](https://gemini.google.com/) - AI Assistant
- [Claude](https://claude.ai/) - AI Assistant

---

## 📄 Lisensi

MIT License - Lihat [LICENSE](LICENSE)

---

## 🙏 Terima Kasih

Terima kasih kepada:
- Semua pengguna yang melaporkan masalah di v4.0.0
- Komunitas Python, Telegram Bot, dan Systemd
- Semua yang memberikan feedback

---

## 📞 Dukungan

- **GitHub Issues:** https://github.com/Iyankz/botlinkmaster/issues
- **Dokumentasi:** Lihat direktori docs/
- **Tool Diagnostic:** `python diagnose.py`
- **Troubleshooting:** Baca `TROUBLESHOOTING.md`

---

## 🎉 Ringkasan

v4.1.0 mengubah BotLinkMaster dari script manual menjadi **system service production-ready**!

**Manfaat Utama:**
- ✅ Deployment tanpa ribet
- ✅ Auto-start saat boot
- ✅ Auto-restart jika crash
- ✅ Manajemen mudah
- ✅ Keamanan lebih baik
- ✅ Diagnostic lebih baik
- ✅ Kontrol akses

**Upgrade sekarang dan nikmati manajemen bot tanpa ribet!**

---

**BotLinkMaster v4.1.0** - Deployment production-ready! 🚀

Dirilis dengan ❤️ oleh tim BotLinkMaster
