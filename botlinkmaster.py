#!/usr/bin/env python3
"""
BotLinkMaster v4.5.2 - Network Device Connection Module
SSH/Telnet with multi-vendor support

Features:
- SSH with legacy algorithm support (Huawei, ZTE fix)
- Telnet support with custom port
- Multi-vendor optical power parsing
- Interface listing with special parsers for MikroTik, ZTE OLT
- Port forwarding support (same IP, different ports)

Author: BotLinkMaster
Version: 4.5.2
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
    get_vendor_config, OpticalParser, expand_interface_name, get_optical_commands,
    parse_mikrotik_interfaces, parse_zte_olt_interfaces
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class Protocol(Enum):
    """Connection protocol types"""
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
    enable_password: Optional[str] = None
    
    def __post_init__(self):
        """Set default port based on protocol if not specified"""
        if self.port is None:
            self.port = 22 if self.protocol == Protocol.SSH else 23


class BotLinkMaster:
    """
    Main class for network device connections and monitoring.
    
    Supports:
    - SSH connections with legacy algorithm support
    - Telnet connections
    - Multi-vendor command execution
    - Optical power monitoring
    - Interface status checking
    """
    
    # Legacy algorithms for older devices (Huawei, ZTE, etc.)
    LEGACY_KEY_TYPES = [
        'ssh-rsa', 'rsa-sha2-256', 'rsa-sha2-512',
        'ssh-dss', 'ecdsa-sha2-nistp256', 'ecdsa-sha2-nistp384',
        'ecdsa-sha2-nistp521', 'ssh-ed25519'
    ]
    
    LEGACY_KEX_ALGORITHMS = [
        'diffie-hellman-group14-sha1',
        'diffie-hellman-group1-sha1',
        'diffie-hellman-group-exchange-sha1',
        'diffie-hellman-group-exchange-sha256',
        'ecdh-sha2-nistp256',
        'ecdh-sha2-nistp384',
        'ecdh-sha2-nistp521',
        'curve25519-sha256',
        'curve25519-sha256@libssh.org',
    ]
    
    LEGACY_CIPHERS = [
        'aes128-ctr', 'aes192-ctr', 'aes256-ctr',
        'aes128-cbc', 'aes192-cbc', 'aes256-cbc',
        '3des-cbc', 'blowfish-cbc', 'arcfour',
    ]
    
    def __init__(self, config: ConnectionConfig):
        """
        Initialize BotLinkMaster with connection configuration.
        
        Args:
            config: ConnectionConfig object with device details
        """
        self.config = config
        self.client = None
        self.shell = None
        self.transport = None
        self.connected = False
        self.vendor_config = get_vendor_config(config.vendor)
        self.optical_parser = OpticalParser(config.vendor)
        self.connection_method = None
    
    def connect(self) -> bool:
        """
        Establish connection to the device.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            if self.config.protocol == Protocol.SSH:
                return self._connect_ssh()
            elif self.config.protocol == Protocol.TELNET:
                return self._connect_telnet()
            return False
        except Exception as e:
            logger.error(f"Connection failed to {self.config.host}: {str(e)}")
            return False
    
    def _connect_ssh(self) -> bool:
        """
        Connect via SSH with legacy algorithm support for older devices.
        This fixes "no matching host key type found" error on Huawei/ZTE.
        
        Returns:
            bool: True if connection successful
        """
        try:
            logger.info(f"Connecting to {self.config.host}:{self.config.port} via SSH...")
            
            # Method 1: Try using Transport with legacy algorithms
            try:
                return self._connect_ssh_transport()
            except Exception as e:
                logger.warning(f"Transport method failed: {e}")
            
            # Method 2: Try standard SSHClient with disabled algorithms
            try:
                return self._connect_ssh_standard()
            except Exception as e:
                logger.warning(f"Standard method failed: {e}")
            
            # Method 3: Try alternative connection
            return self._connect_ssh_alternative()
            
        except paramiko.AuthenticationException:
            logger.error(f"Authentication failed for {self.config.host}")
            return False
        except socket.timeout:
            logger.error(f"Connection timeout to {self.config.host}")
            return False
        except Exception as e:
            logger.error(f"SSH connection error: {str(e)}")
            return False
    
    def _connect_ssh_transport(self) -> bool:
        """
        SSH connection using Transport for legacy algorithm support.
        Best for older devices like Huawei, ZTE that use ssh-rsa.
        """
        self.transport = paramiko.Transport((self.config.host, self.config.port))
        self.transport.set_keepalive(30)
        
        # Set legacy algorithms
        self.transport._preferred_keys = self.LEGACY_KEY_TYPES
        self.transport._preferred_kex = self.LEGACY_KEX_ALGORITHMS
        self.transport._preferred_ciphers = self.LEGACY_CIPHERS
        
        # Connect
        self.transport.connect(
            username=self.config.username,
            password=self.config.password,
        )
        
        # Create shell session
        self.shell = self.transport.open_session()
        self.shell.get_pty(term='vt100', width=200, height=50)
        self.shell.invoke_shell()
        
        # Wait for initial prompt
        time.sleep(1.5)
        if self.shell.recv_ready():
            self.shell.recv(65535)
        
        # Disable paging
        self._disable_paging()
        
        self.connected = True
        self.connection_method = "transport"
        logger.info(f"SSH connected (transport) to {self.config.host}")
        return True
    
    def _connect_ssh_standard(self) -> bool:
        """
        Standard SSH connection with SSHClient.
        """
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        # Try with disabled algorithms first (for newer OpenSSH)
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
        """
        Alternative SSH connection method for problematic devices.
        """
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
        """
        Connect via Telnet protocol.
        
        Returns:
            bool: True if connection successful
        """
        try:
            logger.info(f"Connecting to {self.config.host}:{self.config.port} via Telnet...")
            
            self.client = telnetlib.Telnet(
                self.config.host,
                self.config.port,
                timeout=self.config.timeout
            )
            
            # Handle login sequence
            self._telnet_login()
            
            # Disable paging
            self._disable_paging_telnet()
            
            self.connected = True
            self.connection_method = "telnet"
            logger.info(f"Telnet connected to {self.config.host}")
            return True
            
        except socket.timeout:
            logger.error(f"Telnet timeout to {self.config.host}")
            return False
        except Exception as e:
            logger.error(f"Telnet error: {str(e)}")
            return False
    
    def _telnet_login(self):
        """Handle Telnet login sequence"""
        # Wait for username prompt
        output = self.client.read_until(b":", timeout=10).decode('utf-8', errors='ignore')
        
        if any(p in output.lower() for p in ['username', 'login', 'user']):
            self.client.write(self.config.username.encode('ascii') + b"\n")
        
        # Wait for password prompt
        output = self.client.read_until(b":", timeout=10).decode('utf-8', errors='ignore')
        
        if any(p in output.lower() for p in ['password', 'pass']):
            self.client.write(self.config.password.encode('ascii') + b"\n")
        
        # Wait for command prompt
        time.sleep(2)
        self.client.read_very_eager()
        
        # Handle enable mode if needed
        if self.config.enable_password:
            self.client.write(b"enable\n")
            time.sleep(1)
            output = self.client.read_very_eager().decode('utf-8', errors='ignore')
            if 'password' in output.lower():
                self.client.write(self.config.enable_password.encode('ascii') + b"\n")
                time.sleep(1)
                self.client.read_very_eager()
    
    def _disable_paging(self):
        """Disable terminal paging for SSH connections"""
        if self.vendor_config.disable_paging:
            self._execute_ssh(self.vendor_config.disable_paging, wait_time=1.0)
    
    def _disable_paging_telnet(self):
        """Disable terminal paging for Telnet connections"""
        if self.vendor_config.disable_paging:
            self._execute_telnet(self.vendor_config.disable_paging, wait_time=1.0)
    
    def execute_command(self, command: str, wait_time: float = 2.0) -> str:
        """
        Execute command on the device.
        
        Args:
            command: Command string to execute
            wait_time: Time to wait for response (seconds)
            
        Returns:
            str: Command output
        """
        if not self.connected:
            logger.warning("Not connected to device")
            return ""
        
        try:
            if self.config.protocol == Protocol.SSH:
                return self._execute_ssh(command, wait_time)
            elif self.config.protocol == Protocol.TELNET:
                return self._execute_telnet(command, wait_time)
            return ""
        except Exception as e:
            logger.error(f"Command execution error: {str(e)}")
            return ""
    
    def _execute_ssh(self, command: str, wait_time: float) -> str:
        """Execute command via SSH"""
        try:
            # Send command
            self.shell.send(command + "\n")
            time.sleep(wait_time)
            
            # Collect output
            output = ""
            max_wait = time.time() + 15  # 15 second timeout
            
            while time.time() < max_wait:
                if self.shell.recv_ready():
                    chunk = self.shell.recv(65535).decode('utf-8', errors='ignore')
                    output += chunk
                    time.sleep(0.3)
                else:
                    if output:
                        # Got some output, wait a bit more for completion
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
        """Execute command via Telnet"""
        try:
            self.client.write(command.encode('ascii') + b"\n")
            time.sleep(wait_time)
            
            # Read all available output
            output = self.client.read_very_eager().decode('utf-8', errors='ignore')
            
            return self._clean_output(output, command)
            
        except Exception as e:
            logger.error(f"Telnet execute error: {str(e)}")
            return ""
    
    def _clean_output(self, output: str, command: str) -> str:
        """
        Clean command output by removing echo and control characters.
        
        Args:
            output: Raw command output
            command: Original command (to remove from output)
            
        Returns:
            str: Cleaned output
        """
        # Remove ANSI escape sequences
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        output = ansi_escape.sub('', output)
        
        # Remove command echo
        lines = output.split('\n')
        cleaned_lines = []
        skip_first = True
        
        for line in lines:
            # Skip the command echo line
            if skip_first and command in line:
                skip_first = False
                continue
            cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    def get_interfaces(self) -> List[Dict[str, Any]]:
        """
        Get all interfaces from the device with status and description.
        
        Returns:
            List of interface dictionaries with 'name', 'status', 'description'
        """
        interfaces = []
        
        # Check for special parser based on vendor
        interface_parser = getattr(self.vendor_config, 'interface_parser', 'default')
        
        # Special handling for MikroTik
        if interface_parser == 'mikrotik':
            return self._get_mikrotik_interfaces()
        
        # Get interface list for other vendors
        cmd = self.vendor_config.show_interface_brief
        output = self.execute_command(cmd, wait_time=3.0)
        
        # Try description command if brief fails
        if not output or 'Invalid' in output or 'Error' in output:
            cmd = self.vendor_config.show_interface_description
            output = self.execute_command(cmd, wait_time=3.0)
        
        # Try status command
        if not output or 'Invalid' in output:
            cmd = self.vendor_config.show_interface_status
            output = self.execute_command(cmd, wait_time=3.0)
        
        # Try alternative commands
        if not output or 'Invalid' in output:
            for alt_cmd in self.vendor_config.alt_interface_commands:
                if '{interface}' not in alt_cmd:  # Skip interface-specific commands
                    output = self.execute_command(alt_cmd, wait_time=3.0)
                    if output and 'Invalid' not in output and 'Error' not in output:
                        break
        
        if not output:
            logger.warning("Could not get interface list")
            return interfaces
        
        # Use appropriate parser
        if interface_parser == 'zte_olt':
            logger.info("Using ZTE OLT interface parser")
            return parse_zte_olt_interfaces(output)
        
        # Default parsing
        return self._parse_default_interfaces(output)
    
    def _get_mikrotik_interfaces(self) -> List[Dict[str, Any]]:
        """
        Get MikroTik interfaces with special handling.
        Tries multiple commands and cleans output before parsing.
        """
        interfaces = []
        
        # Commands to try in order
        commands = [
            "/interface print",
            "/interface print brief",
            "/interface ethernet print",
            "interface print",
        ]
        
        output = ""
        for cmd in commands:
            logger.info(f"MikroTik: Trying command: {cmd}")
            output = self.execute_command(cmd, wait_time=4.0)  # Longer wait for MikroTik
            
            if output:
                # Check if output contains interface data
                # Should have lines starting with numbers
                has_interface_data = bool(re.search(r'^\s*\d+\s+', output, re.MULTILINE))
                if has_interface_data:
                    logger.info(f"MikroTik: Got interface data from: {cmd}")
                    break
        
        if not output:
            logger.warning("MikroTik: Could not get interface list from any command")
            return interfaces
        
        # Clean ANSI escape codes
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        output = ansi_escape.sub('', output)
        
        # Parse using MikroTik parser
        interfaces = parse_mikrotik_interfaces(output)
        
        logger.info(f"MikroTik: Parsed {len(interfaces)} interfaces")
        return interfaces
        
        # Default parsing
        return self._parse_default_interfaces(output)
    
    def _parse_default_interfaces(self, output: str) -> List[Dict[str, Any]]:
        """
        Default interface parsing for most vendors.
        
        Args:
            output: Raw command output
            
        Returns:
            List of interface dictionaries
        """
        interfaces = []
        lines = output.split('\n')
        
        for line in lines:
            line = line.strip()
            
            # Skip empty lines and separators
            if not line or '---' in line or '===' in line or '***' in line:
                continue
            
            # Skip obvious header lines
            lower_line = line.lower()
            header_keywords = ['interface', 'port', 'status', 'protocol', 'description', 
                              'type', 'vlan', 'duplex', 'speed', 'mtu']
            if any(kw in lower_line for kw in header_keywords):
                # But only if no digits in first 20 chars (likely header)
                if not any(c.isdigit() for c in line[:20]):
                    continue
            
            parts = line.split()
            if len(parts) >= 1:
                iface_name = parts[0]
                
                # Validate interface name (should contain number or slash)
                if not any(c.isdigit() for c in iface_name) and '/' not in iface_name:
                    continue
                
                # Skip if looks like a command prompt
                if iface_name.endswith('#') or iface_name.endswith('>'):
                    continue
                
                interface = {
                    'name': iface_name,
                    'status': 'unknown',
                    'description': '',
                }
                
                # Determine status from the line
                line_lower = line.lower()
                
                # Check for UP indicators
                up_indicators = [' up ', ' up/', '/up ', '*up', 'up(s)', 
                                'connected', 'link-ok', 'running']
                down_indicators = [' down ', ' down/', '/down ', '*down', 'down(s)',
                                  'notconnect', 'disabled', 'no-link', 'offline']
                
                for indicator in up_indicators:
                    if indicator in line_lower or line_lower.endswith(' up'):
                        interface['status'] = 'up'
                        break
                
                if interface['status'] == 'unknown':
                    for indicator in down_indicators:
                        if indicator in line_lower or line_lower.endswith(' down'):
                            interface['status'] = 'down'
                            break
                
                # Try to extract description (usually last columns)
                if len(parts) >= 3:
                    # Find where description might start
                    desc_start = -1
                    for i, part in enumerate(parts[1:], 1):
                        part_lower = part.lower()
                        if part_lower in ['up', 'down', '*up', '*down', 'up(s)', 'down(s)']:
                            desc_start = i + 1
                            break
                    
                    if desc_start > 0 and desc_start < len(parts):
                        interface['description'] = ' '.join(parts[desc_start:])
                
                interfaces.append(interface)
        
        return interfaces
    
    def get_interface_status(self, interface_name: str) -> Dict[str, Any]:
        """
        Get detailed status for a specific interface.
        
        Args:
            interface_name: Name of the interface
            
        Returns:
            Dictionary with interface details
        """
        full_interface = expand_interface_name(interface_name)
        
        # Special handling for MikroTik
        if self.config.vendor.lower() == 'mikrotik':
            return self._get_mikrotik_interface_status(interface_name)
        
        # Try with expanded name first
        cmd = self.vendor_config.show_interface.format(interface=full_interface)
        output = self.execute_command(cmd, wait_time=3.0)
        
        # Try original name if expanded fails
        if not output or 'Invalid' in output or 'Error' in output or '%' in output:
            cmd = self.vendor_config.show_interface.format(interface=interface_name)
            output = self.execute_command(cmd, wait_time=3.0)
        
        # Parse results
        result = {
            'name': interface_name,
            'full_name': full_interface,
            'status': self.optical_parser.parse_interface_status(output),
            'description': self.optical_parser.parse_description(output),
            'raw_output': output,
        }
        
        return result
    
    def _get_mikrotik_interface_status(self, interface_name: str) -> Dict[str, Any]:
        """
        Get MikroTik interface status using /interface print.
        
        MikroTik format:
         #    NAME           TYPE      ACTUAL-MTU  L2MTU  MAX-L2MTU  MAC-ADDRESS      
         0    ether1         ether           1500   1584      10218  48:8F:5A:05:51:79
         1 RS sfp-sfpplus1   ether           1500   1584      10218  48:8F:5A:05:51:69
        
        Flags: R=RUNNING (UP), S=SLAVE, X=DISABLED (DOWN)
        """
        result = {
            'name': interface_name,
            'full_name': interface_name,
            'status': 'unknown',
            'description': '',
            'flags': '',
            'raw_output': '',
        }
        
        # Try multiple commands
        commands = [
            "/interface print",
            "/interface print brief",
            "/interface ethernet print",
        ]
        
        output = ""
        for cmd in commands:
            output = self.execute_command(cmd, wait_time=3.0)
            if output and interface_name.lower() in output.lower():
                break
        
        result['raw_output'] = output
        
        if not output:
            return result
        
        # Clean ANSI escape codes
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        output = ansi_escape.sub('', output)
        
        # Parse output to find the specific interface
        lines = output.split('\n')
        current_comment = ''
        
        for line in lines:
            original_line = line
            line = line.strip()
            
            # Capture comment for next interface
            if line.startswith(';;;'):
                current_comment = line[3:].strip()
                continue
            
            # Skip header lines
            if line.startswith('Flags:') or line.startswith('Columns:'):
                continue
            if 'NAME' in line and ('TYPE' in line or 'MTU' in line):
                continue
            
            # Skip prompt/banner lines
            if line.endswith('>') or line.endswith('#') or '[admin@' in line:
                continue
            if 'MikroTik' in line or 'MMM' in line:
                continue
            
            # Interface lines start with a number
            match = re.match(r'^(\d+)\s+(.*)$', line)
            if not match:
                continue
            
            rest = match.group(2).strip()
            if not rest:
                continue
            
            parts = rest.split()
            if not parts:
                continue
            
            # Determine if first part is flags or name
            flags = ''
            name_idx = 0
            
            first_part = parts[0]
            
            # Check if first part looks like flags
            if len(first_part) <= 4 and all(c in 'RSDXrsdx' for c in first_part):
                flags = first_part.upper()
                name_idx = 1
            
            # Get interface name
            if name_idx >= len(parts):
                continue
            
            name = parts[name_idx]
            
            # Check if this is our interface (case insensitive)
            if name.lower() == interface_name.lower():
                result['flags'] = flags
                result['description'] = current_comment
                
                # Determine status from flags
                if 'R' in flags:
                    result['status'] = 'up'
                elif 'X' in flags:
                    result['status'] = 'down'
                elif 'S' in flags:
                    result['status'] = 'up'
                else:
                    result['status'] = 'down'
                
                logger.info(f"MikroTik interface {interface_name}: flags={flags}, status={result['status']}")
                return result
            
            # Reset comment
            current_comment = ''
        
        # Interface not found in output
        logger.warning(f"MikroTik interface {interface_name} not found in output")
        return result
    
    def get_optical_power(self, interface_name: str) -> Dict[str, Any]:
        """
        Get optical power readings for an interface.
        Tries multiple commands to find optical data.
        
        Args:
            interface_name: Name of the interface (or ONU for OLT)
            
        Returns:
            Dictionary with optical power data
        """
        full_interface = expand_interface_name(interface_name)
        
        # Get all possible optical commands
        commands = get_optical_commands(self.config.vendor, full_interface)
        
        # Also try with original name if different
        if full_interface != interface_name:
            commands.extend(get_optical_commands(self.config.vendor, interface_name))
        
        # Remove duplicates while preserving order
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
            logger.info(f"Trying optical command: {cmd}")
            output = self.execute_command(cmd, wait_time=3.0)
            
            if output:
                # Skip if error response
                error_indicators = ['Invalid', 'Error', 'Unrecognized', '% ', 
                                   'Unknown command', 'Incomplete command']
                if any(err in output for err in error_indicators):
                    logger.debug(f"Command returned error: {cmd}")
                    continue
                
                all_output += f"\n{'='*50}\n{cmd}\n{'='*50}\n{output}\n"
                
                # Try to parse optical data
                parsed = self.optical_parser.parse_optical_power(output)
                
                if parsed['found']:
                    result = parsed
                    successful_cmd = cmd
                    logger.info(f"Found optical data with: {cmd}")
                    break
        
        # If no result found, try parsing combined output
        if not result or not result.get('found'):
            result = self.optical_parser.parse_optical_power(all_output)
            if result.get('found'):
                successful_cmd = 'combined_output'
            else:
                successful_cmd = 'none_found'
        
        # Add metadata
        result['interface'] = interface_name
        result['full_interface'] = full_interface
        result['all_output'] = all_output
        result['command_used'] = successful_cmd
        result['commands_tried'] = len(unique_commands)
        
        return result
    
    def check_interface_with_optical(self, interface_name: str) -> Dict[str, Any]:
        """
        Get complete interface information including optical power.
        
        Args:
            interface_name: Name of the interface
            
        Returns:
            Dictionary with complete interface and optical data
        """
        # Get interface status
        interface_info = self.get_interface_status(interface_name)
        
        # Get optical power
        optical_info = self.get_optical_power(interface_name)
        
        # Combine results
        return {
            'name': interface_name,
            'full_name': interface_info.get('full_name', interface_name),
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
            'commands_tried': optical_info.get('commands_tried', 0),
            'raw_output': optical_info.get('all_output', ''),
            'found': optical_info.get('found', False),
        }
    
    def execute_custom_command(self, command: str, wait_time: float = 3.0) -> str:
        """
        Execute a custom command on the device.
        
        Args:
            command: Custom command to execute
            wait_time: Time to wait for response
            
        Returns:
            Command output
        """
        return self.execute_command(command, wait_time)
    
    def test_connection(self) -> Tuple[bool, str]:
        """
        Test the connection by executing a simple command.
        
        Returns:
            Tuple of (success, message)
        """
        if not self.connected:
            return False, "Not connected"
        
        # Try a simple command
        output = self.execute_command("", wait_time=1.0)
        if output is not None:
            return True, f"Connection OK via {self.connection_method}"
        return False, "Command execution failed"
    
    def disconnect(self):
        """Close the connection to the device."""
        try:
            if self.transport:
                self.transport.close()
                self.transport = None
            
            if self.shell:
                self.shell.close()
                self.shell = None
            
            if self.client:
                if self.config.protocol == Protocol.SSH:
                    self.client.close()
                elif self.config.protocol == Protocol.TELNET:
                    self.client.close()
                self.client = None
            
            self.connected = False
            logger.info(f"Disconnected from {self.config.host}")
            
        except Exception as e:
            logger.error(f"Disconnect error: {str(e)}")
    
    def __enter__(self):
        """Context manager entry - establish connection."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - close connection."""
        self.disconnect()
    
    def __del__(self):
        """Destructor - ensure connection is closed."""
        if self.connected:
            self.disconnect()


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def quick_check_device(host: str, username: str, password: str, 
                       vendor: str = "generic", protocol: str = "ssh",
                       port: int = None) -> Dict[str, Any]:
    """
    Quick utility function to check device connectivity.
    
    Args:
        host: Device IP/hostname
        username: Login username
        password: Login password
        vendor: Vendor type
        protocol: 'ssh' or 'telnet'
        port: Connection port (default: 22 for SSH, 23 for Telnet)
        
    Returns:
        Dictionary with connection result
    """
    config = ConnectionConfig(
        host=host,
        username=username,
        password=password,
        protocol=Protocol.SSH if protocol.lower() == 'ssh' else Protocol.TELNET,
        port=port,
        vendor=vendor
    )
    
    result = {
        'host': host,
        'connected': False,
        'method': None,
        'error': None,
    }
    
    try:
        with BotLinkMaster(config) as bot:
            result['connected'] = bot.connected
            result['method'] = bot.connection_method
    except Exception as e:
        result['error'] = str(e)
    
    return result


def get_interface_optical(host: str, username: str, password: str,
                          interface: str, vendor: str = "generic",
                          protocol: str = "ssh", port: int = None) -> Dict[str, Any]:
    """
    Quick utility function to get interface optical power.
    
    Args:
        host: Device IP/hostname
        username: Login username
        password: Login password
        interface: Interface name
        vendor: Vendor type
        protocol: 'ssh' or 'telnet'
        port: Connection port
        
    Returns:
        Dictionary with optical power data
    """
    config = ConnectionConfig(
        host=host,
        username=username,
        password=password,
        protocol=Protocol.SSH if protocol.lower() == 'ssh' else Protocol.TELNET,
        port=port,
        vendor=vendor
    )
    
    try:
        with BotLinkMaster(config) as bot:
            if not bot.connected:
                return {'error': 'Connection failed', 'found': False}
            return bot.check_interface_with_optical(interface)
    except Exception as e:
        return {'error': str(e), 'found': False}


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("BotLinkMaster v4.5.2 - Network Device Connection Module")
    print("=" * 60)
    print("\nFeatures:")
    print("  - SSH with legacy algorithm support (Huawei/ZTE fix)")
    print("  - Telnet support with custom port")
    print("  - Multi-vendor optical power parsing")
    print("  - Interface listing with special parsers")
    print("  - Port forwarding support")
    print("\nSupported Vendors:")
    from vendor_commands import get_supported_vendors
    vendors = get_supported_vendors()
    for i, v in enumerate(vendors, 1):
        print(f"  {i:2}. {v}")
    print("\nUsage:")
    print("  from botlinkmaster import BotLinkMaster, ConnectionConfig, Protocol")
    print("  config = ConnectionConfig(host='192.168.1.1', username='admin', ...")
    print("  with BotLinkMaster(config) as bot:")
    print("      interfaces = bot.get_interfaces()")
    print("      optical = bot.get_optical_power('Gi0/0')")