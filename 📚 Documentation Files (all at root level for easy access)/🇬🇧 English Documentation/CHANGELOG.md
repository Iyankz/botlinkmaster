# Changelog

All notable changes to BotLinkMaster will be documented in this file.

## [4.1.0] - 2026-01-07

### 🎉 Major Update - Service Edition

#### Added - Systemd Service Integration
- **Complete systemd service support** - Bot runs as background service
- **`install-complete.sh`** - One-command installer that sets up everything
- **`botctl`** - Easy service management script (start, stop, restart, status, logs)
- **`setup-service.sh`** - Manual service installer
- **`botlinkmaster.service`** - Production-ready systemd service file
- Auto-start on boot (enabled by default)
- Auto-restart on crash (10s delay, max 5 attempts)
- Resource limits (512MB RAM, 100% CPU)
- Security hardening (NoNewPrivileges, ProtectSystem, etc)
- Integrated logging with systemd journal

#### Added - Environment & Configuration
- **`.env` file support with python-dotenv** - Fixed environment variable loading
- **ALLOWED_CHAT_IDS** - Restrict bot access to specific Telegram users
- `/myid` command - Users can get their Chat ID for access control
- Authorization check on all commands
- Access denied message with user's Chat ID

#### Added - Diagnostic Tools
- **`diagnose.py`** - Complete diagnostic script
  - Check .env file
  - Verify bot token
  - Test Telegram API connection
  - Check dependencies
  - Verify database
  - Show bot info (username, ID)
- **`test_bot.py`** - Simple test bot for connection verification
- Enhanced logging with verbose output
- Token validation in startup

#### Added - Documentation
- **`README_SERVICE.md`** - Service-focused main documentation
- **`SERVICE_GUIDE.md`** - Complete systemd service guide
- **`QUICKSTART_SERVICE.md`** - 5-minute quick start for service mode
- **`DEPLOYMENT_SUMMARY.md`** - Full deployment overview
- **`INSTALL_CARD.txt`** - Quick reference installation card
- **`QUICK_FIX.md`** - Fast problem resolution guide
- **`TROUBLESHOOTING.md`** - Enhanced with service troubleshooting
- **`FIX_SUMMARY_v4.0.1.md`** - Fix documentation for .env loading

#### Changed
- Installer now offers systemd service setup during installation
- Enhanced error messages with troubleshooting hints
- Improved logging format and verbosity
- Bot startup now includes comprehensive checks
- All scripts made executable with proper permissions

#### Fixed
- **Critical:** Fixed .env file not loading (missing load_dotenv())
- **Critical:** Bot token not found error resolved
- Fixed color output in install.sh (echo -e for escape sequences)
- Fixed install-simple.sh for terminals without color support

#### Security
- Chat ID-based access control
- Service runs as non-root user
- Limited file system access
- Protected system directories
- No new privileges allowed
- Private temporary directory

#### Performance
- Resource limits prevent runaway processes
- Memory cap at 512MB
- CPU quota at 100% (1 core)
- Efficient restart policy

---

## [4.0.0] - 2026-01-06

### 🎉 Major Release - Complete Rewrite

#### Added
- SSH connection support via Paramiko
- Telnet connection support
- SQLAlchemy ORM database integration
- Telegram Bot interface with rich commands
- CLI tool with Rich formatting
- Interface description tracking
- Interface status caching
- Custom port configuration
- Multi-device management
- Docker support
- Systemd service template
- Comprehensive documentation
- Automated installation script with:
  - Root privilege management
  - System dependency installation
  - Timezone configuration
  - Multi-OS support (Ubuntu, CentOS, Arch)

#### Changed
- **BREAKING:** Migrated from SNMP to SSH/Telnet
- **BREAKING:** Renamed from `remonbot` to `botlinkmaster`
- **BREAKING:** Replaced file-based config with database storage
- Improved error handling and logging
- Better connection management

#### Removed
- SNMP protocol support
- File-based configuration
- Fixed port configuration

### Migration Guide from v3.x

**v3 (remonbot) → v4 (botlinkmaster)**

1. **Install v4:**
   ```bash
   git clone https://github.com/yourusername/botlinkmaster.git
   cd botlinkmaster
   ./install.sh
   ```

2. **Migrate devices:**
   ```bash
   # Old v3 config.py format:
   DEVICES = {
       'router1': {'ip': '192.168.1.1', 'community': 'public'}
   }
   
   # New v4 Telegram format:
   /add
   nama: router1
   host: 192.168.1.1
   username: admin
   password: your_password
   protocol: ssh
   ```

3. **Update monitoring:**
   - v3: `/cek router1` (SNMP)
   - v4: `/cek router1 GigabitEthernet0/0` (SSH/interface-specific)

---

## [3.0.0] - 2025-XX-XX (Legacy)

### Added
- SNMP monitoring support
- Basic Telegram bot
- File-based configuration

### Deprecated
- Will be replaced by v4.0 with SSH/Telnet

---

## [2.0.0] - 2024-XX-XX (EOL)

End of Life - No longer supported

---

## Version Naming

**Format:** MAJOR.MINOR.PATCH

- **MAJOR:** Breaking changes, major features
- **MINOR:** New features, non-breaking changes
- **PATCH:** Bug fixes, minor improvements

---

## Upgrade Paths

### v4.0.x → v4.1.0

**What's New:**
- Systemd service integration
- Auto-start on boot
- Easy management with botctl
- Chat ID access control
- Enhanced diagnostics

**How to Upgrade:**

1. Stop current bot:
   ```bash
   # If running manually:
   Ctrl+C
   
   # If running as old service:
   sudo systemctl stop botlinkmaster
   ```

2. Backup data:
   ```bash
   cp .env .env.backup
   cp botlinkmaster.db botlinkmaster.db.backup
   ```

3. Pull updates:
   ```bash
   git pull
   ```

4. Run new installer:
   ```bash
   chmod +x install-complete.sh
   sudo ./install-complete.sh
   ```

5. Restore .env:
   ```bash
   cp .env.backup .env
   ```

6. Start service:
   ```bash
   sudo systemctl start botlinkmaster
   ```

**No breaking changes** - All v4.0 data and configs are compatible!

---

**Current Stable:** v4.1.0  
**Previous Stable:** v4.0.0  
**Next Release:** v4.2.0 (Q1 2026) - Advanced Monitoring Features
