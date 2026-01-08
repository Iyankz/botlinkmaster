# 🎮 botctl - Service Manager

`botctl` adalah script **command-line tool** untuk mengelola BotLinkMaster service dengan mudah.

## 📋 Apa itu botctl?

`botctl` adalah **wrapper script** yang menyederhanakan perintah systemctl untuk BotLinkMaster. Daripada mengetik perintah systemctl yang panjang, Anda cukup gunakan `botctl` dengan perintah sederhana.

**Fungsi Utama:**
- Simplifikasi perintah systemctl
- Interface yang lebih user-friendly
- Help text yang jelas
- Error handling yang baik
- Colored output untuk readability

---

## 🎯 Kenapa Perlu botctl?

### ❌ Tanpa botctl (systemctl biasa):

```bash
# Perintah panjang dan perlu diingat
sudo systemctl start botlinkmaster
sudo systemctl stop botlinkmaster
sudo systemctl restart botlinkmaster
sudo systemctl status botlinkmaster
sudo journalctl -u botlinkmaster -f
sudo systemctl enable botlinkmaster
sudo systemctl disable botlinkmaster

# Install/uninstall service manual
sudo ./setup-service.sh
sudo systemctl stop botlinkmaster
sudo systemctl disable botlinkmaster
sudo rm /etc/systemd/system/botlinkmaster.service
sudo systemctl daemon-reload
```

### ✅ Dengan botctl (mudah!):

```bash
# Perintah pendek dan mudah diingat
sudo ./botctl start
sudo ./botctl stop
sudo ./botctl restart
sudo ./botctl status
sudo ./botctl logs
sudo ./botctl enable
sudo ./botctl disable

# Install/uninstall dengan 1 perintah
sudo ./botctl install
sudo ./botctl uninstall
```

**Lebih pendek, lebih mudah, lebih cepat!** ⚡

---

## 📖 Perintah yang Tersedia

### 1. start - Jalankan Service

```bash
sudo ./botctl start
```

**Fungsi:**
- Start BotLinkMaster service
- Tunggu 2 detik untuk stabilisasi
- Tampilkan status service

**Output:**
```
Starting BotLinkMaster...
● botlinkmaster.service - BotLinkMaster v4.1.0
   Loaded: loaded
   Active: active (running)
   ...
```

### 2. stop - Hentikan Service

```bash
sudo ./botctl stop
```

**Fungsi:**
- Stop BotLinkMaster service
- Tunggu hingga benar-benar berhenti
- Tampilkan konfirmasi

**Output:**
```
Stopping BotLinkMaster...
✓ Service stopped
```

### 3. restart - Restart Service

```bash
sudo ./botctl restart
```

**Fungsi:**
- Restart BotLinkMaster service
- Tunggu 2 detik untuk stabilisasi
- Tampilkan status service

**Kapan digunakan:**
- Setelah update konfigurasi (.env)
- Setelah update code
- Bot tidak merespon
- Troubleshooting

**Output:**
```
Restarting BotLinkMaster...
● botlinkmaster.service - BotLinkMaster v4.1.0
   Loaded: loaded
   Active: active (running)
   ...
```

### 4. status - Cek Status Service

```bash
sudo ./botctl status
```

**Fungsi:**
- Tampilkan status lengkap service
- Tampilkan resource usage
- Tampilkan log terbaru
- Tampilkan quick commands

**Output:**
```
● botlinkmaster.service - BotLinkMaster v4.1.0
   Loaded: loaded
   Active: active (running) since Wed 2026-01-07 10:00:00 WIB
   Main PID: 12345
   Memory: 75.2M
   CPU: 156ms
   CGroup: /system.slice/botlinkmaster.service
           └─12345 /path/to/venv/bin/python /path/to/telegram_bot.py

Quick commands:
  View logs: sudo ./botctl logs
  Restart:   sudo ./botctl restart
```

### 5. logs - Lihat Log (Realtime)

```bash
sudo ./botctl logs
```

**Fungsi:**
- Tampilkan log realtime (live)
- Follow mode (update otomatis)
- Keluar dengan Ctrl+C

**Equivalent:**
```bash
sudo journalctl -u botlinkmaster -f
```

**Output:**
```
Viewing live logs (Ctrl+C to exit)...

Jan 07 10:00:01 hostname botlinkmaster[12345]: Bot started successfully
Jan 07 10:00:05 hostname botlinkmaster[12345]: User 123456789 started the bot
Jan 07 10:00:10 hostname botlinkmaster[12345]: Checking interface eth0
...
```

### 6. logs-all - Lihat Semua Log

```bash
sudo ./botctl logs-all
```

**Fungsi:**
- Tampilkan semua log (dari awal)
- Non-follow mode
- Bagus untuk review keseluruhan

**Equivalent:**
```bash
sudo journalctl -u botlinkmaster --no-pager
```

### 7. enable - Enable Auto-Start

```bash
sudo ./botctl enable
```

**Fungsi:**
- Enable service auto-start saat boot
- Service akan otomatis start saat server reboot

**Output:**
```
Enabling auto-start on boot...
✓ Service will start automatically on boot
```

**Verifikasi:**
```bash
systemctl is-enabled botlinkmaster
# Output: enabled
```

### 8. disable - Disable Auto-Start

```bash
sudo ./botctl disable
```

**Fungsi:**
- Disable service auto-start saat boot
- Service TIDAK akan otomatis start saat server reboot
- Service tetap bisa dijalankan manual

**Output:**
```
Disabling auto-start...
⚠ Service will NOT start automatically on boot
```

**Verifikasi:**
```bash
systemctl is-enabled botlinkmaster
# Output: disabled
```

### 9. install - Install Service

```bash
sudo ./botctl install
```

**Fungsi:**
- Jalankan setup-service.sh
- Install systemd service
- Configure service file
- Enable auto-start

**Kapan digunakan:**
- Jika skip service setup saat install
- Reinstall service jika terhapus
- Setup service di server lain

**Output:**
```
Installing BotLinkMaster service...
✓ Service file installed
✓ Systemd reloaded
✓ Service enabled
```

### 10. uninstall - Uninstall Service

```bash
sudo ./botctl uninstall
```

**Fungsi:**
- Stop service jika running
- Disable auto-start
- Hapus service file
- Reload systemd

**PENTING:** Ini HANYA uninstall service, bukan aplikasi!

**Output:**
```
Uninstalling BotLinkMaster service...
✓ Service stopped
✓ Service disabled
✓ Service file removed

Note: Application files are still in place
To remove completely, delete the installation directory
```

---

## 🚀 Cara Menggunakan

### Setup Pertama Kali

```bash
# 1. Make executable (sekali saja)
chmod +x botctl

# 2. Gunakan botctl
sudo ./botctl start
sudo ./botctl status
sudo ./botctl logs
```

### Penggunaan Harian

```bash
# Cek apakah berjalan
sudo ./botctl status

# Lihat log
sudo ./botctl logs

# Restart jika perlu
sudo ./botctl restart
```

### Troubleshooting

```bash
# Bot tidak merespon
sudo ./botctl restart
sudo ./botctl logs

# Cek status lengkap
sudo ./botctl status

# Lihat semua log
sudo ./botctl logs-all
```

---

## 🔧 Teknis

### Lokasi File

```bash
/path/to/botlinkmaster/botctl
```

### Permissions

```bash
# File harus executable
chmod +x botctl

# Atau saat clone/download
chmod 755 botctl
```

### Requires

- Bash shell
- systemctl (systemd)
- journalctl
- Root/sudo privileges

### Service Name

Script ini hardcoded untuk service name: `botlinkmaster`

Jika Anda ubah service name, edit script:
```bash
SERVICE_NAME="botlinkmaster"  # Ubah ini
```

---

## 💡 Tips & Tricks

### 1. Alias untuk Kemudahan

Tambahkan ke `~/.bashrc` atau `~/.zshrc`:

```bash
alias bot='sudo /path/to/botlinkmaster/botctl'
```

Lalu gunakan:
```bash
bot start
bot stop
bot status
bot logs
```

### 2. Monitoring Cepat

```bash
# Monitor realtime
watch -n 2 'sudo ./botctl status'
```

### 3. Log dengan Filter

```bash
# Hanya error
sudo journalctl -u botlinkmaster -p err

# Hari ini
sudo journalctl -u botlinkmaster --since today

# 1 jam terakhir
sudo journalctl -u botlinkmaster --since "1 hour ago"
```

### 4. Remote Management

Gunakan SSH:
```bash
ssh user@server 'sudo /path/to/botctl status'
ssh user@server 'sudo /path/to/botctl restart'
```

### 5. Automation dengan Cron

```bash
# Auto-restart setiap hari jam 3 pagi
0 3 * * * /path/to/botctl restart > /dev/null 2>&1

# Health check setiap 5 menit
*/5 * * * * systemctl is-active --quiet botlinkmaster || /path/to/botctl start
```

---

## 🆚 botctl vs systemctl

| Aspek | botctl | systemctl |
|-------|--------|-----------|
| **Syntax** | Pendek | Panjang |
| **User-friendly** | ✅ Ya | ❌ Tidak |
| **Help text** | ✅ Built-in | ❌ Manual RTFM |
| **Colored output** | ✅ Ya | ❌ Tidak |
| **Service name** | ✅ Otomatis | ❌ Harus tulis |
| **Quick commands** | ✅ Ya | ❌ Tidak |

**Kesimpulan:** `botctl` lebih mudah untuk daily use, `systemctl` lebih powerful untuk advanced tasks.

---

## 📝 Examples

### Scenario 1: Update Konfigurasi

```bash
# 1. Edit .env
sudo nano .env

# 2. Restart service
sudo ./botctl restart

# 3. Verifikasi
sudo ./botctl logs
```

### Scenario 2: Update Code

```bash
# 1. Stop service
sudo ./botctl stop

# 2. Pull update
git pull

# 3. Update dependencies
source venv/bin/activate
pip install -r requirements.txt

# 4. Start service
sudo ./botctl start

# 5. Monitor
sudo ./botctl logs
```

### Scenario 3: Troubleshooting

```bash
# 1. Cek status
sudo ./botctl status

# 2. Lihat log
sudo ./botctl logs

# 3. Jika error, restart
sudo ./botctl restart

# 4. Monitor hasil
sudo ./botctl logs
```

### Scenario 4: Maintenance

```bash
# 1. Stop service
sudo ./botctl stop

# 2. Backup database
cp botlinkmaster.db botlinkmaster.db.backup

# 3. Lakukan maintenance
# ...

# 4. Start service
sudo ./botctl start
```

---

## 🐛 Troubleshooting botctl

### Error: Permission Denied

```bash
# Problem
./botctl start
# Output: Permission denied

# Solution 1: Make executable
chmod +x botctl

# Solution 2: Use sudo
sudo ./botctl start
```

### Error: Command Not Found

```bash
# Problem
botctl start
# Output: command not found

# Solution: Use ./botctl (current directory)
sudo ./botctl start

# Atau gunakan full path
sudo /path/to/botlinkmaster/botctl start
```

### Error: This script must be run as root

```bash
# Problem
./botctl start
# Output: This command requires root privileges

# Solution: Use sudo
sudo ./botctl start
```

### Error: Service Not Found

```bash
# Problem
sudo ./botctl status
# Output: Failed to get unit file state

# Solution: Install service first
sudo ./botctl install
# Or
sudo ./setup-service.sh
```

---

## 🔍 Behind the Scenes

### What botctl Actually Does

**`sudo ./botctl start`** runs:
```bash
systemctl start botlinkmaster
sleep 2
systemctl status botlinkmaster --no-pager
```

**`sudo ./botctl logs`** runs:
```bash
journalctl -u botlinkmaster -f
```

**`sudo ./botctl uninstall`** runs:
```bash
systemctl stop botlinkmaster
systemctl disable botlinkmaster
rm /etc/systemd/system/botlinkmaster.service
systemctl daemon-reload
```

Jadi `botctl` adalah **wrapper** yang membuat hidup Anda lebih mudah! 😊

---

## 📚 Related Documentation

- **SERVICE_GUIDE.md** - Complete service documentation
- **README_SERVICE.md** - Service edition README
- **QUICKSTART_SERVICE.md** - Quick start guide
- **systemctl manual** - `man systemctl`
- **journalctl manual** - `man journalctl`

---

## 🎯 Summary

**botctl adalah:**
- ✅ Command-line tool untuk manage service
- ✅ Wrapper untuk systemctl
- ✅ User-friendly interface
- ✅ Simplifikasi perintah
- ✅ Save waktu dan effort
- ✅ Cocok untuk daily use

**Perintah paling sering dipakai:**
```bash
sudo ./botctl status   # Cek status
sudo ./botctl logs     # Lihat log
sudo ./botctl restart  # Restart jika perlu
```

**Remember:**
- Selalu gunakan `sudo`
- Gunakan `./botctl` (jangan lupa `./`)
- Run dari directory installation
- Atau buat alias untuk kemudahan

---

**BotLinkMaster v4.1.0** - botctl makes service management easy! 🎮
