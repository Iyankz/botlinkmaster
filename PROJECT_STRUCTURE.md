# 🏗️ BotLinkMaster - Project Structure

## 📊 Overview

- **Language:** Python 3.8+
- **Framework:** python-telegram-bot
- **Database:** SQLAlchemy ORM
- **Protocols:** SSH (Paramiko), Telnet

---

## 📄 Core Files

### botlinkmaster.py
**Purpose:** SSH/Telnet connection handler

**Key Classes:**
- `Protocol(Enum)` - SSH/Telnet enum
- `ConnectionConfig` - Connection config dataclass
- `BotLinkMaster` - Main connection class

**Features:**
- Auto SSH/Telnet selection
- Command execution
- Interface parsing
- Context manager support

### database.py
**Purpose:** Database ORM and operations

**Models:**
- `Device` - Network device information
- `InterfaceCache` - Interface status cache

**Manager:**
- `DatabaseManager` - CRUD operations

### telegram_bot.py
**Purpose:** Telegram bot interface

**Commands:**
- `/start`, `/help`, `/list`
- `/add`, `/device`, `/delete`
- `/cek` (main command)

### cli.py
**Purpose:** Command-line tool

**Commands:**
- `list`, `add`, `delete`
- `show`, `test`, `check`
- `stats`

---

## 🗄️ Database Schema

### devices table
```sql
- id (INTEGER, PK)
- name (VARCHAR, UNIQUE)
- host (VARCHAR)
- username (VARCHAR)
- password (VARCHAR)
- protocol (ENUM: ssh/telnet)
- port (INTEGER, nullable)
- description (TEXT, nullable)
- location (VARCHAR, nullable)
- created_at (DATETIME)
- updated_at (DATETIME)
```

### interface_cache table
```sql
- id (INTEGER, PK)
- device_name (VARCHAR, indexed)
- interface_name (VARCHAR)
- status (VARCHAR)
- protocol_status (VARCHAR)
- description (TEXT)
- last_checked (DATETIME)
```

---

## 🔐 Security

### Sensitive Files (NEVER COMMIT)
- `.env` - Bot token
- `config.py` - May contain secrets
- `*.db` - Device credentials
- `*.log` - May contain sensitive info

### Recommendations
1. Use strong passwords
2. Enable firewall rules
3. Use SSH keys when possible
4. Rotate credentials regularly
5. Limit Telegram bot access
6. Use PostgreSQL for production
7. Enable SSL/TLS connections

---

## 📈 Performance

### Optimization Tips
1. Use PostgreSQL for >100 devices
2. Enable connection pooling
3. Set appropriate timeouts
4. Cache interface data
5. Use Redis for sessions (future)

### Resource Usage
- Memory: ~50-100 MB
- CPU: <5% (idle)
- Disk: <10 MB (+ database)
- Network: Minimal (SSH/Telnet only)

---

See [MILESTONES.md](MILESTONES.md) for roadmap.
