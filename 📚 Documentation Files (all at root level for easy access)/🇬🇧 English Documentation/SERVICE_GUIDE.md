# 🚀 BotLinkMaster - Service Guide

## Running as System Service (systemd)

Bot dapat dijalankan sebagai system service yang:
- ✅ Otomatis start saat boot
- ✅ Restart otomatis jika crash
- ✅ Jalan di background
- ✅ Mudah di-manage dengan systemctl
- ✅ Log terintegrasi dengan system journal

---

## 📦 Installation Methods

### Method 1: Automatic (Recommended)

Saat menjalankan `install.sh`, pilih "Yes" saat ditanya setup service:

```bash
./install.sh

# Nanti akan muncul:
# Setup as system service? (y/N): y
```

Installer akan otomatis:
1. Configure service file
2. Install ke systemd
3. Enable auto-start
4. Siap digunakan dengan systemctl

### Method 2: Manual Setup

Jika skip saat install, atau ingin setup ulang:

```bash
# Run setup script
sudo ./setup-service.sh
```

---

## 🎮 Managing the Service

### Using botctl (Easy Way)

Script `botctl` menyediakan interface mudah untuk manage service:

```bash
# Make executable (first time only)
chmod +x botctl

# Start service
sudo ./botctl start

# Stop service
sudo ./botctl stop

# Restart service
sudo ./botctl restart

# Check status
sudo ./botctl status

# View logs (live)
sudo ./botctl logs

# Enable auto-start on boot
sudo ./botctl enable

# Disable auto-start
sudo ./botctl disable

# Uninstall service
sudo ./botctl uninstall
```

### Using systemctl (Standard Way)

```bash
# Start service
sudo systemctl start botlinkmaster

# Stop service
sudo systemctl stop botlinkmaster

# Restart service
sudo systemctl restart botlinkmaster

# Check status
sudo systemctl status botlinkmaster

# Enable auto-start on boot
sudo systemctl enable botlinkmaster

# Disable auto-start
sudo systemctl disable botlinkmaster

# View logs (live)
sudo journalctl -u botlinkmaster -f

# View all logs
sudo journalctl -u botlinkmaster

# View logs from today
sudo journalctl -u botlinkmaster --since today

# View last 100 lines
sudo journalctl -u botlinkmaster -n 100
```

---

## 📋 Common Tasks

### 1. First Time Setup

```bash
# 1. Install
./install.sh
# Choose 'y' for service setup

# 2. Configure token
sudo nano .env
# Add: TELEGRAM_BOT_TOKEN=your_token

# 3. Start service
sudo systemctl start botlinkmaster

# 4. Check if running
sudo systemctl status botlinkmaster
```

### 2. Check Service Status

```bash
# Quick status
sudo ./botctl status

# Detailed status
sudo systemctl status botlinkmaster

# Should show:
# ● botlinkmaster.service - BotLinkMaster v4.0
#    Loaded: loaded
#    Active: active (running)
```

### 3. View Logs

```bash
# Live logs (Ctrl+C to exit)
sudo ./botctl logs

# Or with systemctl
sudo journalctl -u botlinkmaster -f

# Last 50 lines
sudo journalctl -u botlinkmaster -n 50

# Logs from specific time
sudo journalctl -u botlinkmaster --since "2 hours ago"
sudo journalctl -u botlinkmaster --since "2024-01-07 10:00"
```

### 4. Update Configuration

```bash
# 1. Edit .env
sudo nano /path/to/botlinkmaster/.env

# 2. Restart service to apply changes
sudo systemctl restart botlinkmaster

# 3. Check if running
sudo systemctl status botlinkmaster
```

### 5. Update Bot Code

```bash
# 1. Stop service
sudo systemctl stop botlinkmaster

# 2. Update code (git pull or replace files)
cd /path/to/botlinkmaster
git pull

# 3. Update dependencies if needed
source venv/bin/activate
pip install -r requirements.txt

# 4. Start service
sudo systemctl start botlinkmaster

# 5. Check status
sudo systemctl status botlinkmaster
```

### 6. Troubleshooting

```bash
# Check if service is running
sudo systemctl is-active botlinkmaster

# Check if service is enabled
sudo systemctl is-enabled botlinkmaster

# View service configuration
systemctl cat botlinkmaster

# Reload systemd if service file changed
sudo systemctl daemon-reload

# View recent errors
sudo journalctl -u botlinkmaster -p err

# Full diagnostic
sudo systemctl status botlinkmaster
sudo journalctl -u botlinkmaster -n 100
```

---

## 🔧 Service Configuration

Service file location: `/etc/systemd/system/botlinkmaster.service`

### View Configuration

```bash
systemctl cat botlinkmaster
```

### Key Settings

```ini
[Service]
# Restart policy
Restart=always          # Always restart if stopped
RestartSec=10          # Wait 10s before restart
StartLimitBurst=5      # Max 5 restart attempts
StartLimitInterval=200 # Within 200 seconds

# Resource limits
MemoryMax=512M         # Max 512MB RAM
CPUQuota=100%          # Max 100% CPU (1 core)

# Security
NoNewPrivileges=true   # Cannot gain new privileges
ProtectSystem=strict   # Read-only /usr, /boot, /etc
ProtectHome=true       # No access to /home except own dir
```

### Modify Service

```bash
# 1. Edit service file
sudo nano /etc/systemd/system/botlinkmaster.service

# 2. Reload systemd
sudo systemctl daemon-reload

# 3. Restart service
sudo systemctl restart botlinkmaster
```

---

## 📊 Monitoring

### Check if Bot is Running

```bash
# Method 1: systemctl
sudo systemctl is-active botlinkmaster

# Method 2: process check
ps aux | grep telegram_bot.py

# Method 3: botctl
sudo ./botctl status
```

### Monitor Resource Usage

```bash
# CPU and Memory usage
systemctl status botlinkmaster

# Detailed resource usage
systemd-cgtop

# Filter for botlinkmaster
systemd-cgtop | grep botlinkmaster
```

### Check Uptime

```bash
systemctl status botlinkmaster | grep Active
```

---

## 🚨 Emergency Commands

### Bot Not Responding

```bash
# 1. Check status
sudo systemctl status botlinkmaster

# 2. View recent logs
sudo journalctl -u botlinkmaster -n 50

# 3. Restart service
sudo systemctl restart botlinkmaster

# 4. If still not working, check logs
sudo journalctl -u botlinkmaster -f
```

### Bot Keeps Restarting

```bash
# View crash logs
sudo journalctl -u botlinkmaster -p err

# Common causes:
# - Invalid TELEGRAM_BOT_TOKEN
# - Missing dependencies
# - Database locked
# - Permission issues
```

### High CPU/Memory Usage

```bash
# Check resource usage
systemctl status botlinkmaster

# Limit resources by editing service:
sudo nano /etc/systemd/system/botlinkmaster.service

# Add/modify:
MemoryMax=256M
CPUQuota=50%

# Apply changes
sudo systemctl daemon-reload
sudo systemctl restart botlinkmaster
```

---

## 🔄 Backup & Restore

### Backup Service Configuration

```bash
# Backup service file
sudo cp /etc/systemd/system/botlinkmaster.service \
     /path/to/botlinkmaster/botlinkmaster.service.backup

# Backup application data
cd /path/to/botlinkmaster
tar czf backup-$(date +%Y%m%d).tar.gz \
    .env config.py botlinkmaster.db botlinkmaster.log
```

### Restore Service

```bash
# Restore service file
sudo cp botlinkmaster.service.backup \
     /etc/systemd/system/botlinkmaster.service

# Reload systemd
sudo systemctl daemon-reload

# Restart service
sudo systemctl restart botlinkmaster
```

---

## ❌ Uninstall Service

### Using botctl

```bash
sudo ./botctl uninstall
```

### Manual Uninstall

```bash
# 1. Stop service
sudo systemctl stop botlinkmaster

# 2. Disable auto-start
sudo systemctl disable botlinkmaster

# 3. Remove service file
sudo rm /etc/systemd/system/botlinkmaster.service

# 4. Reload systemd
sudo systemctl daemon-reload

# 5. (Optional) Remove application
rm -rf /path/to/botlinkmaster
```

---

## 🎯 Best Practices

### 1. Always Check Logs After Start

```bash
sudo systemctl start botlinkmaster
sudo journalctl -u botlinkmaster -f
```

### 2. Enable Auto-Start for Production

```bash
sudo systemctl enable botlinkmaster
```

### 3. Regular Backups

```bash
# Create backup script
cat > backup.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
tar czf backup_$DATE.tar.gz .env config.py botlinkmaster.db
echo "Backup created: backup_$DATE.tar.gz"
EOF

chmod +x backup.sh

# Add to cron (daily at 2 AM)
echo "0 2 * * * /path/to/botlinkmaster/backup.sh" | crontab -
```

### 4. Monitor Service Health

```bash
# Create monitoring script
cat > check-health.sh << 'EOF'
#!/bin/bash
if ! systemctl is-active --quiet botlinkmaster; then
    echo "Bot is down! Restarting..."
    systemctl restart botlinkmaster
    # Send notification here
fi
EOF

chmod +x check-health.sh

# Add to cron (check every 5 minutes)
echo "*/5 * * * * /path/to/botlinkmaster/check-health.sh" | crontab -
```

---

## 📖 Reference

### Service States

- `active (running)` - Service is running ✅
- `inactive (dead)` - Service is stopped
- `failed` - Service crashed ❌
- `activating` - Service is starting

### Exit Codes

- `0` - Success
- `1` - General error
- `143` - Terminated by SIGTERM (normal stop)

### Useful Commands

```bash
# Service management
systemctl start|stop|restart|status botlinkmaster

# Logs
journalctl -u botlinkmaster [-f|-n 50|--since "1 hour ago"]

# Enable/Disable
systemctl enable|disable botlinkmaster

# Reload config
systemctl daemon-reload

# Check if running
systemctl is-active botlinkmaster
```

---

## 🆘 Getting Help

If service doesn't work:

1. Check status:
   ```bash
   sudo systemctl status botlinkmaster
   ```

2. View logs:
   ```bash
   sudo journalctl -u botlinkmaster -n 100
   ```

3. Run diagnostic:
   ```bash
   cd /path/to/botlinkmaster
   source venv/bin/activate
   python diagnose.py
   ```

4. Test manually:
   ```bash
   sudo systemctl stop botlinkmaster
   cd /path/to/botlinkmaster
   source venv/bin/activate
   python telegram_bot.py
   ```

---

**BotLinkMaster v4.0** - Professional systemd service integration! 🚀
