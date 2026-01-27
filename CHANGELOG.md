# Changelog

Semua perubahan penting pada BotLinkMaster akan didokumentasikan di file ini.

Format berdasarkan [Keep a Changelog](https://keepachangelog.com/id-ID/1.0.0/).

---

## [4.8.8] - 2025-01-26

### Fixed
- **Cisco NX-OS**: Description terpotong jika mengandung spasi
  - Masalah: "xcon:OLT C300A 1/19/1" tampil sebagai "xcon:OLT"
  - Solusi: `/int` sekarang mengambil description dari `show running-config | section interface`
  - `/cek` mengambil dari `show running-config interface <iface>`
- **Huawei VRP/Quidway**: Status interface UNKNOWN
  - Masalah: `/cek` dan `/redaman` menampilkan UNKNOWN padahal port UP
  - Root cause: `'Error' in output` terlalu luas - menangkap "Total Error:" di statistik
  - Solusi: `_is_command_error()` hanya cek 5 baris pertama untuk error pattern
- **Generic vendor patterns**: Lebih inklusif untuk berbagai format vendor
  - Sekarang juga mengenali format Huawei "current state : UP/DOWN"

### Added
- `_is_command_error()` - Deteksi error command yang lebih akurat
- `_get_all_nxos_descriptions()` - Get all descriptions from running-config
- `_get_nxos_description_from_config()` - Get single interface description

### Notes
- Minimal changes, v4.8.7 baseline preserved
- MikroTik, CloudEngine, Cisco IOS tidak terpengaruh
- Database compatible dengan versi sebelumnya

---

## [4.8.7] - 2025-01-22

### Fixed
- **MikroTik CRS326-24S+2Q+RM**: SSH algorithm compatibility untuk RouterOS 7.16.x
  - Extended KEX algorithms (curve25519-sha256, diffie-hellman-group14-sha256, dll)
  - Extended cipher algorithms (aes128-ctr, aes256-ctr, chacha20-poly1305, dll)
  - Extended key types (ssh-rsa, rsa-sha2-256, rsa-sha2-512, ssh-ed25519, dll)
- **MikroTik**: Extended timeouts untuk switch dengan banyak interface
  - `hard_timeout`: 90s → 120s
  - `command_wait`: 30s → 45s
  - `idle_timeout`: 10s → 15s
- **Huawei CE6855**: Menggunakan `display interface description` (sebelumnya `display interface brief`)
- **Cisco IOS**: Menggunakan `show interface brief` (sebelumnya `show ip interface brief`)
- **Telnet**: Perbaikan total koneksi dan eksekusi command
  - **FIX**: Login prompt detection yang salah kirim command sebagai username
  - Regex-based login detection (`Login:`, `Username:`, `Password:`)
  - Proper sequence: read banner → detect login → send username → detect password → send password
  - Idle-based reading seperti SSH (tidak lagi hanya `read_very_eager`)
  - Better prompt detection untuk command completion
  - Support MikroTik, Cisco, Huawei, dan vendor lainnya
- Improved prompt detection untuk semua vendor

### Added
- `/int` sebagai alias untuk `/interfaces` (lebih singkat)
- Chat ID langsung ditampilkan saat `/start`
- `update.sh` dengan version checking dan rollback
- `VERSION` file untuk tracking versi
- `CHANGELOG.md` untuk dokumentasi perubahan
- `_wait_for_prompt_telnet()` method untuk Telnet prompt detection

### Changed
- `/start` sekarang menampilkan Chat ID langsung
- `/help` dan `/help2` menggunakan `/int` sebagai command utama
- Consistent versioning di semua file

---

## [4.8.6] - 2025-01-20

### Fixed
- MikroTik interface parsing untuk format dengan flags (R, S, X, D)
- Cisco NX-OS interface status detection

### Added
- Pagination untuk `/interfaces` (20 interface per halaman)
- Support untuk MikroTik CRS317 dan CRS326

---

## [4.7.0] - 2025-01-15

### Added
- Multi Chat ID support (personal + group)
- IANA timezone configuration
- `/timezone` dan `/settz` commands
- `/myid` command untuk mendapatkan Chat ID

### Changed
- Konfigurasi timezone menggunakan format IANA (Asia/Jakarta, dll)
- `.env` support untuk ALLOWED_CHAT_IDS

---

## [4.6.0] - 2025-01-10

### Added
- Support 18 vendor (tambah DCN, Raisecom, Allied Telesis, Datacom)
- Optical power monitoring dengan level indicators
- `/redaman` dan `/optical` commands

### Changed
- Improved connection handling untuk semua vendor
- Better error messages

---

## [4.5.0] - 2025-01-05

### Added
- Initial public release
- Support untuk: Cisco IOS, Cisco NX-OS, Huawei, ZTE, Juniper, MikroTik, Nokia, HP/Aruba, FiberHome, H3C, Ruijie, BDCOM, FS
- SSH dan Telnet support
- `/interfaces`, `/cek`, `/add`, `/list`, `/delete` commands
- SQLite database untuk menyimpan device

---

## Version Format

Menggunakan [Semantic Versioning](https://semver.org/):
- **MAJOR.MINOR.PATCH**
- MAJOR: Perubahan besar yang tidak backward compatible
- MINOR: Fitur baru yang backward compatible
- PATCH: Bug fixes

---

## Upgrade Notes

### Dari v4.5.x / v4.6.x / v4.7.x ke v4.8.7

Update aman, tidak ada breaking changes:
```bash
./update.sh
```

File yang diupdate:
- `telegram_bot.py`
- `botlinkmaster.py`
- `vendor_commands.py`
- `database.py`
- `timezone_config.py`

File yang dipertahankan:
- `botlinkmaster.db` (database)
- `.env` (konfigurasi)
- `timezone.conf` (timezone)
- `botlinkmaster.log` (log)
