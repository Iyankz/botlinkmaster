#!/usr/bin/env python3
"""
BotLinkMaster v4.0 - Database Module
SQLAlchemy ORM for device and interface cache management

Author: Yayang Ardiansyah
License: MIT
"""

from sqlalchemy import create_engine, Column, Integer, String, DateTime, Enum, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from datetime import datetime
from typing import List, Optional, Dict, Any
import logging
import os

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create base class for models
Base = declarative_base()


class Device(Base):
    """Device model for storing network device information"""
    __tablename__ = 'devices'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    host = Column(String(255), nullable=False)
    username = Column(String(100), nullable=False)
    password = Column(String(255), nullable=False)
    protocol = Column(Enum('ssh', 'telnet', name='protocol_types'), nullable=False, default='ssh')
    port = Column(Integer, nullable=True)
    description = Column(Text, nullable=True)
    location = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<Device(name='{self.name}', host='{self.host}', protocol='{self.protocol}')>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert device to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'host': self.host,
            'username': self.username,
            'protocol': self.protocol,
            'port': self.port,
            'description': self.description,
            'location': self.location,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class InterfaceCache(Base):
    """Cache for interface status to reduce device queries"""
    __tablename__ = 'interface_cache'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    device_name = Column(String(100), nullable=False, index=True)
    interface_name = Column(String(100), nullable=False)
    status = Column(String(50), nullable=True)
    protocol_status = Column(String(50), nullable=True)
    description = Column(Text, nullable=True)
    last_checked = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<InterfaceCache(device='{self.device_name}', interface='{self.interface_name}')>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert interface cache to dictionary"""
        return {
            'id': self.id,
            'device_name': self.device_name,
            'interface_name': self.interface_name,
            'status': self.status,
            'protocol_status': self.protocol_status,
            'description': self.description,
            'last_checked': self.last_checked.isoformat() if self.last_checked else None
        }


class DatabaseManager:
    """Database manager for handling all database operations"""
    
    def __init__(self, database_url: Optional[str] = None):
        """
        Initialize database manager
        
        Args:
            database_url: SQLAlchemy database URL
                         If None, uses DATABASE_URL env var or defaults to SQLite
        """
        if database_url is None:
            database_url = os.getenv('DATABASE_URL', 'sqlite:///botlinkmaster.db')
        
        logger.info(f"Initializing database: {database_url.split('://')[0]}://...")
        
        self.engine = create_engine(
            database_url,
            echo=False,
            pool_pre_ping=True  # Verify connections before using
        )
        
        # Create session factory
        session_factory = sessionmaker(bind=self.engine)
        self.Session = scoped_session(session_factory)
        
        # Create tables if they don't exist
        Base.metadata.create_all(self.engine)
        logger.info("Database initialized successfully")
    
    def get_session(self):
        """Get a new database session"""
        return self.Session()
    
    # Device operations
    
    def add_device(self, name: str, host: str, username: str, password: str,
                   protocol: str = 'ssh', port: Optional[int] = None,
                   description: Optional[str] = None, location: Optional[str] = None) -> Optional[Device]:
        """
        Add a new device to database
        
        Returns:
            Device object if successful, None otherwise
        """
        session = self.get_session()
        try:
            device = Device(
                name=name,
                host=host,
                username=username,
                password=password,
                protocol=protocol,
                port=port,
                description=description,
                location=location
            )
            session.add(device)
            session.commit()
            logger.info(f"Device '{name}' added successfully")
            return device
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to add device '{name}': {str(e)}")
            return None
        finally:
            session.close()
    
    def get_device(self, name: str) -> Optional[Device]:
        """Get device by name"""
        session = self.get_session()
        try:
            device = session.query(Device).filter_by(name=name).first()
            return device
        finally:
            session.close()
    
    def get_all_devices(self) -> List[Device]:
        """Get all devices"""
        session = self.get_session()
        try:
            devices = session.query(Device).order_by(Device.name).all()
            return devices
        finally:
            session.close()
    
    def update_device(self, name: str, **kwargs) -> bool:
        """
        Update device information
        
        Args:
            name: Device name
            **kwargs: Fields to update (host, username, password, etc.)
        
        Returns:
            bool: True if successful
        """
        session = self.get_session()
        try:
            device = session.query(Device).filter_by(name=name).first()
            if not device:
                logger.warning(f"Device '{name}' not found")
                return False
            
            for key, value in kwargs.items():
                if hasattr(device, key):
                    setattr(device, key, value)
            
            device.updated_at = datetime.utcnow()
            session.commit()
            logger.info(f"Device '{name}' updated successfully")
            return True
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to update device '{name}': {str(e)}")
            return False
        finally:
            session.close()
    
    def delete_device(self, name: str) -> bool:
        """
        Delete device from database
        
        Returns:
            bool: True if successful
        """
        session = self.get_session()
        try:
            device = session.query(Device).filter_by(name=name).first()
            if not device:
                logger.warning(f"Device '{name}' not found")
                return False
            
            # Also delete associated interface cache
            session.query(InterfaceCache).filter_by(device_name=name).delete()
            
            session.delete(device)
            session.commit()
            logger.info(f"Device '{name}' deleted successfully")
            return True
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to delete device '{name}': {str(e)}")
            return False
        finally:
            session.close()
    
    # Interface cache operations
    
    def cache_interface(self, device_name: str, interface_name: str,
                       status: Optional[str] = None, protocol_status: Optional[str] = None,
                       description: Optional[str] = None) -> bool:
        """
        Cache interface information
        
        Returns:
            bool: True if successful
        """
        session = self.get_session()
        try:
            # Check if already exists
            cache = session.query(InterfaceCache).filter_by(
                device_name=device_name,
                interface_name=interface_name
            ).first()
            
            if cache:
                # Update existing
                cache.status = status
                cache.protocol_status = protocol_status
                cache.description = description
                cache.last_checked = datetime.utcnow()
            else:
                # Create new
                cache = InterfaceCache(
                    device_name=device_name,
                    interface_name=interface_name,
                    status=status,
                    protocol_status=protocol_status,
                    description=description
                )
                session.add(cache)
            
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to cache interface: {str(e)}")
            return False
        finally:
            session.close()
    
    def get_cached_interface(self, device_name: str, interface_name: str) -> Optional[InterfaceCache]:
        """Get cached interface information"""
        session = self.get_session()
        try:
            cache = session.query(InterfaceCache).filter_by(
                device_name=device_name,
                interface_name=interface_name
            ).first()
            return cache
        finally:
            session.close()
    
    def get_device_interfaces(self, device_name: str) -> List[InterfaceCache]:
        """Get all cached interfaces for a device"""
        session = self.get_session()
        try:
            interfaces = session.query(InterfaceCache).filter_by(
                device_name=device_name
            ).order_by(InterfaceCache.interface_name).all()
            return interfaces
        finally:
            session.close()
    
    def clear_device_cache(self, device_name: str) -> bool:
        """Clear all cached interfaces for a device"""
        session = self.get_session()
        try:
            session.query(InterfaceCache).filter_by(device_name=device_name).delete()
            session.commit()
            logger.info(f"Cache cleared for device '{device_name}'")
            return True
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to clear cache: {str(e)}")
            return False
        finally:
            session.close()
    
    def get_statistics(self) -> Dict[str, int]:
        """Get database statistics"""
        session = self.get_session()
        try:
            stats = {
                'total_devices': session.query(Device).count(),
                'total_cached_interfaces': session.query(InterfaceCache).count()
            }
            return stats
        finally:
            session.close()


# Example usage
if __name__ == "__main__":
    # Initialize database
    db = DatabaseManager()
    
    # Add test device
    device = db.add_device(
        name="test-router",
        host="192.168.1.1",
        username="admin",
        password="password",
        protocol="ssh",
        description="Test router"
    )
    
    if device:
        print(f"Added device: {device.name}")
        
        # Cache interface
        db.cache_interface(
            device_name="test-router",
            interface_name="GigabitEthernet0/0",
            status="up",
            protocol_status="up",
            description="WAN Interface"
        )
        
        # Get device
        device = db.get_device("test-router")
        if device:
            print(f"Device: {device.to_dict()}")
        
        # Get statistics
        stats = db.get_statistics()
        print(f"Statistics: {stats}")
