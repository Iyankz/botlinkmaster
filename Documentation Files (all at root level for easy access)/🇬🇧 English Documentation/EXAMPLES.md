# 📚 BotLinkMaster - Usage Examples

## Example 1: Basic Device Management

### Add Device via Telegram
```
/add
nama: core-switch-1
host: 10.0.0.1
username: admin
password: Sw1tch@2024
protocol: ssh
port: 22
description: Core Switch - Data Center
location: DC1-Rack-A-U10
```

### Check Interface Status
```
/cek core-switch-1 GigabitEthernet1/0/1
```

Result:
```
🟢 Interface Status

Device: core-switch-1
Interface: GigabitEthernet1/0/1
Status: UP
Description: Uplink to Router
IP Address: 10.0.1.1/30
```

---

## Example 2: Multi-Site Monitoring

### Scenario
Monitor devices across 3 locations via Telegram.

### Setup
```
# Add HQ Router
/add
nama: hq-router
host: 192.168.1.1
username: admin
password: pass123
protocol: ssh
location: Head Office

# Add Branch Router  
/add
nama: branch-jakarta-router
host: 192.168.10.1
username: admin
password: pass123
protocol: ssh
location: Jakarta Branch

# Add Branch Router
/add
nama: branch-bandung-router
host: 192.168.20.1
username: admin
password: pass123
protocol: ssh
location: Bandung Branch
```

### Monitor All Sites
```
# Check HQ uplink
/cek hq-router Gi0/0/0

# Check Jakarta WAN
/cek branch-jakarta-router Gi0/0/1

# Check Bandung WAN
/cek branch-bandung-router Gi0/0/1
```

---

## Example 3: Using CLI

### Add Device
```bash
./cli.py add router-1 192.168.1.1 admin password123 \
  --protocol ssh \
  --port 22 \
  --description "Edge Router" \
  --location "Network Room"
```

### List All Devices
```bash
./cli.py list
```

### Test Connection
```bash
./cli.py test router-1
```

### Check Interface
```bash
./cli.py check router-1 GigabitEthernet0/0
```

### Show Device Details
```bash
./cli.py show router-1
```

---

## Example 4: Python Integration

```python
from botlinkmaster import BotLinkMaster, ConnectionConfig, Protocol
from database import DatabaseManager

# Initialize database
db = DatabaseManager()

# Add device
device = db.add_device(
    name="test-switch",
    host="192.168.1.10",
    username="admin",
    password="password",
    protocol="ssh"
)

# Connect and check interface
config = ConnectionConfig(
    host=device.host,
    username=device.username,
    password=device.password,
    protocol=Protocol.SSH
)

with BotLinkMaster(config) as bot:
    if bot.connected:
        # Get all interfaces
        interfaces = bot.get_interfaces()
        for iface in interfaces:
            print(f"{iface['name']}: {iface['status']}")
        
        # Get specific interface
        info = bot.get_specific_interface("GigabitEthernet0/1")
        if info:
            print(f"Status: {info['status']}")
```

---

## Example 5: Troubleshooting Workflow

### Scenario: Interface Down Alert

1. **Receive alert** (from monitoring system)
2. **Quick check via Telegram:**
   ```
   /cek problem-device GigabitEthernet0/5
   ```

3. **If down, check device details:**
   ```
   /device problem-device
   ```

4. **Check all interfaces:**
   ```bash
   ./cli.py test problem-device
   ```

5. **Document findings** in cache for later review

---

## Example 6: Scheduled Monitoring (Cron)

### Setup Cron Job

```bash
# Edit crontab
crontab -e

# Add job to check critical interfaces every 5 minutes
*/5 * * * * cd /path/to/botlinkmaster && /path/to/botlinkmaster/venv/bin/python3 << 'EOF'
from botlinkmaster import BotLinkMaster, ConnectionConfig, Protocol
from database import DatabaseManager

db = DatabaseManager()
device = db.get_device("critical-router")

if device:
    config = ConnectionConfig(
        host=device.host,
        username=device.username,
        password=device.password,
        protocol=Protocol.SSH if device.protocol == 'ssh' else Protocol.TELNET
    )
    
    with BotLinkMaster(config) as bot:
        if bot.connected:
            info = bot.get_specific_interface("GigabitEthernet0/0")
            if info and "up" not in info.get('status', '').lower():
                # Send alert (implement your notification)
                print(f"ALERT: Interface down on {device.name}")
EOF
```

---

## More Examples

See [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) for technical details.
