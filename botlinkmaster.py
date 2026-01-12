#!/usr/bin/env python3
"""
BotLinkMaster v4.5.1 - Network Device Connection Module
SSH/Telnet with multi-vendor support and improved Huawei optical parsing

Author: BotLinkMaster
Version: 4.5.1
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
    get_vendor_config, OpticalParser, expand_interface_name, get_optical_commands
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class Protocol(Enum):
    SSH = "ssh"
    TELNET = "telnet"


@dataclass
class ConnectionConfig:
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
        """Connect via SSH with legacy algorithm support for Huawei"""
        try:
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            logger.info(f"Connecting to {self.config.host}:{self.config.port} via SSH...")
            
            # Transport for legacy key exchange (Huawei fix)
            transport = paramiko.Transport((self.config.host, self.config.port))
            transport.set_keepalive(30)
            
            # Enable legacy algorithms for older devices (Huawei, ZTE, etc.)
            transport._preferred_keys = [
                'ssh-rsa', 'rsa-sha2-256', 'rsa-sha2-512',
                'ssh-dss', 'ecdsa-sha2-nistp256', 'ssh-ed25519'
            ]
            transport._preferred_kex = [
                'diffie-hellman-group14-sha1',
                'diffie-hellman-group1-sha1',
                'diffie-hellman-group-exchange-sha1',
                'diffie-hellman-group-exchange-sha256',
                'ecdh-sha2-nistp256',
                'ecdh-sha2-nistp384',
                'ecdh-sha2-nistp521',
            ]
            transport._preferred_ciphers = [
                'aes128-ctr', 'aes192-ctr', 'aes256-ctr',
                'aes128-cbc', 'aes192-cbc', 'aes256-cbc',
                '3des-cbc', 'blowfish-cbc',
            ]
            
            try:
                transport.connect(
                    username=self.config.username,
                    password=self.config.password,
                )
            except paramiko.SSHException as e:
                logger.warning(f"Transport connect failed, trying standard: {e}")
                transport.close()
                # Fallback to standard connection
                self.client.connect(
                    hostname=self.config.host,
                    port=self.config.port,
                    username=self.config.username,
                    password=self.config.password,
                    timeout=self.config.timeout,
                    look_for_keys=False,
                    allow_agent=False,
                    disabled_algorithms={
                        'pubkeys': ['rsa-sha2-256', 'rsa-sha2-512']
                    }
                )
                self.shell = self.client.invoke_shell()
            else:
                self.client._transport = transport
                self.shell = transport.open_session()
                self.shell.get_pty()
                self.shell.invoke_shell()
            
            time.sleep(1)
            # Clear initial buffer
            if self.shell.recv_ready():
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
            # Try alternative connection method
            return self._connect_ssh_alternative()
    
    def _connect_ssh_alternative(self) -> bool:
        """Alternative SSH connection for problematic devices"""
        try:
            logger.info("Trying alternative SSH connection...")
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            self.client.connect(
                hostname=self.config.host,
                port=self.config.port,
                username=self.config.username,
                password=self.config.password,
                timeout=self.config.timeout,
                look_for_keys=False,
                allow_agent=False,
            )
            
            self.shell = self.client.invoke_shell()
            time.sleep(1)
            self.shell.recv(65535)
            
            if self.vendor_config.disable_paging:
                self._execute_ssh(self.vendor_config.disable_paging, 1)
            
            self.connected = True
            logger.info(f"Alternative SSH connected to {self.config.host}")
            return True
        except Exception as e:
            logger.error(f"Alternative SSH failed: {str(e)}")
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
            
            # Wait for login prompt
            output = self.client.read_until(b":", timeout=10).decode('utf-8', errors='ignore')
            if 'name' in output.lower() or 'login' in output.lower() or 'user' in output.lower():
                self.client.write(self.config.username.encode('ascii') + b"\n")
            
            # Wait for password prompt
            output = self.client.read_until(b":", timeout=10).decode('utf-8', errors='ignore')
            if 'pass' in output.lower() or 'word' in output.lower():
                self.client.write(self.config.password.encode('ascii') + b"\n")
            
            time.sleep(2)
            self.client.read_very_eager()
            
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
        if not self.connected:
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
        try:
            self.shell.send(command + "\n")
            time.sleep(wait_time)
            
            output = ""
            timeout = time.time() + 15  # 15 second timeout
            while time.time() < timeout:
                if self.shell.recv_ready():
                    chunk = self.shell.recv(65535).decode('utf-8', errors='ignore')
                    output += chunk
                    time.sleep(0.3)
                else:
                    if output:
                        break
                    time.sleep(0.5)
            
            return output
        except Exception as e:
            logger.error(f"SSH exec error: {str(e)}")
            return ""
    
    def _execute_telnet(self, command: str, wait_time: float) -> str:
        try:
            self.client.write(command.encode('ascii') + b"\n")
            time.sleep(wait_time)
            output = self.client.read_very_eager().decode('utf-8', errors='ignore')
            return output
        except Exception as e:
            logger.error(f"Telnet exec error: {str(e)}")
            return ""
    
    def get_interfaces(self) -> List[Dict[str, Any]]:
        """Get all interfaces with status and description"""
        interfaces = []
        
        # Try description command first
        cmd = self.vendor_config.show_interface_description
        output = self.execute_command(cmd, wait_time=3.0)
        
        if not output or 'Invalid' in output or 'Error' in output:
            cmd = self.vendor_config.show_interface_brief
            output = self.execute_command(cmd, wait_time=3.0)
        
        if not output:
            return interfaces
        
        # Parse output
        lines = output.split('\n')
        for line in lines:
            line = line.strip()
            if not line or '---' in line:
                continue
            
            # Skip header lines
            lower_line = line.lower()
            if any(h in lower_line for h in ['interface', 'port', 'status', 'protocol', '====', '----']):
                if not any(c.isdigit() for c in line[:20]):
                    continue
            
            parts = line.split()
            if len(parts) >= 1:
                iface_name = parts[0]
                
                # Skip if not interface-like
                if not any(c.isdigit() for c in iface_name):
                    continue
                
                interface = {
                    'name': iface_name,
                    'status': 'unknown',
                    'description': '',
                }
                
                # Determine status from line
                line_lower = line.lower()
                if ' up ' in line_lower or line_lower.endswith(' up') or '*up' in line_lower:
                    interface['status'] = 'up'
                elif ' down ' in line_lower or line_lower.endswith(' down') or '*down' in line_lower:
                    interface['status'] = 'down'
                elif 'up' in line_lower and 'down' not in line_lower:
                    interface['status'] = 'up'
                elif 'down' in line_lower:
                    interface['status'] = 'down'
                
                # Try to get description
                if len(parts) >= 3:
                    # Find description - usually after status columns
                    desc_start = 2
                    for i, part in enumerate(parts):
                        if part.lower() in ['up', 'down', '*up', '*down', 'up(s)', 'down(s)']:
                            desc_start = i + 1
                            break
                    if desc_start < len(parts):
                        interface['description'] = ' '.join(parts[desc_start:])
                
                interfaces.append(interface)
        
        return interfaces
    
    def get_interface_status(self, interface_name: str) -> Dict[str, Any]:
        """Get detailed interface status"""
        full_interface = expand_interface_name(interface_name)
        
        cmd = self.vendor_config.show_interface.format(interface=full_interface)
        output = self.execute_command(cmd, wait_time=3.0)
        
        if not output or 'Invalid' in output or 'Error' in output:
            cmd = self.vendor_config.show_interface.format(interface=interface_name)
            output = self.execute_command(cmd, wait_time=3.0)
        
        result = {
            'name': interface_name,
            'status': self.optical_parser.parse_interface_status(output),
            'description': self.optical_parser.parse_description(output),
            'raw_output': output,
        }
        
        return result
    
    def get_optical_power(self, interface_name: str) -> Dict[str, Any]:
        """Get optical power for interface with multiple command attempts"""
        full_interface = expand_interface_name(interface_name)
        
        # Get all possible optical commands
        commands = get_optical_commands(self.config.vendor, full_interface)
        
        # Also try with original interface name
        if full_interface != interface_name:
            commands.extend(get_optical_commands(self.config.vendor, interface_name))
        
        all_output = ""
        result = None
        successful_cmd = None
        
        for cmd in commands:
            logger.info(f"Trying optical command: {cmd}")
            output = self.execute_command(cmd, wait_time=3.0)
            
            if output:
                # Skip if error messages
                if any(err in output for err in ['Invalid', 'Error', 'Unrecognized', '%']):
                    continue
                
                all_output += f"\n--- {cmd} ---\n{output}\n"
                parsed = self.optical_parser.parse_optical_power(output)
                
                if parsed['found']:
                    result = parsed
                    successful_cmd = cmd
                    logger.info(f"Found optical data with command: {cmd}")
                    break
        
        # If not found with vendor commands, try parsing all output
        if not result or not result.get('found'):
            result = self.optical_parser.parse_optical_power(all_output)
            if result.get('found'):
                successful_cmd = 'combined'
            else:
                successful_cmd = 'multiple'
        
        result['interface'] = interface_name
        result['all_output'] = all_output
        result['command_used'] = successful_cmd or 'none'
        
        return result
    
    def check_interface_with_optical(self, interface_name: str) -> Dict[str, Any]:
        """Get complete interface info including optical power"""
        interface_info = self.get_interface_status(interface_name)
        optical_info = self.get_optical_power(interface_name)
        
        return {
            'name': interface_name,
            'status': interface_info.get('status', 'unknown'),
            'description': interface_info.get('description', ''),
            'rx_power': optical_info.get('rx_power'),
            'tx_power': optical_info.get('tx_power'),
            'rx_power_dbm': optical_info.get('rx_power_dbm', 'N/A'),
            'tx_power_dbm': optical_info.get('tx_power_dbm', 'N/A'),
            'attenuation': optical_info.get('attenuation'),
            'attenuation_db': optical_info.get('attenuation_db', 'N/A'),
            'optical_status': optical_info.get('signal_status', 'unknown'),
            'command_used': optical_info.get('command_used', 'unknown'),
            'raw_output': optical_info.get('all_output', ''),
            'found': optical_info.get('found', False),
        }
    
    def disconnect(self):
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
    print("BotLinkMaster v4.5.1 - Network Device Connection Module")