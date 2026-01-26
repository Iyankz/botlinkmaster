#!/usr/bin/env python3
"""
BotLinkMaster v4.8.8 - Database Module
SQLite database with support for multiple devices per IP (port forwarding)

Author: BotLinkMaster
Version: 4.8.7
"""

import sqlite3
import logging
from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class Device:
    id: Optional[int]
    name: str
    host: str
    username: str
    password: str
    protocol: str
    port: Optional[int]
    description: Optional[str]
    location: Optional[str]
    vendor: Optional[str]
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


@dataclass
class InterfaceCache:
    id: Optional[int]
    device_name: str
    interface_name: str
    status: Optional[str]
    protocol_status: Optional[str]
    description: Optional[str]
    rx_power: Optional[float]
    tx_power: Optional[float]
    cached_at: Optional[str] = None


class DatabaseManager:
    def __init__(self, db_path: str = "botlinkmaster.db"):
        self.db_path = db_path
        self.conn = None
        self._connect()
        self._create_tables()
        self._migrate_tables()
    
    def _connect(self):
        try:
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self.conn.row_factory = sqlite3.Row
            logger.info(f"Connected to database: {self.db_path}")
        except Exception as e:
            logger.error(f"Database connection error: {e}")
            raise
    
    def _create_tables(self):
        cursor = self.conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS devices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                host TEXT NOT NULL,
                username TEXT NOT NULL,
                password TEXT NOT NULL,
                protocol TEXT DEFAULT 'ssh',
                port INTEGER,
                description TEXT,
                location TEXT,
                vendor TEXT DEFAULT 'generic',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS interface_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_name TEXT NOT NULL,
                interface_name TEXT NOT NULL,
                status TEXT,
                protocol_status TEXT,
                description TEXT,
                rx_power REAL,
                tx_power REAL,
                cached_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(device_name, interface_name)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS allowed_users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER UNIQUE NOT NULL,
                username TEXT,
                is_admin INTEGER DEFAULT 0,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.conn.commit()
    
    def _migrate_tables(self):
        cursor = self.conn.cursor()
        
        cursor.execute("PRAGMA table_info(devices)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'vendor' not in columns:
            try:
                cursor.execute("ALTER TABLE devices ADD COLUMN vendor TEXT DEFAULT 'generic'")
                self.conn.commit()
            except:
                pass
        
        cursor.execute("PRAGMA table_info(interface_cache)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'rx_power' not in columns:
            try:
                cursor.execute("ALTER TABLE interface_cache ADD COLUMN rx_power REAL")
                cursor.execute("ALTER TABLE interface_cache ADD COLUMN tx_power REAL")
                self.conn.commit()
            except:
                pass
    
    def add_device(self, name: str, host: str, username: str, password: str,
                   protocol: str = 'ssh', port: Optional[int] = None,
                   description: Optional[str] = None, location: Optional[str] = None,
                   vendor: Optional[str] = 'generic') -> Optional[Device]:
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO devices (name, host, username, password, protocol, port, description, location, vendor)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (name, host, username, password, protocol, port, description, location, vendor or 'generic'))
            self.conn.commit()
            return self.get_device(name)
        except sqlite3.IntegrityError:
            logger.warning(f"Device already exists: {name}")
            return None
        except Exception as e:
            logger.error(f"Error adding device: {e}")
            return None
    
    def get_device(self, name: str) -> Optional[Device]:
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT * FROM devices WHERE name = ?', (name,))
            row = cursor.fetchone()
            if row:
                return Device(
                    id=row['id'], name=row['name'], host=row['host'],
                    username=row['username'], password=row['password'],
                    protocol=row['protocol'], port=row['port'],
                    description=row['description'], location=row['location'],
                    vendor=row['vendor'] if 'vendor' in row.keys() else 'generic',
                    created_at=row['created_at'], updated_at=row['updated_at']
                )
            return None
        except Exception as e:
            logger.error(f"Error getting device: {e}")
            return None
    
    def get_all_devices(self) -> List[Device]:
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT * FROM devices ORDER BY name')
            rows = cursor.fetchall()
            return [Device(
                id=r['id'], name=r['name'], host=r['host'],
                username=r['username'], password=r['password'],
                protocol=r['protocol'], port=r['port'],
                description=r['description'], location=r['location'],
                vendor=r['vendor'] if 'vendor' in r.keys() else 'generic',
                created_at=r['created_at'], updated_at=r['updated_at']
            ) for r in rows]
        except Exception as e:
            logger.error(f"Error getting devices: {e}")
            return []
    
    def update_device(self, name: str, **kwargs) -> bool:
        try:
            allowed = ['host', 'username', 'password', 'protocol', 'port', 
                      'description', 'location', 'vendor']
            updates = {k: v for k, v in kwargs.items() if k in allowed}
            if not updates:
                return False
            
            set_clause = ', '.join([f"{k} = ?" for k in updates.keys()])
            values = list(updates.values()) + [name]
            
            cursor = self.conn.cursor()
            cursor.execute(f'''
                UPDATE devices SET {set_clause}, updated_at = CURRENT_TIMESTAMP
                WHERE name = ?
            ''', values)
            self.conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Error updating device: {e}")
            return False
    
    def delete_device(self, name: str) -> bool:
        try:
            cursor = self.conn.cursor()
            cursor.execute('DELETE FROM interface_cache WHERE device_name = ?', (name,))
            cursor.execute('DELETE FROM devices WHERE name = ?', (name,))
            self.conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Error deleting device: {e}")
            return False
    
    def cache_interface(self, device_name: str, interface_name: str,
                       status: Optional[str] = None, protocol_status: Optional[str] = None,
                       description: Optional[str] = None,
                       rx_power: Optional[float] = None,
                       tx_power: Optional[float] = None) -> bool:
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO interface_cache 
                (device_name, interface_name, status, protocol_status, description, rx_power, tx_power, cached_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (device_name, interface_name, status, protocol_status, description, rx_power, tx_power))
            self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error caching interface: {e}")
            return False
    
    def get_device_interfaces(self, device_name: str) -> List[InterfaceCache]:
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT * FROM interface_cache WHERE device_name = ?
                ORDER BY interface_name
            ''', (device_name,))
            rows = cursor.fetchall()
            return [InterfaceCache(
                id=r['id'], device_name=r['device_name'],
                interface_name=r['interface_name'], status=r['status'],
                protocol_status=r['protocol_status'], description=r['description'],
                rx_power=r['rx_power'] if 'rx_power' in r.keys() else None,
                tx_power=r['tx_power'] if 'tx_power' in r.keys() else None,
                cached_at=r['cached_at']
            ) for r in rows]
        except Exception as e:
            logger.error(f"Error getting interfaces: {e}")
            return []
    
    def get_setting(self, key: str, default: str = '') -> str:
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT value FROM settings WHERE key = ?', (key,))
            row = cursor.fetchone()
            return row['value'] if row else default
        except:
            return default
    
    def set_setting(self, key: str, value: str) -> bool:
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO settings (key, value, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
            ''', (key, value))
            self.conn.commit()
            return True
        except:
            return False
    
    def add_allowed_user(self, chat_id: int, username: str = None, is_admin: bool = False) -> bool:
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO allowed_users (chat_id, username, is_admin)
                VALUES (?, ?, ?)
            ''', (chat_id, username, 1 if is_admin else 0))
            self.conn.commit()
            return True
        except:
            return False
    
    def remove_allowed_user(self, chat_id: int) -> bool:
        try:
            cursor = self.conn.cursor()
            cursor.execute('DELETE FROM allowed_users WHERE chat_id = ?', (chat_id,))
            self.conn.commit()
            return cursor.rowcount > 0
        except:
            return False
    
    def get_allowed_users(self) -> List[dict]:
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT * FROM allowed_users')
            return [dict(r) for r in cursor.fetchall()]
        except:
            return []
    
    def is_user_allowed(self, chat_id: int) -> bool:
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT 1 FROM allowed_users WHERE chat_id = ?', (chat_id,))
            return cursor.fetchone() is not None
        except:
            return False
    
    def close(self):
        if self.conn:
            self.conn.close()
