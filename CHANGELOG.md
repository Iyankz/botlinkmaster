# Changelog

All notable changes to BotLinkMaster will be documented in this file.

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

**Current Stable:** v4.0.0  
**Next Release:** v4.1.0 (Q1 2026)
