#!/usr/bin/env python3
"""
BotLinkMaster v4.2 - Network Device Connection Module
SSH/Telnet connection with multi-vendor optical power support

Author: BotLinkMaster
Version: 4.2
"""

import paramiko
import telnetlib
import socket
import time
import re
import logging
from enum import Enum
from dataclasses import dataclass
from typing import Optional, List, Dict, Any

from vendor_commands import (
    get_vendor_config,
    OpticalParser,
    expand_interface_name,
    get_optical_commands,
    Vendor
)

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
    vendor: str = "generic"
    
    def __post_init__(self):
        if self.port is None:
            self.port = 22 if self.protocol == Protocol.SSH else 23


class BotLinkMaster:
    """Main class for network device connections"""
    
    def __init__(self, config: ConnectionConfig):
        self.config = config
        self.client = None
        self.shell = None
        self.connected = False
        self.vendor_config = get_vendor_config(config.vendor)
        self.optical_parser = OpticalParser(config.vendor)
        
    def connect(self) -> bool:
        """Connect to device"""
        try:
            if self.config.protocol == Protocol.SSH:
                return self._connect_ssh()
            elif self.config.protocol == Protocol.TELNET:
                return self._connect_telnet()
            return False
        except Exception as e:
            logger.error(f"Connection failed: {str(e)}")
            return False
    
    def _connect_ssh(self) -> bool:
        """Connect via SSH"""
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
            time.sleep(1)
            self.shell.recv(65535)
            
            # Disable paging
            if self.vendor_config.disable_paging:
                self._execute_ssh(self.vendor_config.disable_paging, 1)
            
            self.connected = True
            logger.info(f"SSH connected to {self.config.host}")
            return True
            
        except paramiko.AuthenticationException:
            logger.error(f"Auth failed for {self.config.host}")
            return False
        except Exception as e:
            logger.error(f"SSH error: {str(e)}")
            return False
    
    def _connect_telnet(self) -> bool:
        """Connect via Telnet"""
        try:
            logger.info(f"Connecting to {self.config.host}:{self.config.port} via Telnet...")
            
            self.client = telnetlib.Telnet(
                self.config.host,
                self.config.port,
                timeout=self.config.timeout
            )
            
            # Login
            self.client.read_until(b":", timeout=10)
            self.client.write(self.config.username.encode('ascii') + b"\n")
            self.client.read_until(b":", timeout=10)
            self.client.write(self.config.password.encode('ascii') + b"\n")
            
            time.sleep(2)
            
            # Disable paging
            if self.vendor_config.disable_paging:
                self._execute_telnet(self.vendor_config.disable_paging, 1)
            
            self.connected = True
            logger.info(f"Telnet connected to {self.config.host}")
            return True
            
        except Exception as e:
            logger.error(f"Telnet error: {str(e)}")
            return False
    
    def execute_command(self, command: str, wait_time: float = 2.0) -> str:
        """Execute command on device"""
        if not self.connected:
            logger.error("Not connected")
            return ""
        
        try:
            if self.config.protocol == Protocol.SSH:
                return self._execute_ssh(command, wait_time)
            elif self.config.protocol == Protocol.TELNET:
                return self._execute_telnet(command, wait_time)
            return ""
        except Exception as e:
            logger.error(f"Command error: {str(e)}")
            return ""
    
    def _execute_ssh(self, command: str, wait_time: float) -> str:
        """Execute SSH command"""
        try:
            self.shell.send(command + "\n")
            time.sleep(wait_time)
            
            output = ""
            while self.shell.recv_ready():
                output += self.shell.recv(65535).decode('utf-8', errors='ignore')
                time.sleep(0.5)
            
            return output
        except Exception as e:
            logger.error(f"SSH exec error: {str(e)}")
            return ""
    
    def _execute_telnet(self, command: str, wait_time: float) -> str:
        """Execute Telnet command"""
        try:
            self.client.write(command.encode('ascii') + b"\n")
            time.sleep(wait_time)
            output = self.client.read_very_eager().decode('utf-8', errors='ignore')
            return output
        except Exception as e:
            logger.error(f"Telnet exec error: {str(e)}")
            return ""
    
    def get_specific_interface(self, interface_name: str) -> Optional[Dict[str, Any]]:
        """Get interface details"""
        full_interface = expand_interface_name(interface_name)
        
        command = self.vendor_config.show_interface.format(interface=full_interface)
        output = self.execute_command(command)
        
        if not output or "Invalid" in output or "Error" in output:
            command = self.vendor_config.show_interface.format(interface=interface_name)
            output = self.execute_command(command)
            
            if not output or "Invalid" in output:
                return None
        
        interface_info = {
            'name': interface_name,
            'full_output': output,
            'status': 'unknown'
        }
        
        # Extract status
        status_match = re.search(self.vendor_config.status_pattern, output, re.IGNORECASE)
        if status_match:
            interface_info['status'] = status_match.group(1)
        
        # Description
        desc_match = re.search(r'[Dd]escription[:\s]+(.+)', output)
        if desc_match:
            interface_info['description'] = desc_match.group(1).strip()
        
        return interface_info
    
    def get_optical_power(self, interface_name: str) -> Dict[str, Any]:
        """
        Get optical power for interface - MAIN FUNCTION FOR REDAMAN
        Tries multiple commands until one works
        """
        full_interface = expand_interface_name(interface_name)
        
        # Get all possible commands for this vendor
        commands = get_optical_commands(self.config.vendor, full_interface)
        
        all_output = ""
        result = None
        
        # Try each command
        for cmd in commands:
            logger.info(f"Trying optical command: {cmd}")
            output = self.execute_command(cmd, wait_time=3.0)
            
            if output and "Invalid" not in output and "Error" not in output and "%" not in output:
                all_output += f"\n--- Command: {cmd} ---\n{output}\n"
                
                # Parse the output
                parsed = self.optical_parser.parse_optical_power(output)
                
                if parsed['found']:
                    result = parsed
                    result['command_used'] = cmd
                    logger.info(f"Found optical data with: {cmd}")
                    break
        
        # If no result from specific commands, try the generic patterns
        if not result or not result.get('found'):
            result = self.optical_parser.parse_optical_power(all_output)
            result['command_used'] = 'multiple'
        
        result['interface'] = interface_name
        result['all_output'] = all_output
        
        return result
    
    def check_interface_with_optical(self, interface_name: str) -> Dict[str, Any]:
        """Get complete interface info including optical power"""
        
        # Get basic interface info
        interface_info = self.get_specific_interface(interface_name) or {}
        
        # Get optical power
        optical_info = self.get_optical_power(interface_name)
        
        # Merge
        result = {
            'name': interface_name,
            'status': interface_info.get('status', 'unknown'),
            'description': interface_info.get('description', ''),
            'rx_power': optical_info.get('rx_power'),
            'tx_power': optical_info.get('tx_power'),
            'rx_power_dbm': optical_info.get('rx_power_dbm', 'N/A'),
            'tx_power_dbm': optical_info.get('tx_power_dbm', 'N/A'),
            'temperature': optical_info.get('temperature'),
            'optical_status': optical_info.get('signal_status', 'unknown'),
            'command_used': optical_info.get('command_used', 'unknown'),
            'raw_output': optical_info.get('all_output', ''),
            'found': optical_info.get('found', False),
        }
        
        return result
    
    def disconnect(self):
        """Close connection"""
        try:
            if self.client:
                if self.config.protocol == Protocol.SSH:
                    self.client.close()
                elif self.config.protocol == Protocol.TELNET:
                    self.client.close()
                self.connected = False
                logger.info(f"Disconnected from {self.config.host}")
        except Exception as e:
            logger.error(f"Disconnect error: {str(e)}")
    
    def __enter__(self):
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()


if __name__ == "__main__":
    # Test example
    print("BotLinkMaster v4.2 - Multi-vendor optical power support")
    print("Use with telegram_bot.py for Telegram integration")