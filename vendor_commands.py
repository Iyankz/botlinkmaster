#!/usr/bin/env python3
"""
BotLinkMaster - Vendor Commands v4.8.4
Multi-vendor support for routers and switches

CHANGELOG v4.8.4:
- FIX: Comment dengan karakter khusus {}, [] menyebabkan interface hilang
- FIX: sfp-sfpplus16 tidak terbaca karena comment "Cust:xxxx{cvlan}[speed]"
- IMPROVED: Better comment/description handling
- IMPROVED: More robust interface line detection

CHANGELOG v4.8.3:
- FIX: Wait for prompt before sending commands

CHANGELOG v4.8.2:
- FIX: MikroTik last interface not parsed (sfp-sfpplus16 missing)

Note: OLT support will be available in v5.0.0

Author: BotLinkMaster
Version: 4.8.4
"""

import re
from typing import Dict, Any, List
from dataclasses import dataclass, field
from enum import Enum


class Vendor(Enum):
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
    name: str
    disable_paging: str
    show_interface: str
    show_interface_brief: str
    show_interface_status: str
    show_interface_description: str
    show_optical_all: str
    show_optical_interface: str
    show_optical_detail: str
    alt_optical_commands: List[str] = field(default_factory=list)
    alt_interface_commands: List[str] = field(default_factory=list)
    rx_power_patterns: List[str] = field(default_factory=list)
    tx_power_patterns: List[str] = field(default_factory=list)
    status_up_patterns: List[str] = field(default_factory=list)
    status_down_patterns: List[str] = field(default_factory=list)
    description_pattern: str = ""
    interface_parser: str = "default"
    notes: str = ""


VENDOR_CONFIGS: Dict[str, VendorConfig] = {
    # ==========================================================================
    # CISCO IOS
    # ==========================================================================
    Vendor.CISCO_IOS.value: VendorConfig(
        name="Cisco IOS/IOS-XE",
        disable_paging="terminal length 0",
        show_interface="show interface {interface}",
        show_interface_brief="show ip interface brief",
        show_interface_status="show interface status",
        show_interface_description="show interface description",
        show_optical_all="show interface transceiver",
        show_optical_interface="show interface {interface} transceiver",
        show_optical_detail="show interface {interface} transceiver detail",
        rx_power_patterns=[
            r"Receive\s+Power[:\s]+(-?\d+\.?\d*)\s*dBm",
            r"Rx\s+Power[:\s]+(-?\d+\.?\d*)",
            r"RX\s+power[:\s]+(-?\d+\.?\d*)",
        ],
        tx_power_patterns=[
            r"Transmit\s+Power[:\s]+(-?\d+\.?\d*)\s*dBm",
            r"Tx\s+Power[:\s]+(-?\d+\.?\d*)",
            r"TX\s+power[:\s]+(-?\d+\.?\d*)",
        ],
        status_up_patterns=[r"line protocol is up", r"is up"],
        status_down_patterns=[r"line protocol is down", r"is down", r"administratively down"],
        description_pattern=r"Description[:\s]+(.+?)(?:\n|$)",
        notes="Cisco IOS routers and switches",
    ),
    
    # ==========================================================================
    # CISCO NX-OS
    # ==========================================================================
    Vendor.CISCO_NXOS.value: VendorConfig(
        name="Cisco NX-OS",
        disable_paging="terminal length 0",
        show_interface="show interface {interface}",
        show_interface_brief="show interface status",
        show_interface_status="show interface status",
        show_interface_description="show interface description",
        show_optical_all="show interface transceiver details",
        show_optical_interface="show interface {interface} transceiver details",
        show_optical_detail="show interface {interface} transceiver details",
        alt_interface_commands=[
            "show interface status",
            "show interface brief",
            "show interface description",
        ],
        interface_parser="cisco_nxos",
        rx_power_patterns=[
            r"Rx\s+Power[:\s]+(-?\d+\.?\d*)\s*dBm",
            r"Receive\s+Power[:\s]+(-?\d+\.?\d*)",
            r"RX[:\s]+(-?\d+\.?\d*)\s*dBm",
        ],
        tx_power_patterns=[
            r"Tx\s+Power[:\s]+(-?\d+\.?\d*)\s*dBm",
            r"Transmit\s+Power[:\s]+(-?\d+\.?\d*)",
            r"TX[:\s]+(-?\d+\.?\d*)\s*dBm",
        ],
        status_up_patterns=[
            r"line protocol is up",
            r"\bconnected\b",
            r"\bup\b",
        ],
        status_down_patterns=[
            r"line protocol is down",
            r"\bnotconnect\b",
            r"\bdisabled\b",
            r"\bdown\b",
            r"\bsfp not inserted\b",
        ],
        description_pattern=r"Description[:\s]+(.+?)(?:\n|$)",
        notes="Cisco Nexus switches",
    ),
    
    # ==========================================================================
    # HUAWEI VRP
    # ==========================================================================
    Vendor.HUAWEI.value: VendorConfig(
        name="Huawei VRP",
        disable_paging="screen-length 0 temporary",
        show_interface="display interface {interface}",
        show_interface_brief="display interface brief",
        show_interface_status="display interface brief",
        show_interface_description="display interface description",
        show_optical_all="display transceiver",
        show_optical_interface="display transceiver interface {interface}",
        show_optical_detail="display interface {interface} transceiver verbose",
        alt_optical_commands=[
            "display interface {interface} transceiver verbose",
            "display transceiver interface {interface} verbose",
            "display transceiver diagnosis interface {interface}",
            "display transceiver interface {interface}",
        ],
        rx_power_patterns=[
            r"RX\s*power\s*\(dBm\)[:\s\|]+(-?\d+\.?\d*)",
            r"RxPower\s*\(dBm\)\s*\|?\s*(-?\d+\.?\d*)",
            r"Rx\s*Power\s*\(dBm\)[:\s]+(-?\d+\.?\d*)",
            r"Current\s+RX\s+Power\s*\(dBm\)[:\s]+(-?\d+\.?\d*)",
            r"RX\s+Power[:\s]+(-?\d+\.?\d*)",
            r"Rx\s+optical\s+power[:\s]+(-?\d+\.?\d*)",
            r"RX[:\s]+(-?\d+\.?\d*)\s*dBm",
        ],
        tx_power_patterns=[
            r"TX\s*power\s*\(dBm\)[:\s\|]+(-?\d+\.?\d*)",
            r"TxPower\s*\(dBm\)\s*\|?\s*(-?\d+\.?\d*)",
            r"Tx\s*Power\s*\(dBm\)[:\s]+(-?\d+\.?\d*)",
            r"Current\s+TX\s+Power\s*\(dBm\)[:\s]+(-?\d+\.?\d*)",
            r"TX\s+Power[:\s]+(-?\d+\.?\d*)",
            r"Tx\s+optical\s+power[:\s]+(-?\d+\.?\d*)",
            r"TX[:\s]+(-?\d+\.?\d*)\s*dBm",
        ],
        status_up_patterns=[r"current state[:\s]*UP", r"Physical[:\s]+UP", r"is\s+UP"],
        status_down_patterns=[r"current state[:\s]*DOWN", r"Physical[:\s]+DOWN", r"is\s+DOWN"],
        description_pattern=r"Description[:\s]+(.+?)(?:\n|$)",
        notes="Huawei routers and switches",
    ),
    
    # ==========================================================================
    # ZTE Switch/Router
    # ==========================================================================
    Vendor.ZTE.value: VendorConfig(
        name="ZTE",
        disable_paging="terminal length 0",
        show_interface="show interface {interface}",
        show_interface_brief="show interface brief",
        show_interface_status="show interface status",
        show_interface_description="show interface description",
        show_optical_all="show transceiver detail",
        show_optical_interface="show transceiver interface {interface}",
        show_optical_detail="show transceiver interface {interface} detail",
        rx_power_patterns=[r"Rx\s+Power[:\s]+(-?\d+\.?\d*)", r"RX[:\s]+(-?\d+\.?\d*)"],
        tx_power_patterns=[r"Tx\s+Power[:\s]+(-?\d+\.?\d*)", r"TX[:\s]+(-?\d+\.?\d*)"],
        status_up_patterns=[r"line protocol is up"],
        status_down_patterns=[r"line protocol is down"],
        description_pattern=r"Description[:\s]+(.+?)(?:\n|$)",
        notes="ZTE routers and switches",
    ),
    
    # ==========================================================================
    # JUNIPER JunOS
    # ==========================================================================
    Vendor.JUNIPER.value: VendorConfig(
        name="Juniper JunOS",
        disable_paging="set cli screen-length 0",
        show_interface="show interfaces {interface}",
        show_interface_brief="show interfaces terse",
        show_interface_status="show interfaces terse",
        show_interface_description="show interfaces descriptions",
        show_optical_all="show interfaces diagnostics optics",
        show_optical_interface="show interfaces diagnostics optics {interface}",
        show_optical_detail="show interfaces {interface} extensive",
        rx_power_patterns=[
            r"Laser\s+rx\s+power[:\s]+(-?\d+\.?\d*)\s*dBm",
            r"Receiver\s+signal\s+average\s+optical\s+power[:\s]+(-?\d+\.?\d*)",
        ],
        tx_power_patterns=[
            r"Laser\s+output\s+power[:\s]+(-?\d+\.?\d*)\s*dBm",
        ],
        status_up_patterns=[r"Physical link is Up"],
        status_down_patterns=[r"Physical link is Down"],
        description_pattern=r"Description[:\s]+(.+?)(?:\n|$)",
        notes="Juniper routers and switches",
    ),
    
    # ==========================================================================
    # MIKROTIK RouterOS - FIXED
    # ==========================================================================
    Vendor.MIKROTIK.value: VendorConfig(
        name="MikroTik RouterOS",
        disable_paging="",
        show_interface="/interface print detail where name={interface}",
        show_interface_brief="/interface print brief",
        show_interface_status="/interface print brief",
        show_interface_description="/interface print brief",
        show_optical_all="/interface ethernet monitor [find] once",
        show_optical_interface="interface/ethernet/monitor {interface} once",
        show_optical_detail="interface/ethernet/monitor {interface} once",
        alt_optical_commands=[
            "/interface ethernet monitor {interface}",
            "interface/ethernet/monitor {interface} once",
            "/interface ethernet monitor {interface} once",
        ],
        alt_interface_commands=[
            "/interface print brief",
            "/interface print",
        ],
        interface_parser="mikrotik",
        rx_power_patterns=[
            r"sfp-rx-power[:\s]+(-?\d+\.?\d*)\s*dBm",
            r"sfp-rx-power[:\s]+(-?\d+\.?\d*)",
        ],
        tx_power_patterns=[
            r"sfp-tx-power[:\s]+(-?\d+\.?\d*)\s*dBm",
            r"sfp-tx-power[:\s]+(-?\d+\.?\d*)",
        ],
        status_up_patterns=[
            r"status[:\s]+link-ok",
            r"running=yes",
        ],
        status_down_patterns=[
            r"status[:\s]+no-link",
            r"running=no",
            r"disabled=yes",
        ],
        description_pattern=r"comment[:\s]+(.+?)(?:\n|$)",
        notes="MikroTik RouterOS - Flags: R=RUNNING, S=SLAVE, X=DISABLED",
    ),
    
    # ==========================================================================
    # NOKIA SR-OS
    # ==========================================================================
    Vendor.NOKIA.value: VendorConfig(
        name="Nokia SR-OS",
        disable_paging="environment no more",
        show_interface="show port {interface}",
        show_interface_brief="show port",
        show_interface_status="show port {interface}",
        show_interface_description="show port description",
        show_optical_all="show port detail",
        show_optical_interface="show port {interface} optical",
        show_optical_detail="show port {interface} detail",
        rx_power_patterns=[r"Rx\s+Optical\s+Pwr[:\s]+(-?\d+\.?\d*)"],
        tx_power_patterns=[r"Tx\s+Optical\s+Pwr[:\s]+(-?\d+\.?\d*)"],
        status_up_patterns=[r"Oper\s+State[:\s]+Up"],
        status_down_patterns=[r"Oper\s+State[:\s]+Down"],
        description_pattern=r"Description[:\s]+(.+?)(?:\n|$)",
        notes="Nokia SR-OS routers",
    ),
    
    # ==========================================================================
    # HP/ARUBA
    # ==========================================================================
    Vendor.HP_ARUBA.value: VendorConfig(
        name="HP/Aruba Switch",
        disable_paging="no page",
        show_interface="show interface {interface}",
        show_interface_brief="show interface brief",
        show_interface_status="show interface status",
        show_interface_description="show interface {interface}",
        show_optical_all="show interface transceiver",
        show_optical_interface="show interface {interface} transceiver",
        show_optical_detail="show interface {interface} transceiver detail",
        rx_power_patterns=[r"Rx\s+Power[:\s]+(-?\d+\.?\d*)"],
        tx_power_patterns=[r"Tx\s+Power[:\s]+(-?\d+\.?\d*)"],
        status_up_patterns=[r"Status.+?Up", r"Link[:\s]+Up"],
        status_down_patterns=[r"Status.+?Down", r"Link[:\s]+Down"],
        description_pattern=r"Name[:\s]+(.+?)(?:\n|$)",
        notes="HP ProCurve and Aruba switches",
    ),
    
    # ==========================================================================
    # FIBERHOME Switch
    # ==========================================================================
    Vendor.FIBERHOME.value: VendorConfig(
        name="FiberHome",
        disable_paging="terminal length 0",
        show_interface="show interface {interface}",
        show_interface_brief="show interface brief",
        show_interface_status="show interface status",
        show_interface_description="show interface description",
        show_optical_all="show transceiver detail",
        show_optical_interface="show transceiver interface {interface}",
        show_optical_detail="show transceiver interface {interface} detail",
        rx_power_patterns=[r"Rx\s+Power[:\s]+(-?\d+\.?\d*)"],
        tx_power_patterns=[r"Tx\s+Power[:\s]+(-?\d+\.?\d*)"],
        status_up_patterns=[r"Link[:\s]+UP"],
        status_down_patterns=[r"Link[:\s]+DOWN"],
        description_pattern=r"Description[:\s]+(.+?)(?:\n|$)",
        notes="FiberHome switches",
    ),
    
    # ==========================================================================
    # DCN
    # ==========================================================================
    Vendor.DCN.value: VendorConfig(
        name="DCN",
        disable_paging="terminal length 0",
        show_interface="show interface {interface}",
        show_interface_brief="show interface status",
        show_interface_status="show interface status",
        show_interface_description="show interface description",
        show_optical_all="show transceiver",
        show_optical_interface="show transceiver interface {interface}",
        show_optical_detail="show transceiver interface {interface} detail",
        rx_power_patterns=[r"Rx\s+Power[:\s]+(-?\d+\.?\d*)"],
        tx_power_patterns=[r"Tx\s+Power[:\s]+(-?\d+\.?\d*)"],
        status_up_patterns=[r"Link[:\s]+UP"],
        status_down_patterns=[r"Link[:\s]+DOWN"],
        description_pattern=r"Description[:\s]+(.+?)(?:\n|$)",
        notes="DCN switches",
    ),
    
    # ==========================================================================
    # H3C Comware
    # ==========================================================================
    Vendor.H3C.value: VendorConfig(
        name="H3C Comware",
        disable_paging="screen-length disable",
        show_interface="display interface {interface}",
        show_interface_brief="display interface brief",
        show_interface_status="display interface brief",
        show_interface_description="display interface description",
        show_optical_all="display transceiver",
        show_optical_interface="display transceiver interface {interface}",
        show_optical_detail="display transceiver interface {interface} verbose",
        rx_power_patterns=[
            r"RX\s+Power[:\s]+(-?\d+\.?\d*)",
            r"Rx\s*power\s*\(dBm\)[:\s]+(-?\d+\.?\d*)",
        ],
        tx_power_patterns=[
            r"TX\s+Power[:\s]+(-?\d+\.?\d*)",
            r"Tx\s*power\s*\(dBm\)[:\s]+(-?\d+\.?\d*)",
        ],
        status_up_patterns=[r"current state[:\s]+UP"],
        status_down_patterns=[r"current state[:\s]+DOWN"],
        description_pattern=r"Description[:\s]+(.+?)(?:\n|$)",
        notes="H3C Comware switches",
    ),
    
    # ==========================================================================
    # RUIJIE
    # ==========================================================================
    Vendor.RUIJIE.value: VendorConfig(
        name="Ruijie",
        disable_paging="terminal length 0",
        show_interface="show interface {interface}",
        show_interface_brief="show interface status",
        show_interface_status="show interface status",
        show_interface_description="show interface description",
        show_optical_all="show transceiver",
        show_optical_interface="show transceiver interface {interface}",
        show_optical_detail="show transceiver detail interface {interface}",
        rx_power_patterns=[r"Rx\s+Power[:\s]+(-?\d+\.?\d*)"],
        tx_power_patterns=[r"Tx\s+Power[:\s]+(-?\d+\.?\d*)"],
        status_up_patterns=[r"line protocol is up"],
        status_down_patterns=[r"line protocol is down"],
        description_pattern=r"Description[:\s]+(.+?)(?:\n|$)",
        notes="Ruijie switches",
    ),
    
    # ==========================================================================
    # BDCOM Switch
    # ==========================================================================
    Vendor.BDCOM.value: VendorConfig(
        name="BDCOM",
        disable_paging="terminal length 0",
        show_interface="show interface {interface}",
        show_interface_brief="show interface brief",
        show_interface_status="show interface status",
        show_interface_description="show interface description",
        show_optical_all="show transceiver",
        show_optical_interface="show transceiver interface {interface}",
        show_optical_detail="show transceiver interface {interface} detail",
        rx_power_patterns=[r"Rx\s+Power[:\s]+(-?\d+\.?\d*)"],
        tx_power_patterns=[r"Tx\s+Power[:\s]+(-?\d+\.?\d*)"],
        status_up_patterns=[r"Link[:\s]+UP"],
        status_down_patterns=[r"Link[:\s]+DOWN"],
        description_pattern=r"Description[:\s]+(.+?)(?:\n|$)",
        notes="BDCOM switches",
    ),
    
    # ==========================================================================
    # RAISECOM
    # ==========================================================================
    Vendor.RAISECOM.value: VendorConfig(
        name="Raisecom",
        disable_paging="terminal length 0",
        show_interface="show interface {interface}",
        show_interface_brief="show interface brief",
        show_interface_status="show interface status",
        show_interface_description="show interface description",
        show_optical_all="show transceiver",
        show_optical_interface="show transceiver {interface}",
        show_optical_detail="show transceiver {interface} detail",
        rx_power_patterns=[r"Rx\s*Power[:\s]+(-?\d+\.?\d*)"],
        tx_power_patterns=[r"Tx\s*Power[:\s]+(-?\d+\.?\d*)"],
        status_up_patterns=[r"Status[:\s]+UP"],
        status_down_patterns=[r"Status[:\s]+DOWN"],
        description_pattern=r"Description[:\s]+(.+?)(?:\n|$)",
        notes="Raisecom equipment",
    ),
    
    # ==========================================================================
    # FS.COM
    # ==========================================================================
    Vendor.FS.value: VendorConfig(
        name="FS.COM",
        disable_paging="terminal length 0",
        show_interface="show interface {interface}",
        show_interface_brief="show interface status",
        show_interface_status="show interface status",
        show_interface_description="show interface description",
        show_optical_all="show transceiver",
        show_optical_interface="show transceiver interface {interface}",
        show_optical_detail="show transceiver interface {interface}",
        rx_power_patterns=[r"Rx\s+Power[:\s]+(-?\d+\.?\d*)"],
        tx_power_patterns=[r"Tx\s+Power[:\s]+(-?\d+\.?\d*)"],
        status_up_patterns=[r"Link[:\s]+Up"],
        status_down_patterns=[r"Link[:\s]+Down"],
        description_pattern=r"Description[:\s]+(.+?)(?:\n|$)",
        notes="FS.COM switches",
    ),
    
    # ==========================================================================
    # ALLIED TELESIS
    # ==========================================================================
    Vendor.ALLIED.value: VendorConfig(
        name="Allied Telesis",
        disable_paging="terminal length 0",
        show_interface="show interface {interface}",
        show_interface_brief="show interface brief",
        show_interface_status="show interface status",
        show_interface_description="show interface description",
        show_optical_all="show system pluggable",
        show_optical_interface="show system pluggable {interface}",
        show_optical_detail="show system pluggable {interface} detail",
        rx_power_patterns=[r"Rx\s+Power[:\s]+(-?\d+\.?\d*)"],
        tx_power_patterns=[r"Tx\s+Power[:\s]+(-?\d+\.?\d*)"],
        status_up_patterns=[r"Status[:\s]+UP"],
        status_down_patterns=[r"Status[:\s]+DOWN"],
        description_pattern=r"Description[:\s]+(.+?)(?:\n|$)",
        notes="Allied Telesis switches",
    ),
    
    # ==========================================================================
    # DATACOM
    # ==========================================================================
    Vendor.DATACOM.value: VendorConfig(
        name="Datacom",
        disable_paging="terminal length 0",
        show_interface="show interface {interface}",
        show_interface_brief="show interface status",
        show_interface_status="show interface status",
        show_interface_description="show interface description",
        show_optical_all="show interface transceiver",
        show_optical_interface="show interface {interface} transceiver",
        show_optical_detail="show interface {interface} transceiver detail",
        rx_power_patterns=[r"Rx\s+Power[:\s]+(-?\d+\.?\d*)"],
        tx_power_patterns=[r"Tx\s+Power[:\s]+(-?\d+\.?\d*)"],
        status_up_patterns=[r"Status[:\s]+UP"],
        status_down_patterns=[r"Status[:\s]+DOWN"],
        description_pattern=r"Description[:\s]+(.+?)(?:\n|$)",
        notes="Datacom switches",
    ),
    
    # ==========================================================================
    # GENERIC
    # ==========================================================================
    Vendor.GENERIC.value: VendorConfig(
        name="Generic",
        disable_paging="terminal length 0",
        show_interface="show interface {interface}",
        show_interface_brief="show interface brief",
        show_interface_status="show interface status",
        show_interface_description="show interface description",
        show_optical_all="show transceiver",
        show_optical_interface="show transceiver interface {interface}",
        show_optical_detail="show transceiver interface {interface}",
        alt_optical_commands=[
            "display transceiver interface {interface}",
            "display transceiver diagnosis interface {interface}",
        ],
        alt_interface_commands=["display interface {interface}"],
        rx_power_patterns=[
            r"(?:Rx|RX|Receive)\s*(?:Power|power)[:\s\|]+(-?\d+\.?\d*)",
        ],
        tx_power_patterns=[
            r"(?:Tx|TX|Transmit)\s*(?:Power|power)[:\s\|]+(-?\d+\.?\d*)",
        ],
        status_up_patterns=[r"(?:line protocol|status|state|link)\s+(?:is\s+)?up", r"is\s+UP"],
        status_down_patterns=[r"(?:line protocol|status|state|link)\s+(?:is\s+)?down", r"is\s+DOWN"],
        description_pattern=r"[Dd]escription[:\s]+(.+?)(?:\n|$)",
        notes="Generic fallback",
    ),
}


def get_vendor_config(vendor: str) -> VendorConfig:
    """Get vendor configuration by name"""
    vendor_lower = vendor.lower().strip().replace(" ", "_").replace("-", "_")
    if vendor_lower in VENDOR_CONFIGS:
        return VENDOR_CONFIGS[vendor_lower]
    for key in VENDOR_CONFIGS:
        if vendor_lower in key or key in vendor_lower:
            return VENDOR_CONFIGS[key]
    return VENDOR_CONFIGS[Vendor.GENERIC.value]


def get_supported_vendors() -> List[str]:
    """Get list of supported vendors"""
    return [v.value for v in Vendor]


def get_optical_commands(vendor: str, interface: str) -> List[str]:
    """Get list of optical commands for a vendor and interface"""
    config = get_vendor_config(vendor)
    commands = []
    
    if config.show_optical_interface:
        commands.append(config.show_optical_interface.format(interface=interface))
    if config.show_optical_detail:
        cmd = config.show_optical_detail.format(interface=interface)
        if cmd not in commands:
            commands.append(cmd)
    
    for alt_cmd in config.alt_optical_commands:
        if '{interface}' in alt_cmd:
            cmd = alt_cmd.format(interface=interface)
            if cmd not in commands:
                commands.append(cmd)
    
    return commands


class OpticalParser:
    """Parser for optical power readings"""
    
    def __init__(self, vendor: str = "generic"):
        self.vendor = vendor
        self.config = get_vendor_config(vendor)
    
    def parse_optical_power(self, output: str) -> Dict[str, Any]:
        """Parse optical power from command output"""
        result = {
            'rx_power': None, 'tx_power': None,
            'rx_power_dbm': 'N/A', 'tx_power_dbm': 'N/A',
            'signal_status': 'unknown', 'raw_output': output, 'found': False,
        }
        
        if not output:
            return result
        
        # Try RX patterns
        for pattern in self.config.rx_power_patterns:
            match = re.search(pattern, output, re.IGNORECASE | re.MULTILINE)
            if match:
                try:
                    result['rx_power'] = float(match.group(1))
                    result['rx_power_dbm'] = f"{result['rx_power']:.2f} dBm"
                    result['found'] = True
                    break
                except:
                    continue
        
        # Try TX patterns
        for pattern in self.config.tx_power_patterns:
            match = re.search(pattern, output, re.IGNORECASE | re.MULTILINE)
            if match:
                try:
                    result['tx_power'] = float(match.group(1))
                    result['tx_power_dbm'] = f"{result['tx_power']:.2f} dBm"
                    result['found'] = True
                    break
                except:
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
                except:
                    pass
            elif len(dbm_matches) == 1:
                try:
                    result['rx_power'] = float(dbm_matches[0])
                    result['rx_power_dbm'] = f"{result['rx_power']:.2f} dBm"
                    result['found'] = True
                except:
                    pass
        
        # Signal status
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
            elif rx >= -30:
                result['signal_status'] = 'very_weak'
            else:
                result['signal_status'] = 'critical'
        
        return result
    
    def parse_interface_status(self, output: str) -> str:
        """Parse interface status from output"""
        if not output:
            return 'unknown'
        
        # MikroTik special handling
        if self.vendor.lower() == 'mikrotik':
            if re.search(r'status[:\s]+link-ok', output, re.IGNORECASE):
                return 'up'
            if re.search(r'status[:\s]+no-link', output, re.IGNORECASE):
                return 'down'
        
        for pattern in self.config.status_up_patterns:
            if re.search(pattern, output, re.IGNORECASE | re.MULTILINE):
                return 'up'
        for pattern in self.config.status_down_patterns:
            if re.search(pattern, output, re.IGNORECASE | re.MULTILINE):
                return 'down'
        return 'unknown'
    
    def parse_description(self, output: str) -> str:
        """Parse interface description from output"""
        if not output or not self.config.description_pattern:
            return ''
        match = re.search(self.config.description_pattern, output, re.IGNORECASE)
        return match.group(1).strip() if match else ''


# =============================================================================
# MIKROTIK OUTPUT CLEANER - v4.8.4
# =============================================================================

def clean_mikrotik_output(output: str) -> str:
    """
    Clean MikroTik output - remove prompts and command echoes
    
    v4.8.4: More careful cleaning to preserve data
    """
    if not output:
        return output
    
    # Remove ANSI escape codes
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    output = ansi_escape.sub('', output)
    
    # Remove carriage returns
    output = output.replace('\r', '')
    
    lines = output.split('\n')
    cleaned_lines = []
    
    for line in lines:
        # Skip pure prompt lines: [user@hostname] > or [user@hostname] /path>
        # BUT be careful not to remove lines that just contain [ from comments
        if re.match(r'^\s*\[[\w\-@]+\]\s*[/\w]*[>#]\s*$', line):
            continue
        
        # Remove prompt from END of line only
        # Pattern: [user@host] > at the very end
        line = re.sub(r'\s*\[[\w\-@]+\]\s*[/\w]*[>#]\s*$', '', line)
        
        cleaned_lines.append(line)
    
    return '\n'.join(cleaned_lines)


# =============================================================================
# MIKROTIK INTERFACE PARSER - FIXED v4.8.4
# =============================================================================

def parse_mikrotik_interfaces(output: str) -> List[Dict[str, Any]]:
    """
    Parse MikroTik /interface print brief output - FIXED v4.8.4
    
    Format:
    Flags: R - RUNNING; S - SLAVE
    Columns: NAME, TYPE, ACTUAL-MTU, L2MTU, MAX-L2MTU, MAC-ADDRESS
    #   NAME           TYPE      ACTUAL-MTU  L2MTU  MAX-L2MTU  MAC-ADDRESS
    0   ether1         ether           1500   1584      10218  48:8F:5A:05:51:79
    ;;; Cust:SECAPA{cvlan 400}[2Gbps]
    15 RS sfp-sfpplus16   ether           1500   1584      10218  48:8F:5A:05:51:69
    
    v4.8.4 FIX:
    - Handle comments with special characters: {}, [], :, etc.
    - Comment line (;;;) should NOT affect next interface line parsing
    - Don't strip [ from interface names - only remove MikroTik prompts
    
    Flag meanings:
    - R = RUNNING = UP
    - RS = RUNNING + SLAVE = UP  
    - S = SLAVE only = DOWN
    - X = DISABLED = DOWN
    - (empty) = DOWN
    """
    interfaces = []
    
    if not output:
        return interfaces
    
    # v4.8.4: Clean output but preserve data
    output = clean_mikrotik_output(output)
    
    lines = output.split('\n')
    current_comment = ''
    
    for line in lines:
        line_stripped = line.strip()
        
        if not line_stripped:
            continue
        
        # Skip headers
        if line_stripped.startswith('Flags:') or line_stripped.startswith('Columns:'):
            continue
        if 'NAME' in line_stripped and 'TYPE' in line_stripped and 'MTU' in line_stripped:
            continue
        
        # v4.8.4: Capture comments - can contain ANY characters including {}, []
        # Example: ;;; Cust:SECAPA{cvlan 400}[2Gbps]
        if line_stripped.startswith(';;;'):
            current_comment = line_stripped[3:].strip()
            continue
        
        # v4.8.4: Skip lines that are ONLY a MikroTik prompt
        # Must have @ and end with > or #
        if re.match(r'^\[[\w\-]+@[\w\-]+\].*[>#]\s*$', line_stripped):
            # Check if there's actual data after the prompt
            # Example: [admin@MT] > 15 RS sfp-sfpplus16 ether
            match = re.search(r'[>#]\s*(\d+.*)$', line_stripped)
            if match:
                # There's data after prompt, extract it
                line_stripped = match.group(1).strip()
            else:
                continue
        
        # v4.8.4: Interface line pattern - starts with number
        # Pattern: NUM [FLAGS] NAME TYPE ...
        # Examples:
        #   0   ether1         ether           1500
        #   1 RS sfp-sfpplus1   ether           1500
        #  15   sfp-sfpplus16  ether           1500
        
        match = re.match(r'^(\d+)\s+(.+)$', line_stripped)
        
        if not match:
            continue
        
        idx = match.group(1)
        rest = match.group(2).strip()
        
        # v4.8.4: DON'T aggressively remove [ from the line
        # Only remove if it's clearly a MikroTik prompt pattern [user@host]
        # NOT if it's part of data like [2Gbps]
        
        # Remove trailing prompt ONLY if it matches MikroTik prompt pattern
        rest = re.sub(r'\s*\[[\w\-]+@[\w\-]+\].*$', '', rest).strip()
        
        parts = rest.split()
        
        if not parts:
            continue
        
        # Determine flags and name
        flags = ''
        name_idx = 0
        
        first = parts[0]
        
        # Check if first part is flags (R, RS, S, X, D, etc.)
        # v4.8.4: Flags are 1-4 uppercase letters from set {R,S,D,X}
        if len(first) <= 4 and first.isalpha() and all(c in 'RSDXrsdx' for c in first):
            flags = first.upper()
            name_idx = 1
        
        if name_idx >= len(parts):
            continue
        
        name = parts[name_idx]
        
        # v4.8.4: DON'T strip [ from name - interface names don't contain [
        # But DO remove if there's a MikroTik prompt attached
        # Only clean if it looks like [user@host] pattern
        if '@' in name and name.startswith('['):
            # This is a prompt, not a valid name
            continue
        
        # Skip invalid names
        if not name:
            continue
        if name in ['ether', 'bond', 'bridge', 'vlan', 'loopback', 'Flags:', 'Columns:', 'NAME']:
            continue
        
        # Determine status from flags
        if 'R' in flags:
            status = 'up'
        else:
            status = 'down'
        
        # Get type (next field after name)
        iface_type = ''
        if len(parts) > name_idx + 1:
            potential_type = parts[name_idx + 1]
            # Type should be simple: ether, bridge, vlan, etc.
            if potential_type in ['ether', 'bridge', 'vlan', 'bond', 'loopback', 'pppoe-out', 'l2tp-out', 'ovpn-out']:
                iface_type = potential_type
        
        interfaces.append({
            'name': name,
            'status': status,
            'description': current_comment,
            'flags': flags,
            'type': iface_type,
        })
        
        # Reset comment for next interface
        current_comment = ''
    
    return interfaces


# =============================================================================
# CISCO NX-OS INTERFACE PARSER
# =============================================================================

def parse_cisco_nxos_interfaces(output: str) -> List[Dict[str, Any]]:
    """
    Parse Cisco NX-OS show interface status output
    
    Format:
    --------------------------------------------------------------------------------
    Port          Name               Status    Vlan      Duplex  Speed   Type
    --------------------------------------------------------------------------------
    Eth1/1        Uplink-Router      connected 1         full    10G     10Gbase-SR
    Eth1/2        --                 notconnect 1        auto    auto    --
    """
    interfaces = []
    
    if not output:
        return interfaces
    
    lines = output.split('\n')
    in_data = False
    
    for line in lines:
        line = line.strip()
        
        if not line:
            continue
        
        if '----' in line:
            in_data = True
            continue
        
        if 'Port' in line and 'Status' in line:
            continue
        
        if not in_data:
            continue
        
        parts = line.split()
        if len(parts) < 3:
            continue
        
        iface_name = parts[0]
        
        if not any(c.isdigit() for c in iface_name):
            continue
        
        status = 'unknown'
        description = ''
        
        line_lower = line.lower()
        
        if 'connected' in line_lower and 'notconnect' not in line_lower:
            status = 'up'
        elif 'notconnect' in line_lower:
            status = 'down'
        elif 'disabled' in line_lower:
            status = 'down'
        elif 'sfp not' in line_lower:
            status = 'down'
        elif 'xcvr not' in line_lower:
            status = 'down'
        
        if len(parts) >= 2:
            desc = parts[1]
            if desc != '--':
                description = desc
        
        interfaces.append({
            'name': iface_name,
            'status': status,
            'description': description,
        })
    
    return interfaces


# =============================================================================
# INTERFACE NAME EXPANSION
# =============================================================================

INTERFACE_ALIASES = {
    'gi': 'GigabitEthernet', 'gig': 'GigabitEthernet',
    'fa': 'FastEthernet', 'te': 'TenGigabitEthernet',
    'eth': 'Ethernet', 'ge': 'GigabitEthernet',
    'xge': 'XGigabitEthernet', '10ge': '10GE',
    '25ge': '25GE', '40ge': '40GE', '100ge': '100GE',
}


def expand_interface_name(short_name: str) -> str:
    """Expand short interface name to full name"""
    for full in INTERFACE_ALIASES.values():
        if short_name.lower().startswith(full.lower()):
            return short_name
    for alias, full in INTERFACE_ALIASES.items():
        if short_name.lower().startswith(alias):
            return f"{full}{short_name[len(alias):]}"
    return short_name
