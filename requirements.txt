# 📋 BotLinkMaster v4.1.0 - Requirements

Dokumen ini berisi daftar lengkap requirements untuk menjalankan BotLinkMaster.

---

## 🖥️ System Requirements

### Minimum Requirements

| Komponen | Spesifikasi |
|----------|-------------|
| **Operating System** | Ubuntu 20.04+ / Debian 10+ / CentOS 7+ / RHEL 7+ / Fedora 30+ / Arch Linux |
| **CPU** | 1 Core @ 1 GHz |
| **RAM** | 512 MB |
| **Storage** | 150 MB minimum (100 MB aplikasi + 50 MB database) |
| **Network** | Koneksi internet untuk Telegram API |
| **Privileges** | Root/sudo access untuk instalasi |

### Recommended Requirements

| Komponen | Spesifikasi |
|----------|-------------|
| **Operating System** | Ubuntu 22.04 LTS atau Debian 11+ |
| **CPU** | 2 Cores @ 2 GHz |
| **RAM** | 1 GB |
| **Storage** | 500 MB (untuk growth) |
| **Network** | Koneksi internet stabil 1 Mbps+ |
| **Privileges** | Root/sudo untuk instalasi, user biasa untuk operasional |

### Production Requirements

| Komponen | Spesifikasi |
|----------|-------------|
| **Operating System** | Ubuntu 22.04 LTS (untuk long-term support) |
| **CPU** | 2-4 Cores |
| **RAM** | 2 GB |
| **Storage** | 1 GB SSD |
| **Network** | Redundant internet connection |
| **Backup** | Regular backup strategy |

---

## 💻 Software Requirements

### Operating System Support

**Fully Tested:**
- ✅ Ubuntu 20.04 LTS
- ✅ Ubuntu 22.04 LTS
- ✅ Debian 11 (Bullseye)
- ✅ Debian 12 (Bookworm)

**Compatible (Should Work):**
- ✅ CentOS 7, 8
- ✅ RHEL 7, 8, 9
- ✅ Fedora 30+
- ✅ Arch Linux
- ✅ Rocky Linux 8+
- ✅ AlmaLinux 8+

**Not Supported:**
- ❌ Windows (use WSL2 or Docker)
- ❌ macOS (use Docker)

### Python Requirements

**Version:**
- **Minimum:** Python 3.8
- **Recommended:** Python 3.11+
- **Tested:** Python 3.8, 3.9, 3.10, 3.11

**Python Components:**
- python3
- python3-pip
- python3-venv
- python3-dev (untuk beberapa package)

### System Packages

**Required (otomatis terinstall oleh installer):**
```bash
# Core
python3, python3-pip, python3-venv

# Version Control
git

# Network Tools
curl, wget, openssh-client, telnet

# System
tzdata
```

**Optional (untuk fitur tambahan):**
```bash
# Database (jika pakai PostgreSQL/MySQL)
postgresql-client    # Untuk PostgreSQL
mysql-client        # Untuk MySQL

# Monitoring
htop, iotop         # Untuk monitoring resource

# Debugging
strace, tcpdump     # Untuk debugging
```

### Python Package Requirements

**Core Dependencies (requirements.txt):**
```python
# SSH/Telnet
paramiko==3.4.0

# Telegram Bot
python-telegram-bot==20.7

# Database
SQLAlchemy==2.0.25

# CLI
click==8.1.7
rich==13.7.0

# Configuration
python-dotenv==1.0.0
```

**Optional Dependencies:**
```python
# PostgreSQL
psycopg2-binary==2.9.9

# MySQL
PyMySQL==1.1.0

# Monitoring
prometheus-client==0.19.0
```

---

## 🌐 Network Requirements

### Internet Connectivity

**Required:**
- Stable internet connection
- Minimum bandwidth: 256 kbps
- Recommended bandwidth: 1 Mbps+
- Low latency preferred (< 200ms ke api.telegram.org)

### Firewall Configuration

**Outbound (MUST Allow):**
- Port 443 (HTTPS) - Telegram API
  - Destination: api.telegram.org
  - Protocol: TCP
  
- Port 22 (SSH) - Device connections
  - Destination: Network devices
  - Protocol: TCP
  
- Port 23 (Telnet) - Device connections (opsional)
  - Destination: Network devices
  - Protocol: TCP

**Inbound:**
- ❌ No inbound ports required
- Bot uses outbound polling only

### DNS Requirements

**Required Domains:**
```
api.telegram.org
*.telegram.org
```

### Proxy Support

Bot mendukung proxy jika diperlukan:
- HTTP Proxy
- HTTPS Proxy
- SOCKS5 Proxy

Konfigurasi via environment variables atau config file.

---

## 📱 Telegram Requirements

### Bot Setup

**Prerequisites:**
1. Akun Telegram aktif
2. Bot token dari @BotFather
3. Basic understanding perintah bot

**Mendapatkan Bot Token:**
1. Buka Telegram, cari @BotFather
2. Kirim `/newbot`
3. Ikuti instruksi untuk membuat bot
4. Simpan token yang diberikan (format: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

**Bot Permissions:**
- Tidak perlu admin privileges
- Tidak perlu join groups (bot personal)
- Tidak perlu inline mode

---

## 🖧 Target Device Requirements

### Network Devices

**Minimum Requirements:**
- SSH atau Telnet enabled
- User account dengan privilege untuk show commands
- Standard CLI interface
- Reachable dari server bot (routing, firewall)

**Recommended:**
- SSH dengan public key authentication
- Dedicated monitoring user
- Standard Cisco-like command syntax
- Consistent interface naming

### Supported Devices

**Tested & Fully Supported:**
- ✅ Cisco IOS (12.x, 15.x)
- ✅ Cisco IOS-XE (16.x, 17.x)
- ✅ Cisco NX-OS (7.x, 9.x)

**Compatible (Should Work):**
- ✅ Juniper JunOS
- ✅ HP/Aruba switches
- ✅ MikroTik RouterOS
- ✅ Dell Networking
- ✅ Huawei VRP

**Partial Support:**
- ⚠️ Linux servers (via SSH)
- ⚠️ Generic SSH/Telnet devices
- ⚠️ Custom/proprietary devices

**Not Supported:**
- ❌ SNMP-only devices
- ❌ Devices without CLI
- ❌ Web-only management

### Device Access Requirements

**User Permissions Needed:**
```
show interfaces
show interface description
show running-config interface (optional)
show ip interface brief (optional)
```

**Recommended User Setup:**
```
# Cisco example
username botmonitor privilege 1 secret <password>
privilege exec level 1 show interfaces
privilege exec level 1 show interface
privilege exec level 1 show ip interface
```

---

## 💾 Storage Requirements

### Disk Space

**Initial Installation:**
- Python packages: ~50 MB
- Application files: ~10 MB
- Virtual environment: ~50 MB
- **Total:** ~110 MB

**Runtime Growth:**
- Database: ~1 MB per 100 devices
- Logs: ~1-5 MB per day
- Cache: ~5-10 MB
- **Estimate:** +50-200 MB untuk production

**Recommended Free Space:**
- Minimum: 200 MB free
- Recommended: 500 MB free
- Production: 1 GB+ free

### Database

**Supported Databases:**
- SQLite (default, recommended untuk < 1000 devices)
- PostgreSQL (recommended untuk production)
- MySQL/MariaDB (supported)

**Database Size Estimates:**
| Devices | Cached Interfaces | Database Size |
|---------|-------------------|---------------|
| 10 | 100 | ~500 KB |
| 50 | 500 | ~2 MB |
| 100 | 1000 | ~5 MB |
| 500 | 5000 | ~25 MB |
| 1000 | 10000 | ~50 MB |

---

## 🔒 Security Requirements

### User Permissions

**Installation (Requires root/sudo):**
- Install system packages
- Configure systemd service
- Set file permissions
- Configure timezone

**Operation (Regular user):**
- Read/write application files
- Access database
- Network connectivity
- No root required

### File Permissions

**Secure Files:**
- `.env` - 600 (rw-------)
- `config.py` - 600 (rw-------)
- `botlinkmaster.db` - 600 (rw-------)
- Private keys - 600 (rw-------)

**Executable Files:**
- `*.sh` scripts - 755 (rwxr-xr-x)
- `*.py` scripts - 755 (rwxr-xr-x)

**Regular Files:**
- Documentation - 644 (rw-r--r--)
- Config templates - 644 (rw-r--r--)

---

## 🎯 Performance Requirements

### Resource Limits (systemd service)

**Default Configuration:**
```ini
MemoryMax=512M
CPUQuota=100%
```

**Recommended for Production:**
```ini
MemoryMax=1G
CPUQuota=200%
```

### Expected Resource Usage

**Idle:**
- CPU: < 1%
- RAM: 50-100 MB
- Network: < 1 KB/s

**Light Load (10 checks/minute):**
- CPU: 2-5%
- RAM: 100-150 MB
- Network: 10-20 KB/s

**Heavy Load (100 checks/minute):**
- CPU: 10-20%
- RAM: 150-300 MB
- Network: 50-100 KB/s

---

## ✅ Pre-Installation Checklist

Sebelum install, pastikan:

### System
- [ ] OS yang didukung (Ubuntu/Debian/CentOS/dll)
- [ ] Root/sudo access tersedia
- [ ] Minimum 200 MB disk space free
- [ ] Minimum 512 MB RAM available
- [ ] Internet connection available

### Software
- [ ] Python 3.8+ installed (atau akan diinstall)
- [ ] git installed (atau akan diinstall)
- [ ] No conflicting services di port 443

### Network
- [ ] Firewall allow outbound ke api.telegram.org:443
- [ ] Firewall allow outbound ke devices (port 22/23)
- [ ] DNS resolution working
- [ ] No proxy issues (atau proxy configured)

### Telegram
- [ ] Punya akun Telegram
- [ ] Sudah punya bot token dari @BotFather
- [ ] Token valid dan tidak expired

### Devices
- [ ] Devices reachable via network
- [ ] SSH atau Telnet enabled di devices
- [ ] User credentials tersedia
- [ ] Firewall di devices allow connection dari bot server

---

## 🚀 Post-Installation Requirements

Setelah install, verify:

### System Service
- [ ] Service installed: `systemctl status botlinkmaster`
- [ ] Service enabled: `systemctl is-enabled botlinkmaster`
- [ ] Service running: `systemctl is-active botlinkmaster`
- [ ] No errors in logs: `journalctl -u botlinkmaster -n 50`

### Configuration
- [ ] .env file exists dengan valid token
- [ ] config.py configured (jika dimodifikasi)
- [ ] Database initialized
- [ ] Permissions correct (600 untuk sensitive files)

### Network
- [ ] Bot dapat connect ke Telegram API
- [ ] Bot dapat connect ke devices
- [ ] No firewall blocking connections

### Functionality
- [ ] Bot responds to `/start` di Telegram
- [ ] Can add devices via `/add`
- [ ] Can check interfaces via `/cek`
- [ ] Logs being written

---

## 📞 Support & Compatibility

### Tested Configurations

**Most Tested (Recommended):**
- Ubuntu 22.04 LTS + Python 3.11 + SQLite
- Ubuntu 20.04 LTS + Python 3.9 + SQLite
- Debian 11 + Python 3.9 + SQLite

**Production Tested:**
- Ubuntu 22.04 LTS + Python 3.11 + PostgreSQL 14
- CentOS 8 + Python 3.9 + PostgreSQL 13

### Known Issues

**Platform-Specific:**
- CentOS 7: Perlu install Python 3.8+ dari EPEL
- Arch Linux: Package names mungkin berbeda
- WSL2: Systemd support limited (gunakan manual mode)

**Network-Specific:**
- Beberapa corporate proxy perlu konfigurasi khusus
- Beberapa firewall perlu whitelist api.telegram.org
- IPv6-only networks: Bot support IPv4 dan IPv6

---

## 🆘 Troubleshooting Requirements

Jika ada masalah terkait requirements:

### System Requirements
```bash
# Cek OS
cat /etc/os-release

# Cek Python version
python3 --version

# Cek disk space
df -h

# Cek memory
free -h

# Cek CPU
nproc
```

### Network Requirements
```bash
# Test Telegram API
curl -I https://api.telegram.org

# Test device connectivity
ping <device-ip>
telnet <device-ip> 22

# Check open ports
netstat -tuln
```

### Package Requirements
```bash
# Check installed packages
pip list

# Check system packages
dpkg -l | grep python3  # Debian/Ubuntu
rpm -qa | grep python3  # CentOS/RHEL
```

---

**BotLinkMaster v4.1.0** - Complete Requirements Documentation
