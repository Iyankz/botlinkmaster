# ⚡ Quick Start - Service Mode

## Setup Bot as System Service (5 Minutes)

Bot akan jalan otomatis di background dan start saat boot.

**BotLinkMaster v4.1.0** - Production-ready service deployment!

---

## 📦 Step 1: Install

```bash
# Clone repository
git clone https://github.com/Iyankz/botlinkmaster.git
cd botlinkmaster

# Run installer
chmod +x install.sh
./install.sh

# Saat ditanya "Setup as system service?", pilih: y
```

---

## 🔑 Step 2: Configure Token

```bash
# Edit .env
sudo nano .env

# Tambahkan token (TIDAK ADA SPASI):
TELEGRAM_BOT_TOKEN=123456:ABCdefGHIjklMNOpqrsTUVwxyz

# Save: Ctrl+X, Y, Enter
```

---

## 🚀 Step 3: Start Service

```bash
# Method 1: Using botctl (easy)
chmod +x botctl
sudo ./botctl start

# Method 2: Using systemctl
sudo systemctl start botlinkmaster

# Check if running
sudo ./botctl status
# or
sudo systemctl status botlinkmaster
```

**Output yang benar:**
```
● botlinkmaster.service - BotLinkMaster v4.0
   Loaded: loaded
   Active: active (running)
   ...
```

---

## 📱 Step 4: Test Bot

1. Buka Telegram
2. Search bot Anda
3. Kirim: `/start`
4. Bot harus reply dengan welcome message

---

## 📋 Daily Commands

### Start/Stop/Restart

```bash
# Start
sudo ./botctl start

# Stop
sudo ./botctl stop

# Restart
sudo ./botctl restart
```

### Check Status

```bash
sudo ./botctl status
```

### View Logs

```bash
# Live logs (Ctrl+C to exit)
sudo ./botctl logs

# Last 50 lines
sudo journalctl -u botlinkmaster -n 50
```

### Enable/Disable Auto-Start

```bash
# Enable (start on boot)
sudo ./botctl enable

# Disable
sudo ./botctl disable
```

---

## 🔧 Common Tasks

### Update Configuration

```bash
# 1. Edit .env
sudo nano .env

# 2. Restart service
sudo ./botctl restart
```

### Update Bot Code

```bash
# 1. Stop service
sudo ./botctl stop

# 2. Pull updates
git pull

# 3. Update dependencies
source venv/bin/activate
pip install -r requirements.txt

# 4. Start service
sudo ./botctl start
```

### View Logs by Time

```bash
# Last hour
sudo journalctl -u botlinkmaster --since "1 hour ago"

# Today
sudo journalctl -u botlinkmaster --since today

# Specific time
sudo journalctl -u botlinkmaster --since "2024-01-07 10:00"
```

---

## 🐛 Troubleshooting

### Service Won't Start

```bash
# 1. Check status
sudo systemctl status botlinkmaster

# 2. View logs
sudo journalctl -u botlinkmaster -n 100

# 3. Check .env
cat .env | grep TOKEN

# 4. Test manually
sudo systemctl stop botlinkmaster
source venv/bin/activate
python telegram_bot.py
```

### Bot Not Responding

```bash
# 1. Check if running
sudo ./botctl status

# 2. Restart service
sudo ./botctl restart

# 3. View logs
sudo ./botctl logs
```

### Check Resource Usage

```bash
sudo systemctl status botlinkmaster

# Shows CPU and Memory usage
```

---

## ⚙️ Advanced

### Modify Service Settings

```bash
# Edit service file
sudo nano /etc/systemd/system/botlinkmaster.service

# Reload systemd
sudo systemctl daemon-reload

# Restart service
sudo systemctl restart botlinkmaster
```

### Backup Service & Data

```bash
# Backup service file
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

- [ ] `sudo ./botctl status` shows "active (running)"
- [ ] Bot merespon `/start` di Telegram
- [ ] `sudo ./botctl logs` shows "Bot started successfully"
- [ ] Auto-start enabled: `systemctl is-enabled botlinkmaster`
- [ ] No errors in: `sudo journalctl -u botlinkmaster -p err`

---

## 📚 Documentation

- [SERVICE_GUIDE.md](SERVICE_GUIDE.md) - Complete service documentation
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Fix common issues
- [README.md](README.md) - Full documentation

---

## 🎯 Summary

**Setup once:**
```bash
./install.sh                # Install & setup service
sudo nano .env              # Add bot token
sudo ./botctl start         # Start service
```

**Daily usage:**
```bash
sudo ./botctl status        # Check if running
sudo ./botctl logs          # View logs
sudo ./botctl restart       # Restart if needed
```

**That's it!** Bot akan jalan otomatis di background dan start saat server reboot.

---

**BotLinkMaster v4.0** - Zero-hassle deployment! 🚀
