# 🤖 BotLinkMaster v4.1.0 - Service Edition

Bot monitoring perangkat jaringan via SSH/Telnet dengan **auto-start service**

## ⚡ Quick Start (3 Commands)

```bash
# 1. Install (otomatis setup service)
chmod +x install-complete.sh
sudo ./install-complete.sh

# 2. Add bot token
sudo nano .env
# Set: TELEGRAM_BOT_TOKEN=your_token

# 3. Start service
sudo systemctl start botlinkmaster
```

**That's it!** ✅ Bot running di background, auto-start on boot.

---

## 📋 Requirements

### System Requirements

**Minimum:**
- **OS:** Ubuntu 20.04+, Debian 10+, CentOS 7+, RHEL 7+, Fedora 30+, Arch Linux
- **CPU:** 1 Core
- **RAM:** 512 MB
- **Storage:** 100 MB (application) + 50-200 MB (database, depends on device count)
- **Network:** Internet connection for Telegram API

**Recommended:**
- **OS:** Ubuntu 22.04 LTS or Debian 11+
- **CPU:** 2 Cores
- **RAM:** 1 GB
- **Storage:** 500 MB
- **Network:** Stable internet connection

### Software Requirements

**System Packages (auto-installed by installer):**
- Python 3.8 or newer (recommended Python 3.11+)
- python3-pip
- python3-venv
- git
- curl, wget
- openssh-client
- telnet
- tzdata

**Python Packages (auto-installed by installer):**
```
paramiko==3.4.0          # For SSH connections
python-telegram-bot==20.7 # For Telegram Bot
SQLAlchemy==2.0.25       # For database ORM
click==8.1.7             # For CLI
rich==13.7.0             # For CLI formatting
python-dotenv==1.0.0     # For .env file support
```

### Network Requirements

**Required Ports:**
- **Outbound:**
  - Port 443 (HTTPS) - For Telegram API
  - Port 22 (SSH) - For connecting to network devices
  - Port 23 (Telnet) - For connecting to network devices (optional)

**No inbound ports required** - Bot uses polling from Telegram API

### Telegram Requirements

- **Bot Token** from [@BotFather](https://t.me/botfather)
- Telegram account to use the bot

### Target Device Requirements

Network devices to be monitored must:
- Support SSH and/or Telnet
- Have user account with access to show commands
- Be reachable from bot server
- Provide standard command output (Cisco-like preferred)

**Supported Devices:**
- Cisco IOS/IOS-XE
- Cisco NX-OS
- Juniper JunOS
- HP/Aruba
- MikroTik
- Generic SSH/Telnet devices

---

## 📋 Daily Usage

```bash
# Check status
sudo systemctl status botlinkmaster

# View logs (live)
sudo journalctl -u botlinkmaster -f

# Restart if needed
sudo systemctl restart botlinkmaster
```

---

## 🎮 Easy Management with `botctl`

```bash
sudo ./botctl start      # Start service
sudo ./botctl stop       # Stop service  
sudo ./botctl restart    # Restart service
sudo ./botctl status     # Check status
sudo ./botctl logs       # View logs
```

---

## ✨ Features

- ✅ **SSH & Telnet** support
- ✅ **Auto-start** on boot (systemd)
- ✅ **Background** service
- ✅ **Auto-restart** on crash
- ✅ **Integrated logging** (journalctl)
- ✅ **Resource limits** (CPU/Memory)
- ✅ **Database** (SQLAlchemy ORM)
- ✅ **Telegram Bot** interface
- ✅ **CLI tools** included
- ✅ **Chat ID restriction** for security

---

## 🤖 Bot Commands

| Command | Description |
|---------|-------------|
| `/start` | Welcome message |
| `/help` | Full help |
| `/myid` | Get your Chat ID |
| `/list` | List all devices |
| `/add` | Add new device |
| `/device <name>` | Device details |
| `/cek <device> <interface>` | Check interface status |
| `/delete <name>` | Delete device |

---

## 📝 Add Device

```
/add
nama: router-1
host: 192.168.1.1
username: admin
password: pass123
protocol: ssh
port: 22
description: Main router
location: Data center
```

---

## 🔒 Access Control (Optional)

Restrict bot to specific users:

```bash
# 1. Get your Chat ID
# Send /myid to bot

# 2. Edit .env
sudo nano .env

# Add:
ALLOWED_CHAT_IDS=123456789,987654321

# 3. Restart
sudo systemctl restart botlinkmaster
```

---

## 🛠️ Service Management

### System Commands

```bash
# Start service
sudo systemctl start botlinkmaster

# Stop service  
sudo systemctl stop botlinkmaster

# Restart service
sudo systemctl restart botlinkmaster

# Check status
sudo systemctl status botlinkmaster

# Enable auto-start (already enabled by installer)
sudo systemctl enable botlinkmaster

# Disable auto-start
sudo systemctl disable botlinkmaster

# View logs (live)
sudo journalctl -u botlinkmaster -f

# View logs (last 100 lines)
sudo journalctl -u botlinkmaster -n 100

# View logs (today)
sudo journalctl -u botlinkmaster --since today
```

### botctl Commands

```bash
# Make executable (first time)
chmod +x botctl

# Start
sudo ./botctl start

# Stop
sudo ./botctl stop

# Restart
sudo ./botctl restart

# Status
sudo ./botctl status

# Logs (live)
sudo ./botctl logs

# Enable auto-start
sudo ./botctl enable

# Disable auto-start
sudo ./botctl disable

# Uninstall service
sudo ./botctl uninstall
```

---

## 📊 Check if Running

```bash
# Method 1: Status
sudo systemctl status botlinkmaster
# Look for: Active: active (running)

# Method 2: Process
ps aux | grep telegram_bot.py

# Method 3: botctl
sudo ./botctl status
```

---

## 🔧 Update Configuration

```bash
# 1. Edit .env
sudo nano .env

# 2. Restart service
sudo systemctl restart botlinkmaster

# 3. Verify
sudo systemctl status botlinkmaster
```

---

## 📦 Update Bot Code

```bash
# 1. Stop service
sudo systemctl stop botlinkmaster

# 2. Pull updates
git pull

# 3. Update dependencies (if needed)
source venv/bin/activate
pip install -r requirements.txt

# 4. Start service
sudo systemctl start botlinkmaster
```

---

## 🐛 Troubleshooting

### Service won't start

```bash
# Check status
sudo systemctl status botlinkmaster

# View logs
sudo journalctl -u botlinkmaster -n 100

# Check .env
cat .env | grep TOKEN

# Run diagnostic
python diagnose.py
```

### Bot not responding

```bash
# Restart service
sudo systemctl restart botlinkmaster

# Check logs
sudo journalctl -u botlinkmaster -f

# Test manually
sudo systemctl stop botlinkmaster
source venv/bin/activate
python telegram_bot.py
```

### View error logs only

```bash
sudo journalctl -u botlinkmaster -p err
```

---

## 📚 Documentation

- **[SERVICE_GUIDE.md](SERVICE_GUIDE.md)** - Complete service documentation
- **[QUICKSTART_SERVICE.md](QUICKSTART_SERVICE.md)** - Quick start guide
- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Fix common issues
- **[EXAMPLES.md](EXAMPLES.md)** - Usage examples

---

## 🔄 System Service Info

**Service file:** `/etc/systemd/system/botlinkmaster.service`

**Settings:**
- Auto-restart on failure
- Max 512MB memory
- Max 100% CPU (1 core)
- Logs to systemd journal
- Security hardening enabled

**View service config:**
```bash
systemctl cat botlinkmaster
```

---

## 📁 File Structure

```
botlinkmaster/
│
├── README.md                    # ⭐ Main docs (must be at root!)
├── README_SERVICE.md            # ⭐ This file (at root!)
│
├── 🐍 Core Python Modules
│   ├── telegram_bot.py          # Main bot
│   ├── botlinkmaster.py         # SSH/Telnet handler
│   ├── database.py              # Database ORM
│   └── cli.py                   # CLI tool
│
├── 🔧 Service & Installation (v4.1.0)
│   ├── install-complete.sh      # Complete installer (USE THIS!)
│   ├── botctl                   # Service manager tool
│   ├── setup-service.sh         # Manual service setup
│   ├── install.sh               # Legacy installer
│   └── botlinkmaster.service    # Systemd service file
│
├── 🔍 Diagnostic Tools (v4.1.0)
│   ├── diagnose.py              # Complete diagnostic
│   └── test_bot.py              # Connection tester
│
├── 🐳 Docker
│   ├── Dockerfile               # Docker image
│   ├── docker-compose.yml       # Docker Compose
│   └── docker-run.sh            # Docker script
│
├── ⚙️ Configuration
│   ├── .env                     # Configuration (ADD TOKEN HERE!)
│   ├── .env.example             # Config template
│   ├── config.py                # Python config
│   └── requirements.txt         # Python dependencies
│
├── 📚 Documentation (All at root level for GitHub)
│   │
│   ├── 🇬🇧 English
│   │   ├── SERVICE_GUIDE.md
│   │   ├── BOTCTL_GUIDE.md
│   │   ├── REQUIREMENTS.md
│   │   ├── TROUBLESHOOTING.md
│   │   ├── QUICKSTART_SERVICE.md
│   │   ├── DEPLOYMENT_SUMMARY.md
│   │   ├── CHANGELOG.md
│   │   └── More...
│   │
│   ├── 🇮🇩 Indonesian
│   │   ├── README_ID.md
│   │   ├── QUICKSTART_ID.md
│   │   └── RELEASE_NOTES_v4.1.0_ID.md
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
└── 🚀 Runtime Files (auto-created)
    ├── venv/                    # Virtual environment
    ├── botlinkmaster.db         # SQLite database
    ├── botlinkmaster.log        # Log file
    └── __pycache__/             # Python cache

NOTE: All documentation files are at ROOT DIRECTORY (not in subfolders)
      so they're easily accessible and README.md displays on GitHub.
```

**Key Files at Root:**
- 🔑 **README.md** - Main docs (displays on GitHub)
- 🔑 **install-complete.sh** - Main installer (use this!)
- 🎮 **botctl** - Easy service management tool
- 📝 **diagnose.py** - Diagnostic tool for issues
- ⚙️ **.env** - Configuration file (add token here!)

---

## ✅ Installation Checklist

After `install-complete.sh`:

- [ ] Service installed: `systemctl status botlinkmaster`
- [ ] Service enabled: `systemctl is-enabled botlinkmaster`
- [ ] .env exists: `ls -la .env`
- [ ] Token added: `cat .env | grep TOKEN`
- [ ] Service started: `sudo systemctl start botlinkmaster`
- [ ] Bot responds in Telegram: `/start`
- [ ] Logs working: `sudo journalctl -u botlinkmaster -f`

---

## 🆘 Quick Help

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

## 🎯 Quick Reference

| Task | Command |
|------|---------|
| **Start** | `sudo systemctl start botlinkmaster` |
| **Stop** | `sudo systemctl stop botlinkmaster` |
| **Restart** | `sudo systemctl restart botlinkmaster` |
| **Status** | `sudo systemctl status botlinkmaster` |
| **Logs** | `sudo journalctl -u botlinkmaster -f` |
| **Edit config** | `sudo nano .env` |
| **Diagnostic** | `python diagnose.py` |

---

## 👥 Contributors

- [Iyankz](https://github.com/Iyankz) - Developer
- [Gemini](https://gemini.google.com/) - AI Assistant
- [Claude](https://claude.ai/) - AI Assistant

---

## 📄 License

MIT License - See [LICENSE](LICENSE)

---

## 🚀 Summary

**Install once:**
```bash
sudo ./install-complete.sh     # Setup everything
sudo nano .env                 # Add token
sudo systemctl start botlinkmaster
```

**Daily usage:**
```bash
sudo systemctl status botlinkmaster
sudo journalctl -u botlinkmaster -f
```

**Auto-start:** ✅ Already enabled  
**Background:** ✅ Service mode  
**Restart on crash:** ✅ Automatic  

---

**BotLinkMaster v4.0** - Zero-config service deployment! 🎉
