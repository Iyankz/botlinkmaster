#!/usr/bin/env python3
"""
BotLinkMaster v4.6.0 - Network Device Connection Module
SSH/Telnet support for routers and switches

Note: OLT support will be available in v5.0.0

Author: BotLinkMaster
Version: 4.6.0
"""

import paramiko
import telnetlib
import socket
import time
import re
import logging
from enum import Enum
from dataclasses import dataclass
from typing import Optional, List, Dict, Any, Tuple

from vendor_commands import (
    get_vendor_config, OpticalParser, expand_interface_name, 
    get_optical_commands, parse_mikrotik_interfaces, parse_cisco_nxos_interfaces
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
    enable_password: Optional[str] = None
    
    def __post_init__(self):
        if self.port is None:
            self.port = 22 if self.protocol == Protocol.SSH else 23


class BotLinkMaster:
    """Main class for network device connections and monitoring"""
    
    LEGACY_KEY_TYPES = [
        'ssh-rsa', 'rsa-sha2-256', 'rsa-sha2-512',
        'ssh-dss', 'ecdsa-sha2-nistp256', 'ssh-ed25519'
    ]
    
    LEGACY_KEX = [
        'diffie-hellman-group14-sha1',
        'diffie-hellman-group1-sha1',
        'diffie-hellman-group-exchange-sha1',
        'diffie-hellman-group-exchange-sha256',
        'ecdh-sha2-nistp256',
    ]
    
    LEGACY_CIPHERS = [
        'aes128-ctr', 'aes192-ctr', 'aes256-ctr',
        'aes128-cbc', '3des-cbc',
    ]
    
    def __init__(self, config: ConnectionConfig):
        self.config = config
        self.client = None
        self.shell = None
        self.transport = None
        self.connected = False
        self.vendor_config = get_vendor_config(config.vendor)
        self.optical_parser = OpticalParser(config.vendor)
        self.connection_method = None
    
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
        """Connect via SSH with legacy algorithm support"""
        try:
            logger.info(f"Connecting to {self.config.host}:{self.config.port} via SSH...")
            
            # Method 1: Transport with legacy algorithms
            try:
                return self._connect_ssh_transport()
            except Exception as e:
                logger.warning(f"Transport method failed: {e}")
            
            # Method 2: Standard SSHClient
            try:
                return self._connect_ssh_standard()
            except Exception as e:
                logger.warning(f"Standard method failed: {e}")
            
            # Method 3: Alternative
            return self._connect_ssh_alternative()
            
        except Exception as e:
            logger.error(f"SSH error: {str(e)}")
            return False
    
    def _connect_ssh_transport(self) -> bool:
        """SSH via Transport for legacy devices"""
        self.transport = paramiko.Transport((self.config.host, self.config.port))
        self.transport.set_keepalive(30)
        
        self.transport._preferred_keys = self.LEGACY_KEY_TYPES
        self.transport._preferred_kex = self.LEGACY_KEX
        self.transport._preferred_ciphers = self.LEGACY_CIPHERS
        
        self.transport.connect(
            username=self.config.username,
            password=self.config.password,
        )
        
        self.shell = self.transport.open_session()
        self.shell.get_pty(term='vt100', width=200, height=50)
        self.shell.invoke_shell()
        
        time.sleep(1.5)
        if self.shell.recv_ready():
            self.shell.recv(65535)
        
        self._disable_paging()
        
        self.connected = True
        self.connection_method = "transport"
        logger.info(f"SSH connected (transport) to {self.config.host}")
        return True
    
    def _connect_ssh_standard(self) -> bool:
        """Standard SSH connection"""
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
            disabled_algorithms={'pubkeys': ['rsa-sha2-256', 'rsa-sha2-512']}
        )
        
        self.shell = self.client.invoke_shell(width=200, height=50)
        
        time.sleep(1.5)
        if self.shell.recv_ready():
            self.shell.recv(65535)
        
        self._disable_paging()
        
        self.connected = True
        self.connection_method = "standard"
        logger.info(f"SSH connected (standard) to {self.config.host}")
        return True
    
    def _connect_ssh_alternative(self) -> bool:
        """Alternative SSH connection"""
        logger.info("Trying alternative SSH...")
        
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
        
        self.shell = self.client.invoke_shell(width=200, height=50)
        
        time.sleep(1.5)
        if self.shell.recv_ready():
            self.shell.recv(65535)
        
        self._disable_paging()
        
        self.connected = True
        self.connection_method = "alternative"
        logger.info(f"SSH connected (alternative) to {self.config.host}")
        return True
    
    def _connect_telnet(self) -> bool:
        """Connect via Telnet"""
        try:
            logger.info(f"Connecting to {self.config.host}:{self.config.port} via Telnet...")
            
            self.client = telnetlib.Telnet(
                self.config.host,
                self.config.port,
                timeout=self.config.timeout
            )
            
            # Login sequence
            output = self.client.read_until(b":", timeout=10).decode('utf-8', errors='ignore')
            if any(p in output.lower() for p in ['username', 'login', 'user']):
                self.client.write(self.config.username.encode('ascii') + b"\n")
            
            output = self.client.read_until(b":", timeout=10).decode('utf-8', errors='ignore')
            if any(p in output.lower() for p in ['password', 'pass']):
                self.client.write(self.config.password.encode('ascii') + b"\n")
            
            time.sleep(2)
            self.client.read_very_eager()
            
            self._disable_paging_telnet()
            
            self.connected = True
            self.connection_method = "telnet"
            logger.info(f"Telnet connected to {self.config.host}")
            return True
            
        except Exception as e:
            logger.error(f"Telnet error: {str(e)}")
            return False
    
    def _disable_paging(self):
        if self.vendor_config.disable_paging:
            self._execute_ssh(self.vendor_config.disable_paging, 1.0)
    
    def _disable_paging_telnet(self):
        if self.vendor_config.disable_paging:
            self._execute_telnet(self.vendor_config.disable_paging, 1.0)
    
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
            max_wait = time.time() + 15
            
            while time.time() < max_wait:
                if self.shell.recv_ready():
                    chunk = self.shell.recv(65535).decode('utf-8', errors='ignore')
                    output += chunk
                    time.sleep(0.3)
                else:
                    if output:
                        time.sleep(0.5)
                        if self.shell.recv_ready():
                            continue
                        break
                    time.sleep(0.5)
            
            return self._clean_output(output, command)
            
        except Exception as e:
            logger.error(f"SSH execute error: {str(e)}")
            return ""
    
    def _execute_telnet(self, command: str, wait_time: float) -> str:
        try:
            self.client.write(command.encode('ascii') + b"\n")
            time.sleep(wait_time)
            output = self.client.read_very_eager().decode('utf-8', errors='ignore')
            return self._clean_output(output, command)
        except Exception as e:
            logger.error(f"Telnet execute error: {str(e)}")
            return ""
    
    def _clean_output(self, output: str, command: str) -> str:
        """Clean command output"""
        # Remove ANSI escape codes
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        output = ansi_escape.sub('', output)
        return output
    
    def get_interfaces(self) -> List[Dict[str, Any]]:
        """Get all interfaces with status"""
        interfaces = []
        
        interface_parser = getattr(self.vendor_config, 'interface_parser', 'default')
        
        # MikroTik special handling
        if interface_parser == 'mikrotik':
            return self._get_mikrotik_interfaces()
        
        # Cisco NX-OS special handling
        if interface_parser == 'cisco_nxos':
            return self._get_cisco_nxos_interfaces()
        
        # Other vendors
        cmd = self.vendor_config.show_interface_brief
        output = self.execute_command(cmd, wait_time=3.0)
        
        if not output or 'Invalid' in output:
            cmd = self.vendor_config.show_interface_description
            output = self.execute_command(cmd, wait_time=3.0)
        
        if not output or 'Invalid' in output:
            for alt_cmd in self.vendor_config.alt_interface_commands:
                if '{interface}' not in alt_cmd:
                    output = self.execute_command(alt_cmd, wait_time=3.0)
                    if output and 'Invalid' not in output:
                        break
        
        if not output:
            return interfaces
        
        return self._parse_default_interfaces(output)
    
    def _get_cisco_nxos_interfaces(self) -> List[Dict[str, Any]]:
        """Get Cisco NX-OS interfaces"""
        commands = [
            "show interface status",
            "show interface brief",
            "show interface description",
        ]
        
        for cmd in commands:
            logger.info(f"Cisco NX-OS: Trying {cmd}")
            output = self.execute_command(cmd, wait_time=4.0)
            
            if output and ('Eth' in output or 'Po' in output or 'Vlan' in output):
                logger.info(f"Cisco NX-OS: Got data from {cmd}")
                interfaces = parse_cisco_nxos_interfaces(output)
                if interfaces:
                    logger.info(f"Cisco NX-OS: Parsed {len(interfaces)} interfaces")
                    return interfaces
        
        # Fallback to default parsing
        return self._parse_default_interfaces(output if output else "")
    
    def _get_mikrotik_interfaces(self) -> List[Dict[str, Any]]:
        """Get MikroTik interfaces"""
        commands = [
            "/interface print brief",
            "/interface print",
        ]
        
        for cmd in commands:
            logger.info(f"MikroTik: Trying {cmd}")
            output = self.execute_command(cmd, wait_time=4.0)
            
            if output and re.search(r'^\s*\d+\s+', output, re.MULTILINE):
                logger.info(f"MikroTik: Got data from {cmd}")
                interfaces = parse_mikrotik_interfaces(output)
                logger.info(f"MikroTik: Parsed {len(interfaces)} interfaces")
                return interfaces
        
        return []
    
    def _parse_default_interfaces(self, output: str) -> List[Dict[str, Any]]:
        """Default interface parsing"""
        interfaces = []
        lines = output.split('\n')
        
        for line in lines:
            line = line.strip()
            
            if not line or '---' in line or '===' in line:
                continue
            
            lower_line = line.lower()
            if any(h in lower_line for h in ['interface', 'port', 'status', 'protocol']):
                if not any(c.isdigit() for c in line[:20]):
                    continue
            
            parts = line.split()
            if len(parts) >= 1:
                iface_name = parts[0]
                
                if not any(c.isdigit() for c in iface_name) and '/' not in iface_name:
                    continue
                
                if iface_name.endswith('#') or iface_name.endswith('>'):
                    continue
                
                interface = {
                    'name': iface_name,
                    'status': 'unknown',
                    'description': '',
                }
                
                line_lower = line.lower()
                
                if ' up ' in line_lower or line_lower.endswith(' up'):
                    interface['status'] = 'up'
                elif ' down ' in line_lower or line_lower.endswith(' down'):
                    interface['status'] = 'down'
                
                if len(parts) >= 3:
                    desc_start = -1
                    for i, part in enumerate(parts[1:], 1):
                        if part.lower() in ['up', 'down']:
                            desc_start = i + 1
                            break
                    if desc_start > 0 and desc_start < len(parts):
                        interface['description'] = ' '.join(parts[desc_start:])
                
                interfaces.append(interface)
        
        return interfaces
    
    def get_interface_status(self, interface_name: str) -> Dict[str, Any]:
        """Get specific interface status"""
        
        # MikroTik special handling
        if self.config.vendor.lower() == 'mikrotik':
            return self._get_mikrotik_interface_status(interface_name)
        
        # Cisco NX-OS special handling
        if self.config.vendor.lower() == 'cisco_nxos':
            return self._get_cisco_nxos_interface_status(interface_name)
        
        full_interface = expand_interface_name(interface_name)
        
        cmd = self.vendor_config.show_interface.format(interface=full_interface)
        output = self.execute_command(cmd, wait_time=3.0)
        
        if not output or 'Invalid' in output or 'Error' in output:
            cmd = self.vendor_config.show_interface.format(interface=interface_name)
            output = self.execute_command(cmd, wait_time=3.0)
        
        return {
            'name': interface_name,
            'full_name': full_interface,
            'status': self.optical_parser.parse_interface_status(output),
            'description': self.optical_parser.parse_description(output),
            'raw_output': output,
        }
    
    def _get_cisco_nxos_interface_status(self, interface_name: str) -> Dict[str, Any]:
        """Get Cisco NX-OS interface status"""
        result = {
            'name': interface_name,
            'full_name': interface_name,
            'status': 'unknown',
            'description': '',
            'raw_output': '',
        }
        
        # Try show interface status first (better for status)
        output = self.execute_command("show interface status", wait_time=3.0)
        result['raw_output'] = output
        
        if output:
            # Parse to find our interface
            for line in output.split('\n'):
                line_lower = line.lower()
                iface_lower = interface_name.lower()
                
                # Check if this line contains our interface
                if iface_lower in line_lower or iface_lower.replace('/', '') in line_lower:
                    parts = line.split()
                    if len(parts) >= 3:
                        # Get description (column 2)
                        if len(parts) >= 2 and parts[1] != '--':
                            result['description'] = parts[1]
                        
                        # Check status
                        if 'connected' in line_lower and 'notconnect' not in line_lower:
                            result['status'] = 'up'
                        elif 'notconnect' in line_lower:
                            result['status'] = 'down'
                        elif 'disabled' in line_lower:
                            result['status'] = 'down'
                        elif 'sfp not' in line_lower or 'xcvr not' in line_lower:
                            result['status'] = 'down'
                        
                        if result['status'] != 'unknown':
                            logger.info(f"Cisco NX-OS {interface_name}: status={result['status']}")
                            return result
        
        # Fallback: use show interface command
        cmd = f"show interface {interface_name}"
        output2 = self.execute_command(cmd, wait_time=3.0)
        
        if output2:
            result['raw_output'] = output2
            result['status'] = self.optical_parser.parse_interface_status(output2)
            result['description'] = self.optical_parser.parse_description(output2)
        
        return result
    
    def _get_mikrotik_interface_status(self, interface_name: str) -> Dict[str, Any]:
        """Get MikroTik interface status - uses same parser as get_interfaces"""
        result = {
            'name': interface_name,
            'full_name': interface_name,
            'status': 'unknown',
            'description': '',
            'flags': '',
            'raw_output': '',
        }
        
        # Get all interfaces using the working method
        interfaces = self._get_mikrotik_interfaces()
        
        if not interfaces:
            logger.warning(f"MikroTik: No interfaces returned")
            return result
        
        # Find our interface in the list
        iface_lower = interface_name.lower()
        
        for iface in interfaces:
            if iface.get('name', '').lower() == iface_lower:
                result['status'] = iface.get('status', 'unknown')
                result['description'] = iface.get('description', '')
                result['flags'] = iface.get('flags', '')
                logger.info(f"MikroTik: Found {interface_name}, flags='{result['flags']}', status={result['status']}, desc='{result['description']}'")
                return result
        
        logger.warning(f"MikroTik: Interface '{interface_name}' not found in {len(interfaces)} interfaces")
        return result
    
    def get_optical_power(self, interface_name: str) -> Dict[str, Any]:
        """Get optical power readings"""
        full_interface = expand_interface_name(interface_name)
        
        commands = get_optical_commands(self.config.vendor, full_interface)
        
        if full_interface != interface_name:
            commands.extend(get_optical_commands(self.config.vendor, interface_name))
        
        # Remove duplicates
        seen = set()
        unique_commands = []
        for cmd in commands:
            if cmd not in seen:
                seen.add(cmd)
                unique_commands.append(cmd)
        
        all_output = ""
        result = None
        successful_cmd = None
        
        for cmd in unique_commands:
            logger.info(f"Trying optical: {cmd}")
            output = self.execute_command(cmd, wait_time=3.0)
            
            if output:
                if any(err in output for err in ['Invalid', 'Error', 'Unrecognized', '% ']):
                    continue
                
                all_output += f"\n{'='*50}\n{cmd}\n{'='*50}\n{output}\n"
                
                parsed = self.optical_parser.parse_optical_power(output)
                
                if parsed['found']:
                    result = parsed
                    successful_cmd = cmd
                    logger.info(f"Found optical with: {cmd}")
                    break
        
        if not result or not result.get('found'):
            result = self.optical_parser.parse_optical_power(all_output)
            successful_cmd = 'combined' if result.get('found') else 'none'
        
        result['interface'] = interface_name
        result['full_interface'] = full_interface
        result['all_output'] = all_output
        result['command_used'] = successful_cmd
        
        return result
    
    def check_interface_with_optical(self, interface_name: str) -> Dict[str, Any]:
        """Get complete interface info with optical"""
        interface_info = self.get_interface_status(interface_name)
        optical_info = self.get_optical_power(interface_name)
        
        return {
            'name': interface_name,
            'full_name': interface_info.get('full_name', interface_name),
            'status': interface_info.get('status', 'unknown'),
            'description': interface_info.get('description', ''),
            'flags': interface_info.get('flags', ''),
            'rx_power': optical_info.get('rx_power'),
            'tx_power': optical_info.get('tx_power'),
            'rx_power_dbm': optical_info.get('rx_power_dbm', 'N/A'),
            'tx_power_dbm': optical_info.get('tx_power_dbm', 'N/A'),
            'optical_status': optical_info.get('signal_status', 'unknown'),
            'command_used': optical_info.get('command_used', 'unknown'),
            'raw_output': optical_info.get('all_output', ''),
            'found': optical_info.get('found', False),
        }
    
    def disconnect(self):
        try:
            if self.transport:
                self.transport.close()
                self.transport = None
            if self.shell:
                self.shell.close()
                self.shell = None
            if self.client:
                self.client.close()
                self.client = None
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
    print("=" * 60)
    print("BotLinkMaster v4.6.0 - Network Device Connection Module")
    print("=" * 60)
    print("\nSupported Vendors:")
    from vendor_commands import get_supported_vendors
    for i, v in enumerate(get_supported_vendors(), 1):
        print(f"  {i:2}. {v}")
    print("\nNote: OLT support will be available in v5.0.0")