#!/usr/bin/env python3
"""
BotLinkMaster v4.0 - SSH/Telnet Connection Module
Handles connections to network devices via SSH or Telnet

Author: Yayang Ardiansyah
License: MIT
"""

import paramiko
import telnetlib
import socket
import time
import re
from enum import Enum
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class Protocol(Enum):
    """Supported connection protocols"""
    SSH = "ssh"
    TELNET = "telnet"


@dataclass
class ConnectionConfig:
    """Configuration for device connection"""
    host: str
    username: str
    password: str
    protocol: Protocol = Protocol.SSH
    port: Optional[int] = None
    timeout: int = 30
    
    def __post_init__(self):
        """Set default ports if not specified"""
        if self.port is None:
            self.port = 22 if self.protocol == Protocol.SSH else 23


class BotLinkMaster:
    """Main class for connecting to network devices"""
    
    def __init__(self, config: ConnectionConfig):
        """
        Initialize connection handler
        
        Args:
            config: ConnectionConfig object with connection details
        """
        self.config = config
        self.client = None
        self.shell = None
        self.connected = False
        
    def connect(self) -> bool:
        """
        Connect to device using configured protocol
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            if self.config.protocol == Protocol.SSH:
                return self._connect_ssh()
            elif self.config.protocol == Protocol.TELNET:
                return self._connect_telnet()
            else:
                logger.error(f"Unsupported protocol: {self.config.protocol}")
                return False
        except Exception as e:
            logger.error(f"Connection failed: {str(e)}")
            return False
    
    def _connect_ssh(self) -> bool:
        """
        Connect via SSH using Paramiko
        
        Returns:
            bool: True if successful
        """
        try:
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            logger.info(f"Connecting to {self.config.host}:{self.config.port} via SSH...")
            
            self.client.connect(
                hostname=self.config.host,
                port=self.config.port,
                username=self.config.username,
                password=self.config.password,
                timeout=self.config.timeout,
                look_for_keys=False,
                allow_agent=False
            )
            
            self.shell = self.client.invoke_shell()
            time.sleep(1)  # Wait for shell to be ready
            self.shell.recv(65535)  # Clear initial output
            
            self.connected = True
            logger.info(f"SSH connection established to {self.config.host}")
            return True
            
        except paramiko.AuthenticationException:
            logger.error(f"Authentication failed for {self.config.host}")
            return False
        except paramiko.SSHException as e:
            logger.error(f"SSH error: {str(e)}")
            return False
        except socket.error as e:
            logger.error(f"Socket error: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return False
    
    def _connect_telnet(self) -> bool:
        """
        Connect via Telnet
        
        Returns:
            bool: True if successful
        """
        try:
            logger.info(f"Connecting to {self.config.host}:{self.config.port} via Telnet...")
            
            self.client = telnetlib.Telnet(
                self.config.host,
                self.config.port,
                timeout=self.config.timeout
            )
            
            # Wait for login prompt
            self.client.read_until(b"login: ", timeout=5)
            self.client.write(self.config.username.encode('ascii') + b"\n")
            
            # Wait for password prompt
            self.client.read_until(b"Password: ", timeout=5)
            self.client.write(self.config.password.encode('ascii') + b"\n")
            
            time.sleep(1)
            self.connected = True
            logger.info(f"Telnet connection established to {self.config.host}")
            return True
            
        except socket.timeout:
            logger.error(f"Connection timeout to {self.config.host}")
            return False
        except Exception as e:
            logger.error(f"Telnet error: {str(e)}")
            return False
    
    def execute_command(self, command: str, wait_time: float = 2.0) -> str:
        """
        Execute command on device
        
        Args:
            command: Command to execute
            wait_time: Time to wait for output (seconds)
        
        Returns:
            str: Command output
        """
        if not self.connected:
            logger.error("Not connected to device")
            return ""
        
        try:
            if self.config.protocol == Protocol.SSH:
                return self._execute_ssh(command, wait_time)
            elif self.config.protocol == Protocol.TELNET:
                return self._execute_telnet(command, wait_time)
            else:
                return ""
        except Exception as e:
            logger.error(f"Command execution failed: {str(e)}")
            return ""
    
    def _execute_ssh(self, command: str, wait_time: float) -> str:
        """Execute command via SSH"""
        try:
            self.shell.send(command + "\n")
            time.sleep(wait_time)
            
            output = ""
            while self.shell.recv_ready():
                output += self.shell.recv(65535).decode('utf-8', errors='ignore')
            
            return output
            
        except Exception as e:
            logger.error(f"SSH command execution error: {str(e)}")
            return ""
    
    def _execute_telnet(self, command: str, wait_time: float) -> str:
        """Execute command via Telnet"""
        try:
            self.client.write(command.encode('ascii') + b"\n")
            time.sleep(wait_time)
            
            output = self.client.read_very_eager().decode('utf-8', errors='ignore')
            return output
            
        except Exception as e:
            logger.error(f"Telnet command execution error: {str(e)}")
            return ""
    
    def get_interfaces(self) -> List[Dict[str, Any]]:
        """
        Get list of interfaces from device
        
        Returns:
            List of interface dictionaries with name, status, description
        """
        command = "show interfaces description"
        output = self.execute_command(command)
        
        if not output:
            return []
        
        interfaces = []
        lines = output.split('\n')
        
        # Parse interface information
        # This is a generic parser - may need adjustment for specific vendors
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#') or 'Interface' in line:
                continue
            
            # Try to parse interface line
            # Format: Interface Status Protocol Description
            match = re.match(r'(\S+)\s+(\S+)\s+(\S+)\s*(.*)', line)
            if match:
                interface = {
                    'name': match.group(1),
                    'status': match.group(2),
                    'protocol': match.group(3),
                    'description': match.group(4).strip() if match.group(4) else ''
                }
                interfaces.append(interface)
        
        logger.info(f"Found {len(interfaces)} interfaces")
        return interfaces
    
    def get_specific_interface(self, interface_name: str) -> Optional[Dict[str, Any]]:
        """
        Get details for a specific interface
        
        Args:
            interface_name: Name of the interface (e.g., "GigabitEthernet0/0")
        
        Returns:
            Dictionary with interface details or None if not found
        """
        command = f"show interface {interface_name}"
        output = self.execute_command(command)
        
        if not output or "Invalid" in output:
            logger.warning(f"Interface {interface_name} not found or command invalid")
            return None
        
        # Parse interface details
        interface_info = {
            'name': interface_name,
            'full_output': output
        }
        
        # Extract status
        status_match = re.search(r'line protocol is (\w+)', output, re.IGNORECASE)
        if status_match:
            interface_info['status'] = status_match.group(1)
        
        # Extract description
        desc_match = re.search(r'Description:\s*(.+)', output)
        if desc_match:
            interface_info['description'] = desc_match.group(1).strip()
        
        # Extract IP address
        ip_match = re.search(r'Internet address is (\S+)', output)
        if ip_match:
            interface_info['ip_address'] = ip_match.group(1)
        
        # Extract MAC address
        mac_match = re.search(r'address is (\S+:\S+:\S+:\S+:\S+:\S+)', output, re.IGNORECASE)
        if mac_match:
            interface_info['mac_address'] = mac_match.group(1)
        
        return interface_info
    
    def disconnect(self):
        """Close connection to device"""
        try:
            if self.client:
                if self.config.protocol == Protocol.SSH:
                    self.client.close()
                elif self.config.protocol == Protocol.TELNET:
                    self.client.close()
                
                self.connected = False
                logger.info(f"Disconnected from {self.config.host}")
        except Exception as e:
            logger.error(f"Error during disconnect: {str(e)}")
    
    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()


# Example usage
if __name__ == "__main__":
    # Example SSH connection
    config = ConnectionConfig(
        host="192.168.1.1",
        username="admin",
        password="password",
        protocol=Protocol.SSH,
        port=22
    )
    
    with BotLinkMaster(config) as device:
        if device.connected:
            # Get all interfaces
            interfaces = device.get_interfaces()
            print(f"Found {len(interfaces)} interfaces")
            
            # Get specific interface
            if interfaces:
                first_int = interfaces[0]['name']
                details = device.get_specific_interface(first_int)
                if details:
                    print(f"Interface {first_int}: {details.get('status', 'unknown')}")
