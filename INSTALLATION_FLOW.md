# 🔄 BotLinkMaster - Installation Flow

## 📊 Three Stages

### Stage 1: Fresh Git Clone
**Files:** 20 files (~215 KB)
- Source code + docs only
- No runtime files

### Stage 2: After `./install.sh`
**Files:** 20 + venv/ + config files (~50-100 MB)
- System dependencies installed
- Virtual environment created
- Config files ready

### Stage 3: Production Ready
**Files:** All + database + logs
- Bot running
- Database populated
- Logs being written

---

## 🔄 Installation Process

```
Git Clone (20 files)
    ↓
./install.sh (requires root/sudo)
    ↓
Install System Dependencies
    ├── python3, pip, venv
    ├── git, curl, wget
    ├── openssh-client, telnet
    └── tzdata
    ↓
Configure Timezone (optional)
    ├── Asia/Jakarta (WIB)
    ├── Asia/Makassar (WITA)
    ├── Asia/Jayapura (WIT)
    ├── Asia/Singapore (SGT)
    ├── UTC
    └── Custom
    ↓
Switch to User
    ↓
Create venv/ + Install Packages
    ↓
Setup .env + config.py
    ↓
Initialize Database
    ↓
Installation Complete!
    ↓
Edit .env (add TELEGRAM_BOT_TOKEN)
    ↓
Run Bot (as normal user)
    ↓
Production Ready ✅
```

---

## ⚙️ Root Privileges

**Why root/sudo needed?**
- Install system packages (python3, pip, openssh, telnet)
- Configure timezone
- Set file permissions

**NOT needed for:**
- Running the bot
- Managing devices
- Normal operations

**How it works:**
```bash
./install.sh           # As user → auto requests sudo
[sudo] password:       # Enter password
# System install...    # As root
# Python setup...      # Back to user
python telegram_bot.py # As user (no root!)
```

---

## 🌍 Timezone Configuration

**Available Options:**
1. Asia/Jakarta (WIB - UTC+7)
2. Asia/Makassar (WITA - UTC+8)
3. Asia/Jayapura (WIT - UTC+9)
4. Asia/Singapore (SGT - UTC+8)
5. UTC (UTC+0)
6. Custom (any timezone)

**Check current:**
```bash
timedatectl | grep "Time zone"
```

---

## 📋 Pre-flight Checklist

### After Git Clone:
- [ ] Have root/sudo access
- [ ] Run `./install.sh`
- [ ] Select timezone
- [ ] Edit `.env` with bot token
- [ ] Test: `source venv/bin/activate && python -c "import botlinkmaster"`

### Before First Run:
- [ ] System dependencies installed
- [ ] Timezone configured
- [ ] TELEGRAM_BOT_TOKEN in `.env`
- [ ] Virtual environment activated
- [ ] Running as normal user (NOT root)

### After First Run:
- [ ] Bot responds to `/start`
- [ ] Database created
- [ ] Logs being written
- [ ] Can add devices with `/add`

---

## 🛠️ Troubleshooting

### "Module not found"
```bash
source venv/bin/activate
python telegram_bot.py
```

### "Permission denied"
```bash
chmod 600 .env config.py
```

### "Database locked"
```bash
ps aux | grep telegram_bot.py
kill <PID>
```

---

See [README.md](README.md) for full documentation.
