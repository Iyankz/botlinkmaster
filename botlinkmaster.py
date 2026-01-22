#!/usr/bin/env python3
"""
BotLinkMaster v4.8.7 - Network Device Connection Module
SSH/Telnet support for routers and switches

CHANGELOG v4.8.7:
- FIX: MikroTik CRS326 SSH algorithm compatibility for RouterOS 7.16.x
- FIX: Extended timeouts (30s → 60s) for switches with many interfaces
- FIX: Improved prompt detection for various vendors
- ADD: Additional legacy SSH algorithms for older devices
- IMPROVED: Hard timeout increased for slow-responding devices

CHANGELOG v4.8.6:
- FIX: MikroTik menggunakan "/interface ethernet print without-paging"
- FIX: Timeout MikroTik ditambah ke 30s untuk device dengan banyak interface

Note: OLT support will be available in v5.0.0

Author: BotLinkMaster
Version: 4.8.7
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
    
    # v4.8.7: Extended legacy key types for CRS326 compatibility
    LEGACY_KEY_TYPES = [
        'ssh-rsa', 'rsa-sha2-256', 'rsa-sha2-512',
        'ssh-dss', 'ecdsa-sha2-nistp256', 'ecdsa-sha2-nistp384',
        'ecdsa-sha2-nistp521', 'ssh-ed25519'
    ]
    
    # v4.8.7: Extended KEX algorithms for RouterOS 7.16.x
    LEGACY_KEX = [
        'curve25519-sha256', 'curve25519-sha256@libssh.org',
        'ecdh-sha2-nistp256', 'ecdh-sha2-nistp384', 'ecdh-sha2-nistp521',
        'diffie-hellman-group-exchange-sha256',
        'diffie-hellman-group14-sha256',
        'diffie-hellman-group14-sha1',
        'diffie-hellman-group1-sha1',
        'diffie-hellman-group-exchange-sha1',
    ]
    
    # v4.8.7: Extended ciphers for legacy devices
    LEGACY_CIPHERS = [
        'aes128-ctr', 'aes192-ctr', 'aes256-ctr',
        'aes128-gcm@openssh.com', 'aes256-gcm@openssh.com',
        'chacha20-poly1305@openssh.com',
        'aes128-cbc', 'aes192-cbc', 'aes256-cbc',
        '3des-cbc',
    ]
    
    # v4.8.7: Updated vendor-specific timeouts with extended values
    VENDOR_TIMEOUTS = {
        'mikrotik': {
            'idle_timeout': 15.0,      # v4.8.7: Increased from 10.0
            'initial_wait': 10.0,      # v4.8.7: Increased from 8.0
            'hard_timeout': 120,       # v4.8.7: Increased from 90 for CRS326
            'prompt_timeout': 30,      # v4.8.7: Increased from 20
            'command_wait': 45.0,      # v4.8.7: Increased from 30.0
        },
        'huawei': {
            'idle_timeout': 8.0,       # v4.8.7: Increased from 5.0
            'initial_wait': 8.0,       # v4.8.7: Increased from 5.0
            'hard_timeout': 90,        # v4.8.7: Increased from 60
            'prompt_timeout': 20,      # v4.8.7: Increased from 15
            'command_wait': 15.0,      # v4.8.7: Increased from 10.0
        },
        'cisco_nxos': {
            'idle_timeout': 5.0,
            'initial_wait': 5.0,
            'hard_timeout': 60,
            'prompt_timeout': 15,
            'command_wait': 10.0,
        },
        'cisco_ios': {
            'idle_timeout': 5.0,
            'initial_wait': 5.0,
            'hard_timeout': 60,
            'prompt_timeout': 15,
            'command_wait': 10.0,
        },
        'default': {
            'idle_timeout': 5.0,
            'initial_wait': 5.0,
            'hard_timeout': 60,
            'prompt_timeout': 15,
            'command_wait': 10.0,
        }
    }
    
    # Prompt patterns for different vendors
    PROMPT_PATTERNS = {
        'mikrotik': [
            r'\[[\w\-@]+\]\s*[>#]\s*$',
            r'\[[\w\-@]+\]\s*/[\w/]*[>#]\s*$',
        ],
        'cisco': [
            r'[\w\-]+[>#]\s*$',
        ],
        'huawei': [
            r'<[\w\-]+>\s*$',
            r'\[[\w\-~]+\]\s*$',
        ],
        'default': [
            r'[>#\$]\s*$',
        ],
    }
    
    def __init__(self, config: ConnectionConfig):
        self.config = config
        self.client = None
        self.shell = None
        self.transport = None
        self.connected = False
        self.vendor_config = get_vendor_config(config.vendor)
        self.optical_parser = OpticalParser(config.vendor)
        self.connection_method = None
        
        vendor_key = config.vendor.lower()
        
        # v4.8.7: Match vendor timeouts more flexibly
        if 'mikrotik' in vendor_key:
            self.timeouts = self.VENDOR_TIMEOUTS['mikrotik']
            self.prompt_patterns = self.PROMPT_PATTERNS['mikrotik']
        elif 'huawei' in vendor_key:
            self.timeouts = self.VENDOR_TIMEOUTS['huawei']
            self.prompt_patterns = self.PROMPT_PATTERNS['huawei']
        elif 'cisco' in vendor_key:
            if 'nxos' in vendor_key:
                self.timeouts = self.VENDOR_TIMEOUTS['cisco_nxos']
            else:
                self.timeouts = self.VENDOR_TIMEOUTS['cisco_ios']
            self.prompt_patterns = self.PROMPT_PATTERNS['cisco']
        else:
            self.timeouts = self.VENDOR_TIMEOUTS['default']
            self.prompt_patterns = self.PROMPT_PATTERNS['default']
    
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
        """Connect via SSH with legacy algorithm support - v4.8.7"""
        try:
            logger.info(f"Connecting to {self.config.host}:{self.config.port} via SSH...")
            
            # v4.8.7: Try transport method first (better for legacy devices like CRS326)
            try:
                return self._connect_ssh_transport()
            except Exception as e:
                logger.warning(f"Transport method failed: {e}")
            
            # Try standard method
            try:
                return self._connect_ssh_standard()
            except Exception as e:
                logger.warning(f"Standard method failed: {e}")
            
            # Try alternative method
            return self._connect_ssh_alternative()
            
        except Exception as e:
            logger.error(f"SSH error: {str(e)}")
            return False
    
    def _connect_ssh_transport(self) -> bool:
        """SSH via Transport for legacy devices - v4.8.7 improved"""
        self.transport = paramiko.Transport((self.config.host, self.config.port))
        self.transport.set_keepalive(30)
        
        # v4.8.7: Set extended algorithms for CRS326 compatibility
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
        
        # Wait for prompt
        if not self._wait_for_prompt(timeout=self.timeouts.get('prompt_timeout', 30)):
            logger.warning("Timeout waiting for initial prompt, continuing anyway...")
        
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
        
        if not self._wait_for_prompt(timeout=self.timeouts.get('prompt_timeout', 30)):
            logger.warning("Timeout waiting for initial prompt, continuing anyway...")
        
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
        
        if not self._wait_for_prompt(timeout=self.timeouts.get('prompt_timeout', 30)):
            logger.warning("Timeout waiting for initial prompt, continuing anyway...")
        
        self._disable_paging()
        
        self.connected = True
        self.connection_method = "alternative"
        logger.info(f"SSH connected (alternative) to {self.config.host}")
        return True
    
    def _wait_for_prompt(self, timeout: int = 30) -> bool:
        """Wait for shell prompt to appear - v4.8.7 improved"""
        logger.info(f"Waiting for prompt (timeout={timeout}s)...")
        
        buffer = ""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if self.shell.recv_ready():
                try:
                    data = self.shell.recv(65535).decode('utf-8', errors='ignore')
                    buffer += data
                    
                    # Check for prompt patterns
                    for pattern in self.prompt_patterns:
                        if re.search(pattern, buffer):
                            logger.info(f"Prompt detected! Buffer size: {len(buffer)}")
                            return True
                    
                    # MikroTik: ] > or ] # at end of line
                    if re.search(r'\]\s*[>#]\s*$', buffer):
                        logger.info("MikroTik prompt detected!")
                        return True
                    
                    # Cisco/Generic: hostname# or hostname>
                    if re.search(r'[\w\-]+[>#]\s*$', buffer):
                        logger.info("Generic prompt detected!")
                        return True
                    
                    # Huawei: <hostname> or [hostname]
                    if re.search(r'[<\[][\w\-~]+[>\]]\s*$', buffer):
                        logger.info("Huawei prompt detected!")
                        return True
                        
                except Exception as e:
                    logger.warning(f"Error reading data: {e}")
            
            time.sleep(0.2)
        
        logger.warning(f"Prompt timeout. Buffer ({len(buffer)} bytes)")
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
            self._execute_ssh(self.vendor_config.disable_paging, 2.0)
    
    def _disable_paging_telnet(self):
        if self.vendor_config.disable_paging:
            self._execute_telnet(self.vendor_config.disable_paging, 2.0)
    
    def execute_command(self, command: str, wait_time: float = None) -> str:
        """Execute command with vendor-specific timeout if not specified"""
        if not self.connected:
            return ""
        
        if wait_time is None:
            wait_time = self.timeouts.get('command_wait', self.timeouts['initial_wait'])
        
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
        """Execute SSH command with idle-time based reading - v4.8.7 improved"""
        try:
            # Clear any pending data in buffer first
            while self.shell.recv_ready():
                self.shell.recv(65535)
            
            # Send command
            logger.info(f"Executing: {command}")
            self.shell.send(command + "\n")
            
            # Initial wait for command to be processed
            time.sleep(wait_time)

            output = ""
            last_data_time = time.time()
            
            idle_timeout = self.timeouts['idle_timeout']
            hard_timeout = time.time() + self.timeouts['hard_timeout']
            
            consecutive_empty_reads = 0
            max_consecutive_empty = 20  # v4.8.7: Increased from 15

            while True:
                if self.shell.recv_ready():
                    data = self.shell.recv(65535).decode("utf-8", errors="ignore")
                    
                    if data:
                        output += data
                        last_data_time = time.time()
                        consecutive_empty_reads = 0
                        
                        # Check if we got a prompt (command complete)
                        if re.search(r'\]\s*[>#/]\s*$', output):
                            time.sleep(0.5)
                            if self.shell.recv_ready():
                                extra = self.shell.recv(65535).decode("utf-8", errors="ignore")
                                if extra:
                                    output += extra
                            break
                        
                        continue
                    else:
                        consecutive_empty_reads += 1
                
                now = time.time()
                idle_time = now - last_data_time

                if output and idle_time >= idle_timeout:
                    # Multiple extra reads to ensure we got everything
                    for _ in range(7):  # v4.8.7: Increased from 5
                        time.sleep(0.5)
                        if self.shell.recv_ready():
                            extra = self.shell.recv(65535).decode("utf-8", errors="ignore")
                            if extra:
                                output += extra
                                logger.info(f"SSH: Captured extra {len(extra)} bytes after idle timeout")
                    break
                
                if consecutive_empty_reads >= max_consecutive_empty:
                    time.sleep(1.0)
                    if self.shell.recv_ready():
                        extra = self.shell.recv(65535).decode("utf-8", errors="ignore")
                        if extra:
                            output += extra
                            logger.info(f"SSH: Captured {len(extra)} bytes on final attempt")
                    break

                if now >= hard_timeout:
                    logger.warning(f"SSH hard timeout for '{command}'")
                    break

                time.sleep(0.2)

            logger.info(f"Command '{command}': received {len(output)} bytes total")
            
            return self._clean_output(output, command)

        except Exception as e:
            logger.error(f"SSH execute error: {e}")
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
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        output = ansi_escape.sub('', output)
        return output
    
    def get_interfaces(self) -> List[Dict[str, Any]]:
        """Get all interfaces with status"""
        interfaces = []
        
        interface_parser = getattr(self.vendor_config, 'interface_parser', 'default')
        
        if interface_parser == 'mikrotik':
            return self._get_mikrotik_interfaces()
        
        if interface_parser == 'cisco_nxos':
            return self._get_cisco_nxos_interfaces()
        
        cmd = self.vendor_config.show_interface_brief
        output = self.execute_command(cmd, wait_time=5.0)
        
        if not output or 'Invalid' in output:
            cmd = self.vendor_config.show_interface_description
            output = self.execute_command(cmd, wait_time=5.0)
        
        if not output or 'Invalid' in output:
            for alt_cmd in self.vendor_config.alt_interface_commands:
                if '{interface}' not in alt_cmd:
                    output = self.execute_command(alt_cmd, wait_time=5.0)
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
            output = self.execute_command(cmd, wait_time=5.0)
            
            if output and ('Eth' in output or 'Po' in output or 'Vlan' in output):
                logger.info(f"Cisco NX-OS: Got data from {cmd}")
                interfaces = parse_cisco_nxos_interfaces(output)
                if interfaces:
                    logger.info(f"Cisco NX-OS: Parsed {len(interfaces)} interfaces")
                    return interfaces
        
        return self._parse_default_interfaces(output if output else "")
    
    def _get_mikrotik_interfaces(self) -> List[Dict[str, Any]]:
        """Get MikroTik interfaces - v4.8.7 improved for CRS326"""
        
        expected_count = self._get_mikrotik_interface_count()
        if expected_count:
            logger.info(f"MikroTik: Expected approximately {expected_count} interfaces")
        
        # v4.8.7: Commands optimized for CRS326
        commands = [
            "/interface ethernet print without-paging",
            "/interface print brief without-paging",
            "/interface print without-paging",
        ]
        
        # v4.8.7: Use longer wait time for CRS326 and large switches
        wait_time = self.timeouts.get('command_wait', 45.0)
        
        for cmd in commands:
            logger.info(f"MikroTik: Trying {cmd}")
            
            output = self.execute_command(cmd, wait_time=wait_time)
            
            if output and re.search(r'^\s*\d+\s+', output, re.MULTILINE):
                logger.info(f"MikroTik: Got {len(output)} bytes from {cmd}")
                
                interfaces = parse_mikrotik_interfaces(output)
                logger.info(f"MikroTik: Parsed {len(interfaces)} interfaces")
                
                if interfaces:
                    logger.info(f"MikroTik: First interface: {interfaces[0]['name']}")
                    logger.info(f"MikroTik: Last interface: {interfaces[-1]['name']}")
                    return interfaces
        
        return []
    
    def _get_mikrotik_interface_count(self) -> int:
        """Get expected interface count from MikroTik"""
        try:
            cmd = "/interface ethernet print count-only"
            output = self.execute_command(cmd, wait_time=5.0)
            
            if output:
                lines = output.strip().split('\n')
                for line in reversed(lines):
                    line = line.strip()
                    if not line or line.endswith('>') or line.endswith('#'):
                        continue
                    if line.isdigit():
                        count = int(line)
                        logger.info(f"MikroTik: ethernet count-only returned {count}")
                        return count
                
                match = re.search(r'\b(\d+)\b', output)
                if match:
                    count = int(match.group(1))
                    return count
        except Exception as e:
            logger.warning(f"MikroTik: Failed to get count: {e}")
        
        return 0
    
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
        
        if self.config.vendor.lower() == 'mikrotik':
            return self._get_mikrotik_interface_status(interface_name)
        
        if self.config.vendor.lower() == 'cisco_nxos':
            return self._get_cisco_nxos_interface_status(interface_name)
        
        full_interface = expand_interface_name(interface_name)
        
        cmd = self.vendor_config.show_interface.format(interface=full_interface)
        output = self.execute_command(cmd, wait_time=5.0)
        
        if not output or 'Invalid' in output or 'Error' in output:
            cmd = self.vendor_config.show_interface.format(interface=interface_name)
            output = self.execute_command(cmd, wait_time=5.0)
        
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
        
        output = self.execute_command("show interface status", wait_time=5.0)
        result['raw_output'] = output
        
        if output:
            for line in output.split('\n'):
                line_lower = line.lower()
                iface_lower = interface_name.lower()
                
                if iface_lower in line_lower or iface_lower.replace('/', '') in line_lower:
                    parts = line.split()
                    if len(parts) >= 3:
                        if len(parts) >= 2 and parts[1] != '--':
                            result['description'] = parts[1]
                        
                        if 'connected' in line_lower and 'notconnect' not in line_lower:
                            result['status'] = 'up'
                        elif 'notconnect' in line_lower:
                            result['status'] = 'down'
                        elif 'disabled' in line_lower:
                            result['status'] = 'down'
                        elif 'sfp not' in line_lower or 'xcvr not' in line_lower:
                            result['status'] = 'down'
                        
                        if result['status'] != 'unknown':
                            return result
        
        cmd = f"show interface {interface_name}"
        output2 = self.execute_command(cmd, wait_time=5.0)
        
        if output2:
            result['raw_output'] = output2
            result['status'] = self.optical_parser.parse_interface_status(output2)
            result['description'] = self.optical_parser.parse_description(output2)
        
        return result
    
    def _get_mikrotik_interface_status(self, interface_name: str) -> Dict[str, Any]:
        """Get MikroTik interface status"""
        result = {
            'name': interface_name,
            'full_name': interface_name,
            'status': 'unknown',
            'description': '',
            'flags': '',
            'raw_output': '',
        }
        
        interfaces = self._get_mikrotik_interfaces()
        
        if not interfaces:
            logger.warning(f"MikroTik: No interfaces returned")
            return result
        
        iface_lower = interface_name.lower()
        
        for iface in interfaces:
            if iface.get('name', '').lower() == iface_lower:
                result['status'] = iface.get('status', 'unknown')
                result['description'] = iface.get('description', '')
                result['flags'] = iface.get('flags', '')
                logger.info(f"MikroTik: Found {interface_name}, flags='{result['flags']}', status={result['status']}")
                return result
        
        logger.warning(f"MikroTik: Interface '{interface_name}' not found in {len(interfaces)} interfaces")
        return result
    
    def get_optical_power(self, interface_name: str) -> Dict[str, Any]:
        """Get optical power readings"""
        full_interface = expand_interface_name(interface_name)
        
        commands = get_optical_commands(self.config.vendor, full_interface)
        
        if full_interface != interface_name:
            commands.extend(get_optical_commands(self.config.vendor, interface_name))
        
        seen = set()
        unique_commands = []
        for cmd in commands:
            if cmd not in seen:
                seen.add(cmd)
                unique_commands.append(cmd)
        
        all_output = ""
        result = None
        successful_cmd = None
        
        # v4.8.7: Use command_wait timeout
        wait_time = self.timeouts.get('command_wait', 10.0)
        
        for cmd in unique_commands:
            logger.info(f"Trying optical: {cmd}")
            output = self.execute_command(cmd, wait_time=wait_time)
            
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
    print("BotLinkMaster v4.8.7 - Network Device Connection Module")
    print("=" * 60)
    print("\nSupported Vendors:")
    from vendor_commands import get_supported_vendors
    for i, v in enumerate(get_supported_vendors(), 1):
        print(f"  {i:2}. {v}")
    print("\nv4.8.7 Fixes:")
    print("  - MikroTik CRS326 SSH algorithm compatibility")
    print("  - Extended timeouts for large switches")
    print("  - Improved prompt detection")
    print("  - Additional legacy SSH algorithms")
    print("\nNote: OLT support will be available in v5.0.0")
