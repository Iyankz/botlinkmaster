#!/usr/bin/env python3
"""
BotLinkMaster v4.8.8 - Timezone Configuration
IANA Timezone support with examples from each continent

Author: BotLinkMaster
Version: 4.8.7
"""

from datetime import datetime
from typing import Dict, List
import os

try:
    from zoneinfo import ZoneInfo
    USING_ZONEINFO = True
except ImportError:
    try:
        import pytz
        USING_ZONEINFO = False
    except ImportError:
        USING_ZONEINFO = None

DEFAULT_TIMEZONE = "Asia/Jakarta"

TIMEZONE_EXAMPLES: Dict[str, List[tuple]] = {
    "Asia": [
        ("Asia/Jakarta", "WIB - Indonesia Barat (UTC+7)"),
        ("Asia/Makassar", "WITA - Indonesia Tengah (UTC+8)"),
        ("Asia/Jayapura", "WIT - Indonesia Timur (UTC+9)"),
        ("Asia/Singapore", "Singapore (UTC+8)"),
        ("Asia/Kuala_Lumpur", "Malaysia (UTC+8)"),
        ("Asia/Bangkok", "Thailand (UTC+7)"),
        ("Asia/Ho_Chi_Minh", "Vietnam (UTC+7)"),
        ("Asia/Manila", "Philippines (UTC+8)"),
        ("Asia/Tokyo", "Japan (UTC+9)"),
        ("Asia/Seoul", "South Korea (UTC+9)"),
        ("Asia/Shanghai", "China (UTC+8)"),
        ("Asia/Hong_Kong", "Hong Kong (UTC+8)"),
        ("Asia/Kolkata", "India (UTC+5:30)"),
        ("Asia/Dubai", "UAE (UTC+4)"),
    ],
    "Europe": [
        ("Europe/London", "UK - GMT/BST (UTC+0/+1)"),
        ("Europe/Paris", "France (UTC+1/+2)"),
        ("Europe/Berlin", "Germany (UTC+1/+2)"),
        ("Europe/Amsterdam", "Netherlands (UTC+1/+2)"),
        ("Europe/Moscow", "Russia (UTC+3)"),
        ("Europe/Istanbul", "Turkey (UTC+3)"),
    ],
    "America": [
        ("America/New_York", "US Eastern (UTC-5/-4)"),
        ("America/Chicago", "US Central (UTC-6/-5)"),
        ("America/Los_Angeles", "US Pacific (UTC-8/-7)"),
        ("America/Sao_Paulo", "Brazil (UTC-3)"),
        ("America/Mexico_City", "Mexico (UTC-6/-5)"),
    ],
    "Australia": [
        ("Australia/Sydney", "Sydney (UTC+10/+11)"),
        ("Australia/Melbourne", "Melbourne (UTC+10/+11)"),
        ("Australia/Perth", "Perth (UTC+8)"),
    ],
    "Africa": [
        ("Africa/Cairo", "Egypt (UTC+2)"),
        ("Africa/Johannesburg", "South Africa (UTC+2)"),
        ("Africa/Lagos", "Nigeria (UTC+1)"),
    ],
    "Pacific": [
        ("Pacific/Auckland", "New Zealand (UTC+12/+13)"),
        ("Pacific/Honolulu", "Hawaii (UTC-10)"),
    ],
}


def get_timezone_object(timezone_str: str):
    if USING_ZONEINFO is True:
        try:
            return ZoneInfo(timezone_str)
        except:
            return ZoneInfo(DEFAULT_TIMEZONE)
    elif USING_ZONEINFO is False:
        try:
            return pytz.timezone(timezone_str)
        except:
            return pytz.timezone(DEFAULT_TIMEZONE)
    return None


def get_current_time(timezone_str: str = DEFAULT_TIMEZONE) -> str:
    tz = get_timezone_object(timezone_str)
    if tz is None:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S %Z")


def validate_timezone(timezone_str: str) -> bool:
    if USING_ZONEINFO is True:
        try:
            ZoneInfo(timezone_str)
            return True
        except:
            return False
    elif USING_ZONEINFO is False:
        try:
            pytz.timezone(timezone_str)
            return True
        except:
            return False
    return True


def get_timezone_examples_text() -> str:
    text = "🌍 TIMEZONE IANA EXAMPLES:\n\n"
    for continent, zones in TIMEZONE_EXAMPLES.items():
        text += f"[{continent}]\n"
        for tz, desc in zones[:4]:
            text += f"  {tz}\n    {desc}\n"
        text += "\n"
    text += "Format: Continent/City\n"
    text += "Contoh: Asia/Jakarta\n"
    text += "\nRef: wikipedia.org/wiki/List_of_tz_database_time_zones"
    return text


def get_timezone_by_continent(continent: str) -> str:
    key = continent.capitalize()
    if key not in TIMEZONE_EXAMPLES:
        return f"❌ Continent '{continent}' not found.\nAvailable: Asia, Europe, America, Australia, Africa, Pacific"
    text = f"🌍 TIMEZONE {key.upper()}:\n\n"
    for tz, desc in TIMEZONE_EXAMPLES[key]:
        text += f"{tz}\n  {desc}\n\n"
    return text


class TimezoneManager:
    def __init__(self, config_file: str = "timezone.conf"):
        self.config_file = config_file
        self.timezone = self._load_timezone()
    
    def _load_timezone(self) -> str:
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    tz = f.read().strip()
                    if validate_timezone(tz):
                        return tz
            except:
                pass
        return DEFAULT_TIMEZONE
    
    def save_timezone(self, timezone_str: str) -> bool:
        if not validate_timezone(timezone_str):
            return False
        try:
            with open(self.config_file, 'w') as f:
                f.write(timezone_str)
            self.timezone = timezone_str
            return True
        except:
            return False
    
    def get_current_time(self) -> str:
        return get_current_time(self.timezone)
    
    def get_timezone(self) -> str:
        return self.timezone


tz_manager = TimezoneManager()
