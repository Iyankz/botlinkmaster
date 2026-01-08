# 🔧 BotLinkMaster - Troubleshooting Guide

## ❌ ERROR: TELEGRAM_BOT_TOKEN tidak ditemukan!

### Penyebab:
Bot tidak bisa membaca file `.env`

### Solusi:

#### 1. Pastikan file .env ada di directory yang benar

```bash
# Cek apakah .env ada
ls -la .env

# Harus menampilkan:
# -rw------- 1 user user 123 Jan 07 10:00 .env
```

#### 2. Pastikan .env berisi token yang benar

```bash
# Lihat isi .env
cat .env

# Harus ada baris:
# TELEGRAM_BOT_TOKEN=123456:ABCdefGHIjklMNOpqrsTUVwxyz
```

#### 3. Pastikan tidak ada spasi di sekitar tanda =

❌ **SALAH:**
```
TELEGRAM_BOT_TOKEN = your_token
TELEGRAM_BOT_TOKEN= your_token
TELEGRAM_BOT_TOKEN =your_token
```

✅ **BENAR:**
```
TELEGRAM_BOT_TOKEN=123456:ABCdefGHIjklMNOpqrsTUVwxyz
```

#### 4. Pastikan virtual environment aktif

```bash
# Cek apakah venv aktif (harus ada tulisan (venv) di prompt)
# SALAH:
lab@lab:~/botlinkmaster$ python telegram_bot.py

# BENAR:
(venv) lab@lab:~/botlinkmaster$ python telegram_bot.py

# Activate venv jika belum:
source venv/bin/activate
```

#### 5. Test apakah bot bisa baca .env

```bash
source venv/bin/activate
python3 << 'EOF'
from dotenv import load_dotenv
import os

load_dotenv()
token = os.getenv('TELEGRAM_BOT_TOKEN')

if token:
    print(f"✅ Token ditemukan: {token[:10]}...")
else:
    print("❌ Token tidak ditemukan!")
    print("\nCek file .env Anda")
EOF
```

---

## 🆔 Cara Mendapatkan Chat ID

### Method 1: Gunakan Bot (Paling Mudah)

1. Jalankan bot:
```bash
source venv/bin/activate
python telegram_bot.py
```

2. Buka Telegram dan chat dengan bot Anda

3. Kirim command:
```
/myid
```

4. Bot akan reply dengan Chat ID Anda:
```
📱 Informasi Anda

Chat ID: 123456789
Username: @your_username
Nama: Your Name
```

### Method 2: Manual via @userinfobot

1. Buka Telegram
2. Search: `@userinfobot`
3. Start chat dan kirim pesan apapun
4. Bot akan reply dengan ID Anda

### Method 3: Via URL

1. Buka: https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates
2. Send a message to your bot
3. Refresh the URL
4. Look for "chat":{"id":123456789}

---

## 🔒 Membatasi Akses Bot (ALLOWED_CHAT_IDS)

### Mengapa Perlu Dibatasi?

- Mencegah orang lain menggunakan bot Anda
- Keamanan: hanya Anda yang bisa akses perangkat
- Kontrol akses untuk tim

### Cara Konfigurasi:

#### 1. Dapatkan Chat ID Anda

Gunakan `/myid` di bot (lihat section di atas)

#### 2. Edit file .env

```bash
nano .env
```

#### 3. Tambahkan Chat ID

**Single user:**
```
ALLOWED_CHAT_IDS=123456789
```

**Multiple users (pisah dengan koma):**
```
ALLOWED_CHAT_IDS=123456789,987654321,456789123
```

**No restriction (allow all):**
```
ALLOWED_CHAT_IDS=
```

#### 4. Restart bot

```bash
# Ctrl+C untuk stop bot, lalu:
python telegram_bot.py
```

### Pesan yang Muncul Jika Tidak Authorized:

```
❌ Access Denied

Anda tidak memiliki akses ke bot ini.

Your Chat ID: 999999999

Hubungi administrator untuk mendapatkan akses.
```

---

## 🐛 Error Lainnya

### Module not found: paramiko, telegram, sqlalchemy

**Penyebab:** Virtual environment tidak aktif

**Solusi:**
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### CryptographyDeprecationWarning

**Penyebab:** Warning dari Paramiko (bukan error)

**Solusi:** Abaikan atau upgrade paramiko:
```bash
pip install --upgrade paramiko
```

### Database locked

**Penyebab:** Ada 2 instance bot yang running

**Solusi:**
```bash
# Cari process
ps aux | grep telegram_bot.py

# Kill process
kill <PID>

# Atau kill all
pkill -f telegram_bot.py
```

### Connection failed / Timeout

**Penyebab:** Tidak bisa koneksi ke device

**Solusi:**
1. Cek host/IP benar
2. Cek port benar (SSH:22, Telnet:23)
3. Cek username/password benar
4. Cek device bisa di-ping:
   ```bash
   ping 192.168.1.1
   ```
5. Cek firewall tidak memblokir

---

## ✅ Checklist Troubleshooting

Sebelum bertanya, pastikan sudah cek:

- [ ] File .env ada dan berisi TELEGRAM_BOT_TOKEN
- [ ] Token tidak ada spasi di sekitar tanda =
- [ ] Virtual environment aktif (ada tulisan (venv) di prompt)
- [ ] Dependencies terinstall (pip list | grep telegram)
- [ ] Bot token valid (dari @BotFather)
- [ ] Chat ID sudah di-configure di ALLOWED_CHAT_IDS (jika digunakan)
- [ ] Tidak ada bot lain yang running

---

## 📝 Log Files

Cek log untuk detail error:

```bash
# Lihat log
tail -f botlinkmaster.log

# Lihat 50 baris terakhir
tail -50 botlinkmaster.log

# Search error
grep ERROR botlinkmaster.log
```

---

## 🆘 Masih Bermasalah?

1. Pastikan sudah cek semua di atas
2. Lihat log file untuk detail error
3. Coba run ulang installer:
   ```bash
   ./install.sh
   ```
4. Buka issue di GitHub dengan:
   - Versi OS
   - Error message lengkap
   - Output dari `python --version`
   - Isi log (tanpa credential!)

---

**Last Updated:** January 7, 2026
**Version:** 4.0.1
