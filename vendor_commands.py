#!/usr/bin/env python3
"""
BotLinkMaster - Vendor Commands Reference
Complete command templates for network device vendors

Supported Vendors:
- Cisco IOS/IOS-XE
- Cisco NX-OS  
- Huawei VRP
- ZTE
- Juniper JunOS
- MikroTik RouterOS
- Nokia SR-OS
- HP/Aruba
- FiberHome
- DCN
- H3C Comware
- Ruijie
- BDCOM
- Raisecom
- FS (Fiberstore)
- Allied Telesis
- Datacom
- Generic

Author: BotLinkMaster
Version: 4.2
"""

import re
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum


class Vendor(Enum):
    """Supported vendors enumeration"""
    CISCO_IOS = "cisco_ios"
    CISCO_NXOS = "cisco_nxos"
    HUAWEI = "huawei"
    ZTE = "zte"
    JUNIPER = "juniper"
    MIKROTIK = "mikrotik"
    NOKIA = "nokia"
    HP_ARUBA = "hp_aruba"
    FIBERHOME = "fiberhome"
    DCN = "dcn"
    H3C = "h3c"
    RUIJIE = "ruijie"
    BDCOM = "bdcom"
    RAISECOM = "raisecom"
    FS = "fs"
    ALLIED = "allied"
    DATACOM = "datacom"
    GENERIC = "generic"


@dataclass
class VendorConfig:
    """Complete configuration for each vendor"""
    name: str
    disable_paging: str
    show_interface: str
    show_interface_brief: str
    # OPTICAL COMMANDS - KEY FOR REDAMAN
    show_optical_all: str
    show_optical_interface: str
    show_optical_detail: str
    alt_optical_commands: List[str] = field(default_factory=list)
    # Patterns for parsing
    rx_power_patterns: List[str] = field(default_factory=list)
    tx_power_patterns: List[str] = field(default_factory=list)
    temperature_pattern: str = ""
    voltage_pattern: str = ""
    status_pattern: str = ""
    notes: str = ""


# =============================================================================
# VENDOR CONFIGURATIONS - COMPLETE COMMAND REFERENCE
# =============================================================================

VENDOR_CONFIGS: Dict[str, VendorConfig] = {

    # =========================================================================
    # CISCO IOS / IOS-XE
    # =========================================================================
    Vendor.CISCO_IOS.value: VendorConfig(
        name="Cisco IOS/IOS-XE",
        disable_paging="terminal length 0",
        show_interface="show interface {interface}",
        show_interface_brief="show ip interface brief",
        show_optical_all="show interface transceiver",
        show_optical_interface="show interface {interface} transceiver",
        show_optical_detail="show interface {interface} transceiver detail",
        alt_optical_commands=[
            "show controllers {interface} phy",
            "show hw-module subslot {slot} transceiver {port} status",
        ],
        rx_power_patterns=[
            r"Receive\s+Power[:\s]+(-?\d+\.?\d*)\s*dBm",
            r"Rx\s+Power[:\s]+(-?\d+\.?\d*)\s*dBm",
            r"RX\s+Power[:\s]+(-?\d+\.?\d*)",
            r"Optical\s+Receive\s+Power[:\s]+(-?\d+\.?\d*)",
        ],
        tx_power_patterns=[
            r"Transmit\s+Power[:\s]+(-?\d+\.?\d*)\s*dBm",
            r"Tx\s+Power[:\s]+(-?\d+\.?\d*)\s*dBm",
            r"TX\s+Power[:\s]+(-?\d+\.?\d*)",
            r"Optical\s+Transmit\s+Power[:\s]+(-?\d+\.?\d*)",
        ],
        temperature_pattern=r"Temperature[:\s]+(-?\d+\.?\d*)",
        status_pattern=r"line protocol is (\w+)",
        notes="Standard Cisco IOS. Use 'show interface transceiver' for SFP info.",
    ),

    # =========================================================================
    # CISCO NX-OS (Nexus)
    # =========================================================================
    Vendor.CISCO_NXOS.value: VendorConfig(
        name="Cisco NX-OS",
        disable_paging="terminal length 0",
        show_interface="show interface {interface}",
        show_interface_brief="show interface brief",
        show_optical_all="show interface transceiver details",
        show_optical_interface="show interface {interface} transceiver details",
        show_optical_detail="show interface {interface} transceiver details",
        alt_optical_commands=[
            "show interface transceiver",
        ],
        rx_power_patterns=[
            r"Rx\s+Power[:\s]+(-?\d+\.?\d*)\s*dBm",
            r"Receive\s+Power[:\s]+(-?\d+\.?\d*)\s*dBm",
        ],
        tx_power_patterns=[
            r"Tx\s+Power[:\s]+(-?\d+\.?\d*)\s*dBm",
            r"Transmit\s+Power[:\s]+(-?\d+\.?\d*)\s*dBm",
        ],
        temperature_pattern=r"Temperature[:\s]+(-?\d+\.?\d*)\s*C",
        status_pattern=r"line protocol is (\w+)",
        notes="Nexus switches. Use 'details' for complete optical info.",
    ),

    # =========================================================================
    # HUAWEI VRP
    # =========================================================================
    Vendor.HUAWEI.value: VendorConfig(
        name="Huawei VRP",
        disable_paging="screen-length 0 temporary",
        show_interface="display interface {interface}",
        show_interface_brief="display interface brief",
        show_optical_all="display transceiver",
        show_optical_interface="display transceiver interface {interface}",
        show_optical_detail="display transceiver interface {interface} verbose",
        alt_optical_commands=[
            "display transceiver diagnosis interface {interface}",
            "display optical-module-info interface {interface}",
            "display interface {interface} transceiver",
            # OLT commands
            "display ont optical-info {port} all",
            "display ont info {port} {ont} all",
        ],
        rx_power_patterns=[
            r"RX\s+Power\s*\(dBm\)[:\s]+(-?\d+\.?\d*)",
            r"Rx\s+Power[:\s]+(-?\d+\.?\d*)",
            r"Current\s+RX\s+Power[:\s]+(-?\d+\.?\d*)",
            r"Receive\s+optical\s+power[:\s]+(-?\d+\.?\d*)",
        ],
        tx_power_patterns=[
            r"TX\s+Power\s*\(dBm\)[:\s]+(-?\d+\.?\d*)",
            r"Tx\s+Power[:\s]+(-?\d+\.?\d*)",
            r"Current\s+TX\s+Power[:\s]+(-?\d+\.?\d*)",
            r"Transmit\s+optical\s+power[:\s]+(-?\d+\.?\d*)",
        ],
        temperature_pattern=r"Temperature[:\s]+(-?\d+\.?\d*)",
        status_pattern=r"current state[:\s]*(\w+)",
        notes="Huawei routers/switches. OLT needs 'display ont optical-info'.",
    ),

    # =========================================================================
    # ZTE
    # =========================================================================
    Vendor.ZTE.value: VendorConfig(
        name="ZTE",
        disable_paging="terminal length 0",
        show_interface="show interface {interface}",
        show_interface_brief="show interface brief",
        show_optical_all="show transceiver detail",
        show_optical_interface="show transceiver interface {interface}",
        show_optical_detail="show transceiver interface {interface} detail",
        alt_optical_commands=[
            "show optic-module interface {interface}",
            "show optical-module-info {interface}",
            # OLT commands
            "show gpon onu detail-info {interface}",
            "show pon power onu {slot}/{port}",
            "show gpon remote-onu optical-info {interface}",
        ],
        rx_power_patterns=[
            r"Rx\s+Power[:\s]+(-?\d+\.?\d*)",
            r"RX\s+Power[:\s]+(-?\d+\.?\d*)",
            r"Receive\s+Power[:\s]+(-?\d+\.?\d*)",
        ],
        tx_power_patterns=[
            r"Tx\s+Power[:\s]+(-?\d+\.?\d*)",
            r"TX\s+Power[:\s]+(-?\d+\.?\d*)",
            r"Transmit\s+Power[:\s]+(-?\d+\.?\d*)",
        ],
        temperature_pattern=r"Temperature[:\s]+(-?\d+\.?\d*)",
        status_pattern=r"(?:line protocol|Link)\s+(?:is\s+)?(\w+)",
        notes="ZTE routers/switches/OLT.",
    ),

    # =========================================================================
    # JUNIPER JunOS
    # =========================================================================
    Vendor.JUNIPER.value: VendorConfig(
        name="Juniper JunOS",
        disable_paging="set cli screen-length 0",
        show_interface="show interfaces {interface}",
        show_interface_brief="show interfaces terse",
        show_optical_all="show interfaces diagnostics optics",
        show_optical_interface="show interfaces diagnostics optics {interface}",
        show_optical_detail="show interfaces diagnostics optics {interface} detail",
        alt_optical_commands=[
            "show interfaces {interface} extensive",
            "show chassis fpc pic-status",
        ],
        rx_power_patterns=[
            r"Laser\s+rx\s+power[:\s]+(-?\d+\.?\d*)\s*dBm",
            r"Receiver\s+signal[:\s]+(-?\d+\.?\d*)",
            r"Rx\s+Power[:\s]+(-?\d+\.?\d*)",
        ],
        tx_power_patterns=[
            r"Laser\s+output\s+power[:\s]+(-?\d+\.?\d*)\s*dBm",
            r"Module\s+transmit[:\s]+(-?\d+\.?\d*)",
            r"Tx\s+Power[:\s]+(-?\d+\.?\d*)",
        ],
        temperature_pattern=r"Module\s+temperature[:\s]+(-?\d+\.?\d*)",
        status_pattern=r"Physical link is (\w+)",
        notes="Juniper. Use 'diagnostics optics' for DOM info.",
    ),

    # =========================================================================
    # MIKROTIK RouterOS
    # =========================================================================
    Vendor.MIKROTIK.value: VendorConfig(
        name="MikroTik RouterOS",
        disable_paging="",
        show_interface="/interface ethernet print detail where name={interface}",
        show_interface_brief="/interface print",
        show_optical_all="/interface ethernet monitor [find] once",
        show_optical_interface="/interface ethernet monitor {interface} once",
        show_optical_detail="/interface ethernet monitor {interface} once",
        alt_optical_commands=[
            "/interface sfp-sfpplus monitor {interface} once",
            "/interface sfp monitor {interface} once",
        ],
        rx_power_patterns=[
            r"sfp-rx-power[:\s]+(-?\d+\.?\d*)",
            r"rx-power[:\s]+(-?\d+\.?\d*)",
        ],
        tx_power_patterns=[
            r"sfp-tx-power[:\s]+(-?\d+\.?\d*)",
            r"tx-power[:\s]+(-?\d+\.?\d*)",
        ],
        temperature_pattern=r"sfp-temperature[:\s]+(-?\d+\.?\d*)",
        voltage_pattern=r"sfp-supply-voltage[:\s]+(\d+\.?\d*)",
        status_pattern=r"status[:\s]+(\w+)",
        notes="MikroTik. Use '/interface ethernet monitor' for SFP stats.",
    ),

    # =========================================================================
    # NOKIA SR-OS
    # =========================================================================
    Vendor.NOKIA.value: VendorConfig(
        name="Nokia SR-OS",
        disable_paging="environment no more",
        show_interface="show port {interface}",
        show_interface_brief="show port",
        show_optical_all="show port detail",
        show_optical_interface="show port {interface} optical",
        show_optical_detail="show port {interface} detail",
        alt_optical_commands=[
            "show mda detail",
            "show port {interface} ddm",
        ],
        rx_power_patterns=[
            r"Rx\s+Optical\s+Pwr[:\s]+(-?\d+\.?\d*)",
            r"Input\s+Power[:\s]+(-?\d+\.?\d*)",
        ],
        tx_power_patterns=[
            r"Tx\s+Optical\s+Pwr[:\s]+(-?\d+\.?\d*)",
            r"Output\s+Power[:\s]+(-?\d+\.?\d*)",
        ],
        temperature_pattern=r"Temperature[:\s]+(-?\d+\.?\d*)",
        status_pattern=r"Oper\s+State[:\s]+(\w+)",
        notes="Nokia/Alcatel-Lucent SR routers.",
    ),

    # =========================================================================
    # HP / ARUBA
    # =========================================================================
    Vendor.HP_ARUBA.value: VendorConfig(
        name="HP/Aruba Switch",
        disable_paging="no page",
        show_interface="show interface {interface}",
        show_interface_brief="show interface brief",
        show_optical_all="show interface transceiver",
        show_optical_interface="show interface {interface} transceiver",
        show_optical_detail="show interface {interface} transceiver detail",
        alt_optical_commands=[
            "show tech transceiver",
        ],
        rx_power_patterns=[
            r"Rx\s+Power[:\s]+(-?\d+\.?\d*)",
            r"Receive\s+Power[:\s]+(-?\d+\.?\d*)",
        ],
        tx_power_patterns=[
            r"Tx\s+Power[:\s]+(-?\d+\.?\d*)",
            r"Transmit\s+Power[:\s]+(-?\d+\.?\d*)",
        ],
        temperature_pattern=r"Temperature[:\s]+(-?\d+\.?\d*)",
        status_pattern=r"Link[:\s]+(\w+)",
        notes="HP ProCurve and Aruba switches.",
    ),

    # =========================================================================
    # FIBERHOME
    # =========================================================================
    Vendor.FIBERHOME.value: VendorConfig(
        name="FiberHome",
        disable_paging="terminal length 0",
        show_interface="show interface {interface}",
        show_interface_brief="show interface brief",
        show_optical_all="show transceiver detail",
        show_optical_interface="show transceiver interface {interface}",
        show_optical_detail="show transceiver interface {interface} detail",
        alt_optical_commands=[
            "show optical-module interface {interface}",
            # OLT
            "show onu optical-transceiver-diagnosis {interface}",
        ],
        rx_power_patterns=[
            r"Rx\s+Power[:\s]+(-?\d+\.?\d*)",
            r"RX\s+Power[:\s]+(-?\d+\.?\d*)",
        ],
        tx_power_patterns=[
            r"Tx\s+Power[:\s]+(-?\d+\.?\d*)",
            r"TX\s+Power[:\s]+(-?\d+\.?\d*)",
        ],
        temperature_pattern=r"Temperature[:\s]+(-?\d+\.?\d*)",
        status_pattern=r"Status[:\s]+(\w+)",
        notes="FiberHome switches and OLT.",
    ),

    # =========================================================================
    # DCN
    # =========================================================================
    Vendor.DCN.value: VendorConfig(
        name="DCN",
        disable_paging="terminal length 0",
        show_interface="show interface {interface}",
        show_interface_brief="show interface status",
        show_optical_all="show transceiver",
        show_optical_interface="show transceiver interface {interface}",
        show_optical_detail="show transceiver interface {interface} detail",
        alt_optical_commands=[
            "show fiber-port optical-transceiver interface {interface}",
        ],
        rx_power_patterns=[
            r"Rx\s+Power[:\s]+(-?\d+\.?\d*)",
            r"RX\s+Power[:\s]+(-?\d+\.?\d*)",
        ],
        tx_power_patterns=[
            r"Tx\s+Power[:\s]+(-?\d+\.?\d*)",
            r"TX\s+Power[:\s]+(-?\d+\.?\d*)",
        ],
        status_pattern=r"(?:link|status)[:\s]+(\w+)",
        notes="DCN switches.",
    ),

    # =========================================================================
    # H3C Comware
    # =========================================================================
    Vendor.H3C.value: VendorConfig(
        name="H3C Comware",
        disable_paging="screen-length disable",
        show_interface="display interface {interface}",
        show_interface_brief="display interface brief",
        show_optical_all="display transceiver",
        show_optical_interface="display transceiver interface {interface}",
        show_optical_detail="display transceiver interface {interface} verbose",
        alt_optical_commands=[
            "display transceiver diagnosis interface {interface}",
        ],
        rx_power_patterns=[
            r"RX\s+Power\s*\(dBm\)[:\s]+(-?\d+\.?\d*)",
            r"Rx\s+Power[:\s]+(-?\d+\.?\d*)",
        ],
        tx_power_patterns=[
            r"TX\s+Power\s*\(dBm\)[:\s]+(-?\d+\.?\d*)",
            r"Tx\s+Power[:\s]+(-?\d+\.?\d*)",
        ],
        temperature_pattern=r"Temperature[:\s]+(-?\d+\.?\d*)",
        status_pattern=r"current state[:\s]+(\w+)",
        notes="H3C uses 'display' commands like Huawei.",
    ),

    # =========================================================================
    # RUIJIE
    # =========================================================================
    Vendor.RUIJIE.value: VendorConfig(
        name="Ruijie",
        disable_paging="terminal length 0",
        show_interface="show interface {interface}",
        show_interface_brief="show interface status",
        show_optical_all="show transceiver",
        show_optical_interface="show transceiver interface {interface}",
        show_optical_detail="show transceiver detail interface {interface}",
        alt_optical_commands=[
            "show interface {interface} transceiver",
        ],
        rx_power_patterns=[
            r"Rx\s+Power[:\s]+(-?\d+\.?\d*)",
            r"RX\s+Power[:\s]+(-?\d+\.?\d*)",
        ],
        tx_power_patterns=[
            r"Tx\s+Power[:\s]+(-?\d+\.?\d*)",
            r"TX\s+Power[:\s]+(-?\d+\.?\d*)",
        ],
        temperature_pattern=r"Temperature[:\s]+(-?\d+\.?\d*)",
        status_pattern=r"line protocol is (\w+)",
        notes="Ruijie switches. Cisco-like syntax.",
    ),

    # =========================================================================
    # BDCOM
    # =========================================================================
    Vendor.BDCOM.value: VendorConfig(
        name="BDCOM",
        disable_paging="terminal length 0",
        show_interface="show interface {interface}",
        show_interface_brief="show interface brief",
        show_optical_all="show transceiver",
        show_optical_interface="show transceiver interface {interface}",
        show_optical_detail="show transceiver interface {interface} detail",
        alt_optical_commands=[
            "show fiber-port transceiver-information interface {interface}",
            # OLT
            "show epon optical-transceiver-diagnosis interface {interface}",
            "show epon onu-info interface {interface}",
        ],
        rx_power_patterns=[
            r"Rx\s+Power[:\s]+(-?\d+\.?\d*)",
            r"RX[:\s]+(-?\d+\.?\d*)",
        ],
        tx_power_patterns=[
            r"Tx\s+Power[:\s]+(-?\d+\.?\d*)",
            r"TX[:\s]+(-?\d+\.?\d*)",
        ],
        status_pattern=r"(?:Status|Link)[:\s]+(\w+)",
        notes="BDCOM switches/OLT.",
    ),

    # =========================================================================
    # RAISECOM
    # =========================================================================
    Vendor.RAISECOM.value: VendorConfig(
        name="Raisecom",
        disable_paging="terminal length 0",
        show_interface="show interface {interface}",
        show_interface_brief="show interface brief",
        show_optical_all="show transceiver",
        show_optical_interface="show transceiver {interface}",
        show_optical_detail="show transceiver {interface} detail",
        alt_optical_commands=[
            "show optical-module {interface}",
        ],
        rx_power_patterns=[
            r"Rx\s*Power[:\s]+(-?\d+\.?\d*)",
            r"RX[:\s]+(-?\d+\.?\d*)",
        ],
        tx_power_patterns=[
            r"Tx\s*Power[:\s]+(-?\d+\.?\d*)",
            r"TX[:\s]+(-?\d+\.?\d*)",
        ],
        status_pattern=r"Status[:\s]+(\w+)",
        notes="Raisecom equipment.",
    ),

    # =========================================================================
    # FS (Fiberstore)
    # =========================================================================
    Vendor.FS.value: VendorConfig(
        name="FS.COM",
        disable_paging="terminal length 0",
        show_interface="show interface {interface}",
        show_interface_brief="show interface status",
        show_optical_all="show transceiver",
        show_optical_interface="show transceiver interface {interface}",
        show_optical_detail="show transceiver interface {interface}",
        alt_optical_commands=[
            "show interface transceiver {interface}",
        ],
        rx_power_patterns=[
            r"Rx\s+Power[:\s]+(-?\d+\.?\d*)",
            r"RxPower[:\s]+(-?\d+\.?\d*)",
        ],
        tx_power_patterns=[
            r"Tx\s+Power[:\s]+(-?\d+\.?\d*)",
            r"TxPower[:\s]+(-?\d+\.?\d*)",
        ],
        status_pattern=r"Status[:\s]+(\w+)",
        notes="FS.COM switches. Cisco-like syntax.",
    ),

    # =========================================================================
    # ALLIED TELESIS
    # =========================================================================
    Vendor.ALLIED.value: VendorConfig(
        name="Allied Telesis",
        disable_paging="terminal length 0",
        show_interface="show interface {interface}",
        show_interface_brief="show interface brief",
        show_optical_all="show system pluggable",
        show_optical_interface="show system pluggable {interface}",
        show_optical_detail="show system pluggable {interface} detail",
        alt_optical_commands=[
            "show interface {interface} transceiver",
        ],
        rx_power_patterns=[
            r"Rx\s+Power[:\s]+(-?\d+\.?\d*)",
            r"RX\s+Power[:\s]+(-?\d+\.?\d*)",
        ],
        tx_power_patterns=[
            r"Tx\s+Power[:\s]+(-?\d+\.?\d*)",
            r"TX\s+Power[:\s]+(-?\d+\.?\d*)",
        ],
        status_pattern=r"Status[:\s]+(\w+)",
        notes="Allied Telesis switches.",
    ),

    # =========================================================================
    # DATACOM
    # =========================================================================
    Vendor.DATACOM.value: VendorConfig(
        name="Datacom",
        disable_paging="terminal length 0",
        show_interface="show interface {interface}",
        show_interface_brief="show interface status",
        show_optical_all="show interface transceiver",
        show_optical_interface="show interface {interface} transceiver",
        show_optical_detail="show interface {interface} transceiver detail",
        alt_optical_commands=[],
        rx_power_patterns=[
            r"Rx\s+Power[:\s]+(-?\d+\.?\d*)",
            r"RX\s+Power[:\s]+(-?\d+\.?\d*)",
        ],
        tx_power_patterns=[
            r"Tx\s+Power[:\s]+(-?\d+\.?\d*)",
            r"TX\s+Power[:\s]+(-?\d+\.?\d*)",
        ],
        status_pattern=r"Status[:\s]+(\w+)",
        notes="Datacom switches.",
    ),

    # =========================================================================
    # GENERIC (Default)
    # =========================================================================
    Vendor.GENERIC.value: VendorConfig(
        name="Generic",
        disable_paging="terminal length 0",
        show_interface="show interface {interface}",
        show_interface_brief="show interface brief",
        show_optical_all="show transceiver",
        show_optical_interface="show transceiver interface {interface}",
        show_optical_detail="show transceiver interface {interface}",
        alt_optical_commands=[
            "show interface transceiver",
            "show interface {interface} transceiver",
            "display transceiver interface {interface}",
            "display transceiver",
        ],
        rx_power_patterns=[
            r"(?:Rx|RX|Receive)\s*(?:Power|power)[:\s]+(-?\d+\.?\d*)",
            r"(?:Rx|RX)[:\s]+(-?\d+\.?\d*)\s*dBm",
        ],
        tx_power_patterns=[
            r"(?:Tx|TX|Transmit)\s*(?:Power|power)[:\s]+(-?\d+\.?\d*)",
            r"(?:Tx|TX)[:\s]+(-?\d+\.?\d*)\s*dBm",
        ],
        temperature_pattern=r"Temperature[:\s]+(-?\d+\.?\d*)",
        status_pattern=r"(?:line protocol|status|state|link)\s+(?:is\s+)?(\w+)",
        notes="Generic fallback. Tries multiple command patterns.",
    ),
}


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_vendor_config(vendor: str) -> VendorConfig:
    """Get vendor configuration by name"""
    vendor_lower = vendor.lower().strip().replace(" ", "_").replace("-", "_")
    
    if vendor_lower in VENDOR_CONFIGS:
        return VENDOR_CONFIGS[vendor_lower]
    
    for key, config in VENDOR_CONFIGS.items():
        if vendor_lower in key or key in vendor_lower:
            return config
    
    return VENDOR_CONFIGS[Vendor.GENERIC.value]


def get_supported_vendors() -> List[str]:
    """Get list of all supported vendors"""
    return [v.value for v in Vendor]


def get_vendor_display_name(vendor: str) -> str:
    """Get display name for vendor"""
    config = get_vendor_config(vendor)
    return config.name


def get_optical_commands(vendor: str, interface: str) -> List[str]:
    """Get all possible optical commands for vendor/interface"""
    config = get_vendor_config(vendor)
    commands = [
        config.show_optical_interface.format(interface=interface),
        config.show_optical_detail.format(interface=interface),
    ]
    for alt_cmd in config.alt_optical_commands:
        if '{interface}' in alt_cmd:
            commands.append(alt_cmd.format(interface=interface))
    return commands


# =============================================================================
# OPTICAL POWER PARSER
# =============================================================================

class OpticalParser:
    """Parser for optical power readings"""
    
    def __init__(self, vendor: str = "generic"):
        self.vendor = vendor
        self.config = get_vendor_config(vendor)
    
    def parse_optical_power(self, output: str) -> Dict[str, Any]:
        """Parse optical power from command output"""
        result = {
            'rx_power': None,
            'tx_power': None,
            'rx_power_dbm': 'N/A',
            'tx_power_dbm': 'N/A',
            'temperature': None,
            'voltage': None,
            'signal_status': 'unknown',
            'raw_output': output,
            'found': False,
        }
        
        if not output:
            return result
        
        # Try all RX patterns
        for pattern in self.config.rx_power_patterns:
            match = re.search(pattern, output, re.IGNORECASE | re.MULTILINE)
            if match:
                try:
                    result['rx_power'] = float(match.group(1))
                    result['rx_power_dbm'] = f"{result['rx_power']:.2f} dBm"
                    result['found'] = True
                    break
                except (ValueError, IndexError):
                    continue
        
        # Try all TX patterns
        for pattern in self.config.tx_power_patterns:
            match = re.search(pattern, output, re.IGNORECASE | re.MULTILINE)
            if match:
                try:
                    result['tx_power'] = float(match.group(1))
                    result['tx_power_dbm'] = f"{result['tx_power']:.2f} dBm"
                    result['found'] = True
                    break
                except (ValueError, IndexError):
                    continue
        
        # Fallback: find any dBm values
        if not result['found']:
            dbm_matches = re.findall(r'(-?\d+\.?\d*)\s*dBm', output, re.IGNORECASE)
            if len(dbm_matches) >= 2:
                try:
                    result['tx_power'] = float(dbm_matches[0])
                    result['rx_power'] = float(dbm_matches[1])
                    result['tx_power_dbm'] = f"{result['tx_power']:.2f} dBm"
                    result['rx_power_dbm'] = f"{result['rx_power']:.2f} dBm"
                    result['found'] = True
                except ValueError:
                    pass
        
        # Temperature
        if self.config.temperature_pattern:
            temp_match = re.search(self.config.temperature_pattern, output, re.IGNORECASE)
            if temp_match:
                try:
                    result['temperature'] = float(temp_match.group(1))
                except (ValueError, IndexError):
                    pass
        
        # Signal status based on RX power
        if result['rx_power'] is not None:
            rx = result['rx_power']
            if rx >= -8:
                result['signal_status'] = 'excellent'
            elif rx >= -14:
                result['signal_status'] = 'good'
            elif rx >= -20:
                result['signal_status'] = 'fair'
            elif rx >= -25:
                result['signal_status'] = 'weak'
            else:
                result['signal_status'] = 'critical'
        
        return result


# =============================================================================
# INTERFACE NAME ALIASES
# =============================================================================

INTERFACE_ALIASES = {
    'gi': 'GigabitEthernet',
    'gig': 'GigabitEthernet',
    'fa': 'FastEthernet',
    'te': 'TenGigabitEthernet',
    'tengig': 'TenGigabitEthernet',
    'eth': 'Ethernet',
    'ge': 'GigabitEthernet',
    'xge': 'XGigabitEthernet',
    '10ge': '10GE',
    '40ge': '40GE',
    '100ge': '100GE',
}


def expand_interface_name(short_name: str) -> str:
    """Expand short interface name to full name"""
    for full in INTERFACE_ALIASES.values():
        if short_name.lower().startswith(full.lower()):
            return short_name
    
    for alias, full in INTERFACE_ALIASES.items():
        if short_name.lower().startswith(alias):
            number_part = short_name[len(alias):]
            return f"{full}{number_part}"
    
    return short_name


def print_vendor_quick_reference():
    """Print quick reference for vendors"""
    print("\n" + "="*70)
    print("VENDOR OPTICAL COMMANDS QUICK REFERENCE")
    print("="*70)
    
    for vendor_key, config in VENDOR_CONFIGS.items():
        print(f"\n[{config.name}] vendor: {vendor_key}")
        print(f"  Optical: {config.show_optical_interface}")
        if config.alt_optical_commands:
            print(f"  Alt: {config.alt_optical_commands[0]}")


if __name__ == "__main__":
    print_vendor_quick_reference()