"""
BotLinkMaster v4.0 - Configuration Template
Copy this file to config.py and adjust settings

Usage:
    cp config_example.py config.py
    # Edit config.py with your settings
"""

# Database Configuration
# Supported: sqlite, postgresql, mysql
# Examples:
#   SQLite: sqlite:///botlinkmaster.db
#   PostgreSQL: postgresql://user:password@localhost/botlinkmaster
#   MySQL: mysql+pymysql://user:password@localhost/botlinkmaster
DATABASE_URL = "sqlite:///botlinkmaster.db"

# Connection Timeouts (seconds)
SSH_TIMEOUT = 30
TELNET_TIMEOUT = 30
COMMAND_WAIT_TIME = 2.0

# Logging Configuration
LOG_FILE = "botlinkmaster.log"
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Cache Settings
CACHE_EXPIRE_HOURS = 24  # How long to keep interface cache

# Telegram Bot Settings (optional restrictions)
# Leave empty to allow all users
ALLOWED_USER_IDS = []  # Example: [123456789, 987654321]
ALLOWED_USERNAMES = []  # Example: ["username1", "username2"]

# Rate Limiting (per user)
MAX_REQUESTS_PER_MINUTE = 10
MAX_REQUESTS_PER_HOUR = 100

# Device Connection Settings
MAX_CONCURRENT_CONNECTIONS = 5  # Maximum parallel device connections
CONNECTION_RETRY_ATTEMPTS = 3
CONNECTION_RETRY_DELAY = 5  # seconds

# Security Settings
ENCRYPT_PASSWORDS = False  # Enable password encryption in database (future feature)
REQUIRE_STRONG_PASSWORDS = False  # Enforce password complexity

# Performance Settings
ENABLE_CONNECTION_POOLING = False  # Connection pooling (future feature)
MAX_POOL_SIZE = 10
