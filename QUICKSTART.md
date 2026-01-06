# 🚀 Quick Start Guide - BotLinkMaster v4.0

## Setup dalam 5 Menit

**⚠️ Penting:** Script installer memerlukan root/sudo privileges.

### 1️⃣ Download dan Extract
```bash
git clone https://github.com/yourusername/botlinkmaster.git
cd botlinkmaster
```

### 2️⃣ Install Dependencies
```bash
# Run installer (akan meminta sudo otomatis)
chmod +x install.sh
./install.sh

# Installer akan:
# - Install system packages (python3, pip, openssh, telnet)
# - Setup timezone (dengan pilihan)
# - Create virtual environment
# - Install Python dependencies
# - Setup configuration files
```

### 3️⃣ Configure Bot Token
```bash
# Edit .env file
nano .env

# Add your bot token:
TELEGRAM_BOT_TOKEN=your_token_from_botfather
```

### 4️⃣ Jalankan Bot
```bash
# Activate virtual environment
source venv/bin/activate

# Run bot (sebagai user biasa, TIDAK perlu root)
python telegram_bot.py
```

✅ **Bot siap digunakan!** Buka Telegram dan mulai chat dengan bot Anda.

---

## 📋 Quick Commands

```bash
# Add device via CLI
./cli.py add router-1 192.168.1.1 admin password --protocol ssh

# List devices
./cli.py list

# Test connection
./cli.py test router-1

# Check interface
./cli.py check router-1 GigabitEthernet0/0
```

---

## 🐳 Docker Quick Start

```bash
# Setup .env
cp .env.example .env
nano .env

# Run with Docker
chmod +x docker-run.sh
./docker-run.sh

# View logs
docker-compose logs -f
```

---

## 🎯 First Steps in Telegram

1. Open Telegram
2. Search for your bot
3. Send `/start`
4. Add a device with `/add`
5. Check interface with `/cek`

---

**Next:** Read [EXAMPLES.md](EXAMPLES.md) for usage examples
