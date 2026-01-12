#!/usr/bin/env python3
"""
BotLinkMaster v4.2 - Database Module
SQLite database for storing device and interface information

Author: BotLinkMaster
Version: 4.2
"""

import sqlite3
import os
from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class Device:
    """Device data class"""
    id: Optional[int]
    name: str
    host: str
    username: str
    password: str
    protocol: str
    port: Optional[int]
    description: Optional[str]
    location: Optional[str]
    vendor: Optional[str]  # NEW: vendor field
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


@dataclass
class InterfaceCache:
    """Interface cache data class"""
    id: Optional[int]
    device_name: str
    interface_name: str
    status: Optional[str]
    protocol_status: Optional[str]
    description: Optional[str]
    rx_power: Optional[float]  # NEW: optical power
    tx_power: Optional[float]  # NEW: optical power
    cached_at: Optional[str] = None


class DatabaseManager:
    """Database manager for BotLinkMaster"""
    
    def __init__(self, db_path: str = "botlinkmaster.db"):
        """Initialize database connection"""
        self.db_path = db_path
        self.conn = None
        self._connect()
        self._create_tables()
        self._migrate_tables()  # Handle schema migrations
    
    def _connect(self):
        """Connect to database"""
        try:
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self.conn.row_factory = sqlite3.Row
            logger.info(f"Connected to database: {self.db_path}")
        except Exception as e:
            logger.error(f"Database connection error: {e}")
            raise
    
    def _create_tables(self):
        """Create database tables"""
        cursor = self.conn.cursor()
        
        # Devices table with vendor field
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
        
        # Interface cache table with optical power
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
        
        self.conn.commit()
        logger.info("Database tables created/verified")
    
    def _migrate_tables(self):
        """Migrate existing tables to add new columns"""
        cursor = self.conn.cursor()
        
        # Check if vendor column exists in devices table
        cursor.execute("PRAGMA table_info(devices)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'vendor' not in columns:
            try:
                cursor.execute("ALTER TABLE devices ADD COLUMN vendor TEXT DEFAULT 'generic'")
                self.conn.commit()
                logger.info("Added vendor column to devices table")
            except Exception as e:
                logger.warning(f"Migration warning: {e}")
        
        # Check interface_cache for rx_power, tx_power
        cursor.execute("PRAGMA table_info(interface_cache)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'rx_power' not in columns:
            try:
                cursor.execute("ALTER TABLE interface_cache ADD COLUMN rx_power REAL")
                cursor.execute("ALTER TABLE interface_cache ADD COLUMN tx_power REAL")
                self.conn.commit()
                logger.info("Added optical power columns to interface_cache table")
            except Exception as e:
                logger.warning(f"Migration warning: {e}")
    
    def add_device(self, name: str, host: str, username: str, password: str,
                   protocol: str = 'ssh', port: Optional[int] = None,
                   description: Optional[str] = None, location: Optional[str] = None,
                   vendor: Optional[str] = 'generic') -> Optional[Device]:
        """Add a new device"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO devices (name, host, username, password, protocol, port, description, location, vendor)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (name, host, username, password, protocol, port, description, location, vendor or 'generic'))
            self.conn.commit()
            
            logger.info(f"Device added: {name} (vendor: {vendor})")
            return self.get_device(name)
        except sqlite3.IntegrityError:
            logger.warning(f"Device already exists: {name}")
            return None
        except Exception as e:
            logger.error(f"Error adding device: {e}")
            return None
    
    def get_device(self, name: str) -> Optional[Device]:
        """Get device by name"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT * FROM devices WHERE name = ?', (name,))
            row = cursor.fetchone()
            
            if row:
                return Device(
                    id=row['id'],
                    name=row['name'],
                    host=row['host'],
                    username=row['username'],
                    password=row['password'],
                    protocol=row['protocol'],
                    port=row['port'],
                    description=row['description'],
                    location=row['location'],
                    vendor=row['vendor'] if 'vendor' in row.keys() else 'generic',
                    created_at=row['created_at'],
                    updated_at=row['updated_at']
                )
            return None
        except Exception as e:
            logger.error(f"Error getting device: {e}")
            return None
    
    def get_all_devices(self) -> List[Device]:
        """Get all devices"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT * FROM devices ORDER BY name')
            rows = cursor.fetchall()
            
            devices = []
            for row in rows:
                devices.append(Device(
                    id=row['id'],
                    name=row['name'],
                    host=row['host'],
                    username=row['username'],
                    password=row['password'],
                    protocol=row['protocol'],
                    port=row['port'],
                    description=row['description'],
                    location=row['location'],
                    vendor=row['vendor'] if 'vendor' in row.keys() else 'generic',
                    created_at=row['created_at'],
                    updated_at=row['updated_at']
                ))
            return devices
        except Exception as e:
            logger.error(f"Error getting devices: {e}")
            return []
    
    def update_device(self, name: str, **kwargs) -> bool:
        """Update device"""
        try:
            allowed_fields = ['host', 'username', 'password', 'protocol', 'port', 
                            'description', 'location', 'vendor']
            updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
            
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
            
            logger.info(f"Device updated: {name}")
            return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Error updating device: {e}")
            return False
    
    def delete_device(self, name: str) -> bool:
        """Delete device and its cached interfaces"""
        try:
            cursor = self.conn.cursor()
            
            # Delete cached interfaces
            cursor.execute('DELETE FROM interface_cache WHERE device_name = ?', (name,))
            
            # Delete device
            cursor.execute('DELETE FROM devices WHERE name = ?', (name,))
            self.conn.commit()
            
            logger.info(f"Device deleted: {name}")
            return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Error deleting device: {e}")
            return False
    
    def cache_interface(self, device_name: str, interface_name: str,
                       status: Optional[str] = None, protocol_status: Optional[str] = None,
                       description: Optional[str] = None,
                       rx_power: Optional[float] = None,
                       tx_power: Optional[float] = None) -> bool:
        """Cache interface information"""
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
        """Get cached interfaces for device"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT * FROM interface_cache WHERE device_name = ?
                ORDER BY interface_name
            ''', (device_name,))
            rows = cursor.fetchall()
            
            interfaces = []
            for row in rows:
                interfaces.append(InterfaceCache(
                    id=row['id'],
                    device_name=row['device_name'],
                    interface_name=row['interface_name'],
                    status=row['status'],
                    protocol_status=row['protocol_status'],
                    description=row['description'],
                    rx_power=row['rx_power'] if 'rx_power' in row.keys() else None,
                    tx_power=row['tx_power'] if 'tx_power' in row.keys() else None,
                    cached_at=row['cached_at']
                ))
            return interfaces
        except Exception as e:
            logger.error(f"Error getting interfaces: {e}")
            return []
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")


if __name__ == "__main__":
    # Test database
    db = DatabaseManager()
    print("Database initialized successfully")
    
    # Test add device
    device = db.add_device(
        name="test-router",
        host="192.168.1.1",
        username="admin",
        password="admin123",
        protocol="ssh",
        port=22,
        vendor="cisco_ios",
        description="Test router"
    )
    
    if device:
        print(f"Device added: {device.name}, vendor: {device.vendor}")
    
    # Get all devices
    devices = db.get_all_devices()
    print(f"Total devices: {len(devices)}")
    
    db.close()