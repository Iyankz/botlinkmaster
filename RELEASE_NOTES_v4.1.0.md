# 🎉 BotLinkMaster v4.1.0 - Service Edition

**Release Date:** January 7, 2026  
**Status:** Stable Release  
**Type:** Minor Version Update (Feature Release)

---

## 📢 What's New

BotLinkMaster v4.1.0 adalah **major feature update** yang mengubah bot menjadi **production-ready system service** dengan auto-start, auto-restart, dan management yang sangat mudah!

### 🎯 Key Highlights

✨ **One-Command Installation** - Setup everything dengan 1 script  
🚀 **Background Service** - Jalan di background, tidak perlu terminal  
🔄 **Auto-Start on Boot** - Otomatis start saat server reboot  
♻️ **Auto-Restart on Crash** - Restart otomatis jika bot crash  
🎮 **Easy Management** - Manage dengan systemctl atau botctl  
📊 **Integrated Logging** - Log terintegrasi dengan systemd journal  
🔒 **Access Control** - Restrict bot access dengan Chat ID  
🔧 **Enhanced Diagnostics** - Tools untuk troubleshoot masalah  

---

## 🆕 New Features

### 1. Systemd Service Integration

**Complete system service support:**
- Bot runs as background systemd service
- No terminal needed
- Managed by system service manager
- Auto-start on boot (enabled by default)
- Auto-restart on crash (configurable)
- Resource limits (512MB RAM, 100% CPU)
- Security hardening applied

**Service File:**
```
/etc/systemd/system/botlinkmaster.service
```

### 2. One-Command Installer

**New `install-complete.sh` script:**
- Installs all system dependencies
- Configures timezone
- Creates Python virtual environment
- Installs Python packages
- Sets up configuration files
- Initializes database
- **Installs systemd service**
- **Enables auto-start**
- Sets proper permissions

**Usage:**
```bash
chmod +x install-complete.sh
sudo ./install-complete.sh
```

### 3. Service Management Tool

**New `botctl` script for easy management:**
```bash
sudo ./botctl start      # Start service
sudo ./botctl stop       # Stop service
sudo ./botctl restart    # Restart service
sudo ./botctl status     # Check status
sudo ./botctl logs       # View logs (live)
sudo ./botctl enable     # Enable auto-start
sudo ./botctl disable    # Disable auto-start
sudo ./botctl uninstall  # Remove service
```

### 4. Environment File Support

**Fixed .env loading:**
- Now properly loads environment variables with python-dotenv
- Configuration via .env file
- No more "Token not found" errors

**New .env variables:**
- `TELEGRAM_BOT_TOKEN` - Your bot token (required)
- `ALLOWED_CHAT_IDS` - Comma-separated Chat IDs (optional)
- `DATABASE_URL` - Database connection string
- `LOG_LEVEL` - Logging level

### 5. Access Control

**Chat ID-based restriction:**
- Restrict bot access to specific Telegram users
- Configure via `ALLOWED_CHAT_IDS` in .env
- Leave empty to allow all users

**New `/myid` command:**
- Users can get their Chat ID
- Use this ID in ALLOWED_CHAT_IDS
- Shows username and name too

**Authorization checks:**
- All commands now check authorization
- Unauthorized users get clear "Access Denied" message
- Shows user's Chat ID for easy configuration

### 6. Diagnostic Tools

**New `diagnose.py` script:**
- Comprehensive diagnostic tool
- Checks .env file existence
- Verifies bot token validity
- Tests Telegram API connection
- Verifies dependencies installed
- Checks database connectivity
- Shows bot information

**New `test_bot.py` script:**
- Minimal test bot
- Quick connectivity verification
- Echo messages back
- Useful for troubleshooting

### 7. Enhanced Logging

**Verbose startup logging:**
- Shows token length (not full token)
- Verifies token format
- Logs application creation
- Logs handler registration
- Shows access control status

**Systemd journal integration:**
- All logs go to systemd journal
- View with `journalctl -u botlinkmaster -f`
- Filter by date, time, level
- Persistent across reboots

### 8. Comprehensive Documentation

**New documentation files:**
- `README_SERVICE.md` - Service-focused README
- `SERVICE_GUIDE.md` - Complete service guide
- `QUICKSTART_SERVICE.md` - 5-minute quick start
- `DEPLOYMENT_SUMMARY.md` - Full deployment overview
- `INSTALL_CARD.txt` - Quick reference card
- Enhanced `TROUBLESHOOTING.md`
- `QUICK_FIX.md` - Fast problem resolution

---

## 🔧 Improvements

### Installer Improvements
- Enhanced `install.sh` with service setup option
- Created `install-simple.sh` for terminals without color
- Fixed color output rendering
- Better error messages
- Interactive timezone selection

### Bot Improvements
- More detailed error messages
- Better startup checks
- Token validation before starting
- Enhanced logging throughout

### Security Improvements
- Service runs as non-root user
- Limited file system access
- Protected system directories
- No new privileges allowed
- Private temporary directory

---

## 🐛 Bug Fixes

### Critical Fixes

1. **Fixed .env not loading** (#CRITICAL)
   - Added `from dotenv import load_dotenv`
   - Added `load_dotenv()` call in telegram_bot.py
   - Bot now properly reads .env file

2. **Fixed "Token not found" error** (#CRITICAL)
   - Related to .env loading fix
   - Bot now finds TELEGRAM_BOT_TOKEN correctly

### Minor Fixes

3. **Fixed color output in install.sh**
   - Added `-e` flag to echo commands
   - ANSI escape codes now render properly
   - No more `\033[...` in output

4. **Fixed file permissions**
   - All scripts properly set as executable
   - Correct permissions on .env (600)
   - Proper ownership for user files

---

## 📊 Technical Details

### System Requirements

**Minimum:**
- Python 3.8+
- 512MB RAM
- 1 CPU core
- 100MB disk space (+ database)

**Recommended:**
- Python 3.11+
- 1GB RAM
- 2 CPU cores
- 500MB disk space

**Supported OS:**
- Ubuntu 20.04+
- Debian 10+
- CentOS 7+
- RHEL 7+
- Fedora 30+
- Arch Linux

### Dependencies

**System packages:**
- python3, python3-pip, python3-venv
- git, curl, wget
- openssh-client, telnet
- tzdata

**Python packages:**
- paramiko==3.4.0
- python-telegram-bot==20.7
- SQLAlchemy==2.0.25
- click==8.1.7
- rich==13.7.0
- python-dotenv==1.0.0

### Service Configuration

**Location:**
```
/etc/systemd/system/botlinkmaster.service
```

**Key Settings:**
- Type: simple
- Restart: always (10s delay)
- StartLimitBurst: 5
- StartLimitInterval: 200s
- MemoryMax: 512M
- CPUQuota: 100%

**Security:**
- NoNewPrivileges=true
- PrivateTmp=true
- ProtectSystem=strict
- ProtectHome=true
- ReadWritePaths: install dir only

---

## 🚀 Migration Guide

### From v4.0.0 to v4.1.0

**Good news:** No breaking changes! Your data and configs are compatible.

**Steps:**

1. **Stop current bot:**
   ```bash
   # If running manually:
   Ctrl+C
   
   # If running with old script:
   pkill -f telegram_bot.py
   ```

2. **Backup data:**
   ```bash
   cp .env .env.backup
   cp config.py config.py.backup
   cp botlinkmaster.db botlinkmaster.db.backup
   ```

3. **Pull updates:**
   ```bash
   git pull origin main
   ```

4. **Run new installer:**
   ```bash
   chmod +x install-complete.sh
   sudo ./install-complete.sh
   ```

5. **Restore configuration:**
   ```bash
   cp .env.backup .env
   # Or edit: sudo nano .env
   ```

6. **Start service:**
   ```bash
   sudo systemctl start botlinkmaster
   ```

7. **Verify:**
   ```bash
   sudo systemctl status botlinkmaster
   sudo journalctl -u botlinkmaster -f
   ```

**That's it!** Your bot is now running as a service.

---

## 📚 Documentation

### Quick Start

```bash
# 1. Install
chmod +x install-complete.sh
sudo ./install-complete.sh

# 2. Add token
sudo nano .env
# Set: TELEGRAM_BOT_TOKEN=your_token

# 3. Start
sudo systemctl start botlinkmaster

# 4. Check
sudo systemctl status botlinkmaster
```

### Daily Usage

```bash
# Start/Stop/Restart
sudo systemctl start botlinkmaster
sudo systemctl stop botlinkmaster
sudo systemctl restart botlinkmaster

# Check status
sudo systemctl status botlinkmaster

# View logs
sudo journalctl -u botlinkmaster -f

# Or use botctl
sudo ./botctl start
sudo ./botctl logs
```

### Documentation Files

- **INSTALL_CARD.txt** - Quick reference
- **README_SERVICE.md** - Main documentation
- **QUICKSTART_SERVICE.md** - 5-minute guide
- **SERVICE_GUIDE.md** - Complete guide
- **DEPLOYMENT_SUMMARY.md** - Full overview
- **CHANGELOG.md** - Version history
- **MILESTONES.md** - Roadmap

---

## 🎯 What's Next

### v4.2.0 - Stability & Enhancement (Q1 2026)

Planned features:
- Multi-vendor support (Cisco, Huawei, Juniper, Mikrotik)
- Bulk device import/export
- Interface bandwidth monitoring
- Enhanced performance
- Unit tests and CI/CD

### v4.3.0 - Advanced Monitoring (Q2 2026)

Planned features:
- Alert notifications
- Multi-channel alerts (Email, Webhook, Slack)
- Historical data tracking
- Dashboard in Telegram
- Grafana integration

---

## 🐛 Known Issues

### None!

All known issues from v4.0.0 have been resolved in v4.1.0.

If you encounter any issues, please:
1. Run `python diagnose.py`
2. Check logs: `sudo journalctl -u botlinkmaster -f`
3. Read `TROUBLESHOOTING.md`
4. Open issue on GitHub

---

## 👥 Contributors

- [Iyankz](https://github.com/Iyankz) - Developer & Maintainer
- [Gemini](https://gemini.google.com/) - AI Assistant
- [Claude](https://claude.ai/) - AI Assistant

---

## 📄 License

MIT License - See [LICENSE](LICENSE)

---

## 🙏 Acknowledgments

Thank you to:
- All users who reported issues in v4.0.0
- The Python, Telegram Bot, and Systemd communities
- Everyone who provided feedback

---

## 📞 Support

- **GitHub Issues:** https://github.com/Iyankz/botlinkmaster/issues
- **Documentation:** See docs/ directory
- **Diagnostic Tool:** `python diagnose.py`
- **Troubleshooting:** Read `TROUBLESHOOTING.md`

---

## 🎉 Summary

v4.1.0 transforms BotLinkMaster from a manual script to a **production-ready system service**!

**Key Benefits:**
- ✅ Zero-hassle deployment
- ✅ Auto-start on boot
- ✅ Auto-restart on crash
- ✅ Easy management
- ✅ Enhanced security
- ✅ Better diagnostics
- ✅ Access control

**Upgrade now and enjoy hassle-free bot management!**

---

**BotLinkMaster v4.1.0** - Production-ready service deployment! 🚀

Released with ❤️ by the BotLinkMaster team
