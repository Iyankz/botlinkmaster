#!/usr/bin/env python3
"""
BotLinkMaster - Vendor Commands v4.8.8
Multi-vendor support for routers and switches

CHANGELOG v4.8.8:
- FIX: Cisco NX-OS description terpotong jika mengandung spasi
       Masalah: "FS(OTB-B T1C1)" menjadi "FS(OTB-B"
       Solusi: normalize_nxos_string() untuk membersihkan karakter non-printable
- FIX: Huawei Non-CloudEngine (Quidway/S-Series) status UNKNOWN
       Masalah: /cek dan /redaman menampilkan UNKNOWN padahal port UP
       Solusi: Tambah pattern "Physical state" dan "Line protocol current state"
- FIX: Optical status tidak lagi tergantung interface status
       Jika RX/TX valid, optical status tetap GOOD/EXCELLENT walaupun link UNKNOWN

CHANGELOG v4.8.7:
- FIX: Cisco IOS show_interface_brief menggunakan "show interface brief"
- FIX: Huawei show_interface_brief menggunakan "display interface description"
- FIX: MikroTik extended timeout dan algorithm support

Note: OLT support will be available in v5.0.0

Author: BotLinkMaster
Version: 4.8.8
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
    # CISCO IOS - FIXED v4.8.7
    # ==========================================================================
    Vendor.CISCO_IOS.value: VendorConfig(
        name="Cisco IOS/IOS-XE",
        disable_paging="terminal length 0",
        show_interface="show interface {interface}",
        # v4.8.7 FIX: Menggunakan "show interface brief" bukan "show ip interface brief"
        show_interface_brief="show interface brief",
        show_interface_status="show interface status",
        show_interface_description="show interface description",
        show_optical_all="show interface transceiver",
        show_optical_interface="show interface {interface} transceiver",
        show_optical_detail="show interface {interface} transceiver detail",
        alt_interface_commands=[
            "show interface status",
            "show interface description",
        ],
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
        notes="Cisco IOS routers and switches - v4.8.7: Fixed show interface brief",
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
    # HUAWEI VRP - FIXED v4.8.7
    # ==========================================================================
    Vendor.HUAWEI.value: VendorConfig(
        name="Huawei VRP",
        disable_paging="screen-length 0 temporary",
        show_interface="display interface {interface}",
        # v4.8.7 FIX: Menggunakan "display interface description" untuk list interface
        # yang menampilkan nama interface dan deskripsi dengan benar
        show_interface_brief="display interface description",
        show_interface_status="display interface description",
        show_interface_description="display interface description",
        show_optical_all="display transceiver",
        show_optical_interface="display transceiver interface {interface}",
        show_optical_detail="display interface {interface} transceiver verbose",
        alt_optical_commands=[
            "display interface {interface} transceiver brief",
            "display interface {interface} transceiver verbose",
            "display transceiver interface {interface} verbose",
            "display transceiver diagnosis interface {interface}",
            "display transceiver interface {interface}",
        ],
        alt_interface_commands=[
            "display interface brief",
            "display interface description",
        ],
        rx_power_patterns=[
            r"RX\s*power\s*\(dBm\)[:\s\|]+(-?\d+\.?\d*)",
            r"RxPower\s*\(dBm\)\s*\|?\s*(-?\d+\.?\d*)",
            r"Rx\s*Power\s*\(dBm\)[:\s]+(-?\d+\.?\d*)",
            r"Current\s+RX\s+Power\s*\(dBm\)[:\s]+(-?\d+\.?\d*)",
            r"RX\s+Power[:\s]+(-?\d+\.?\d*)",
            r"Rx\s+optical\s+power[:\s]+(-?\d+\.?\d*)",
            r"RX[:\s]+(-?\d+\.?\d*)\s*dBm",
            r"Rx\s+Power\s*:\s*(-?\d+\.?\d*)",
            r"RxPower[:\s]+(-?\d+\.?\d*)",
        ],
        tx_power_patterns=[
            r"TX\s*power\s*\(dBm\)[:\s\|]+(-?\d+\.?\d*)",
            r"TxPower\s*\(dBm\)\s*\|?\s*(-?\d+\.?\d*)",
            r"Tx\s*Power\s*\(dBm\)[:\s]+(-?\d+\.?\d*)",
            r"Current\s+TX\s+Power\s*\(dBm\)[:\s]+(-?\d+\.?\d*)",
            r"TX\s+Power[:\s]+(-?\d+\.?\d*)",
            r"Tx\s+optical\s+power[:\s]+(-?\d+\.?\d*)",
            r"TX[:\s]+(-?\d+\.?\d*)\s*dBm",
            r"Tx\s+Power\s*:\s*(-?\d+\.?\d*)",
            r"TxPower[:\s]+(-?\d+\.?\d*)",
        ],
        status_up_patterns=[
            r"current state[:\s]*UP",
            r"Physical[:\s]+UP",
            r"is\s+UP",
            # v4.8.8: Huawei Non-CloudEngine (Quidway/S-Series) patterns
            r"Physical\s+state\s*:\s*Up",
            r"Line\s+protocol\s+current\s+state\s*:\s*Up",
            r"Physical\s+layer\s+state\s*:\s*Up",
            r"Link\s+state\s*:\s*Up",
        ],
        status_down_patterns=[
            r"current state[:\s]*DOWN",
            r"Physical[:\s]+DOWN",
            r"is\s+DOWN",
            # v4.8.8: Huawei Non-CloudEngine (Quidway/S-Series) patterns
            r"Physical\s+state\s*:\s*Down",
            r"Line\s+protocol\s+current\s+state\s*:\s*Down",
            r"Physical\s+layer\s+state\s*:\s*Down",
            r"Link\s+state\s*:\s*Down",
            r"Administratively\s+DOWN",
        ],
        description_pattern=r"Description[:\s]+(.+?)(?:\n|$)",
        notes="Huawei routers and switches - v4.8.7: Fixed interface list command",
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
    # MIKROTIK RouterOS - IMPROVED v4.8.7
    # ==========================================================================
    Vendor.MIKROTIK.value: VendorConfig(
        name="MikroTik RouterOS",
        disable_paging="",  # MikroTik uses "without-paging" in commands
        show_interface="/interface ethernet print detail without-paging where name={interface}",
        show_interface_brief="/interface ethernet print without-paging",
        show_interface_status="/interface ethernet print without-paging",
        show_interface_description="/interface ethernet print without-paging",
        show_optical_all="/interface ethernet monitor [find] once",
        show_optical_interface="/interface ethernet monitor {interface} once",
        show_optical_detail="/interface ethernet monitor {interface} once",
        alt_optical_commands=[
            "/interface ethernet monitor {interface} once",
        ],
        alt_interface_commands=[
            "/interface ethernet print without-paging",
            "/interface print brief without-paging",
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
        notes="MikroTik RouterOS v4.8.7 - CRS326 compatibility fix",
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
# CISCO NX-OS STRING NORMALIZER - v4.8.8
# =============================================================================

def normalize_nxos_string(text: str) -> str:
    """
    Normalize Cisco NX-OS output string - v4.8.8
    
    Masalah: Description dengan spasi terpotong di display
    Contoh: "FS(OTB-B T1C1)" tampil sebagai "FS(OTB-B"
    
    Root cause: NX-OS output mengandung karakter non-printable atau
    whitespace special yang menyebabkan layer display menganggap string selesai.
    
    Solusi:
    - Hapus karakter non-printable (control characters)
    - Normalize whitespace (non-breaking space -> regular space)
    - Strip karakter aneh di awal/akhir
    """
    if not text:
        return text
    
    # Remove ANSI escape codes
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    text = ansi_escape.sub('', text)
    
    # Replace non-breaking space (U+00A0) with regular space
    text = text.replace('\u00a0', ' ')
    
    # Replace other special whitespace characters
    special_spaces = [
        '\u2000',  # En Quad
        '\u2001',  # Em Quad
        '\u2002',  # En Space
        '\u2003',  # Em Space
        '\u2004',  # Three-Per-Em Space
        '\u2005',  # Four-Per-Em Space
        '\u2006',  # Six-Per-Em Space
        '\u2007',  # Figure Space
        '\u2008',  # Punctuation Space
        '\u2009',  # Thin Space
        '\u200a',  # Hair Space
        '\u200b',  # Zero Width Space
        '\u202f',  # Narrow No-Break Space
        '\u205f',  # Medium Mathematical Space
        '\u3000',  # Ideographic Space
    ]
    for sp in special_spaces:
        text = text.replace(sp, ' ')
    
    # Remove control characters (0x00-0x1F except tab, newline, carriage return)
    # And DEL (0x7F) and other non-printable
    cleaned = []
    for char in text:
        code = ord(char)
        # Keep printable ASCII (0x20-0x7E), tab (0x09), newline (0x0A), CR (0x0D)
        # And extended printable characters (0x80+)
        if (0x20 <= code <= 0x7E) or code in (0x09, 0x0A, 0x0D) or code >= 0x80:
            # But filter out problematic high characters
            if code < 0x100 or (code >= 0x100 and not (0xFFF0 <= code <= 0xFFFF)):
                cleaned.append(char)
    
    text = ''.join(cleaned)
    
    # Normalize multiple spaces to single space (but preserve structure)
    text = re.sub(r'[ \t]{2,}', '  ', text)
    
    # Strip leading/trailing whitespace per line
    lines = text.split('\n')
    lines = [line.strip() for line in lines]
    text = '\n'.join(lines)
    
    return text


def normalize_description(desc: str) -> str:
    """
    Normalize interface description specifically - v4.8.8
    
    Removes all non-printable characters and normalizes whitespace
    while preserving the actual content of the description.
    """
    if not desc:
        return desc
    
    # First pass: basic normalization
    desc = normalize_nxos_string(desc)
    
    # Remove hidden characters that might terminate display
    # Some terminals treat certain characters as string terminators
    desc = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', desc)
    
    # Normalize whitespace to regular spaces
    desc = re.sub(r'\s+', ' ', desc)
    
    # Strip
    desc = desc.strip()
    
    return desc


# =============================================================================
# MIKROTIK OUTPUT CLEANER - v4.8.7
# =============================================================================

def clean_mikrotik_output(output: str) -> str:
    """Clean MikroTik output - remove prompts, paging, and command echoes"""
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
        # Skip paging prompt lines
        if line.strip().startswith('-- [') or line.strip() == '-- more --':
            continue
        
        # Skip pure prompt lines
        if re.match(r'^\s*\[[\w\-@]+\]\s*[/\w]*[>#]\s*$', line):
            continue
        
        # Remove prompt from END of line only
        line = re.sub(r'\s*\[[\w\-@]+\]\s*[/\w]*[>#]\s*$', '', line)
        
        cleaned_lines.append(line)
    
    return '\n'.join(cleaned_lines)


# =============================================================================
# MIKROTIK INTERFACE PARSER - v4.8.7
# =============================================================================

def parse_mikrotik_interfaces(output: str) -> List[Dict[str, Any]]:
    """Parse MikroTik /interface ethernet print without-paging output - v4.8.7"""
    interfaces = []
    
    if not output:
        return interfaces
    
    # Clean output
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
        if 'NAME' in line_stripped and 'TYPE' in line_stripped:
            continue
        if 'NAME' in line_stripped and 'MTU' in line_stripped:
            continue
        
        # Skip paging prompts
        if line_stripped.startswith('-- [') or line_stripped.startswith('-- more'):
            continue
        
        # Capture comments
        if line_stripped.startswith(';;;'):
            current_comment = line_stripped[3:].strip()
            continue
        
        # Skip prompt lines
        if re.match(r'^\[[\w\-]+@[\w\-]+\].*[>#]\s*$', line_stripped):
            match = re.search(r'[>#]\s*(\d+.*)$', line_stripped)
            if match:
                line_stripped = match.group(1).strip()
            else:
                continue
        
        # Interface line pattern: NUM FLAGS NAME TYPE ...
        match = re.match(r'^(\d+)\s+(.+)$', line_stripped)
        
        if not match:
            continue
        
        idx = match.group(1)
        rest = match.group(2).strip()
        
        # Remove trailing prompt if attached
        rest = re.sub(r'\s*\[[\w\-]+@[\w\-]+\].*$', '', rest).strip()
        
        parts = rest.split()
        
        if not parts:
            continue
        
        # Determine flags and name
        flags = ''
        name_idx = 0
        
        first = parts[0]
        
        # Flags: R=running, S=slave, X=disabled, D=dynamic
        if len(first) <= 4 and first.isalpha() and all(c in 'RSDXrsdx' for c in first):
            flags = first.upper()
            name_idx = 1
        
        if name_idx >= len(parts):
            continue
        
        name = parts[name_idx]
        
        # Skip invalid names
        if not name:
            continue
        if name in ['ether', 'bond', 'bridge', 'vlan', 'loopback', 'Flags:', 'Columns:', 'NAME']:
            continue
        if '@' in name and name.startswith('['):
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
            if potential_type in ['ether', 'bridge', 'vlan', 'bond', 'loopback', 'pppoe-out', 'l2tp-out', 'ovpn-out']:
                iface_type = potential_type
        
        interfaces.append({
            'name': name,
            'status': status,
            'description': current_comment,
            'flags': flags,
            'type': iface_type,
        })
        
        # Reset comment
        current_comment = ''
    
    return interfaces


# =============================================================================
# CISCO NX-OS INTERFACE PARSER - v4.8.8 FIXED
# =============================================================================

def parse_cisco_nxos_interfaces(output: str) -> List[Dict[str, Any]]:
    """
    Parse Cisco NX-OS show interface status output - v4.8.8 FIXED
    
    v4.8.8 FIX: Description dengan spasi tidak lagi terpotong
    Masalah: "FS(OTB-B T1C1)" menjadi "FS(OTB-B"
    Solusi: Parse berdasarkan posisi kolom, bukan split by whitespace
    
    Format output NX-OS:
    Port          Name               Status    Vlan      Duplex  Speed   Type
    --------------------------------------------------------------------------------
    Eth1/1        FS(OTB-B T1C1)     connected 100       full    10G     10Gbase-SR
    """
    interfaces = []
    
    if not output:
        return interfaces
    
    # v4.8.8: Normalize output first
    output = normalize_nxos_string(output)
    
    lines = output.split('\n')
    in_data = False
    header_positions = {}
    
    for line in lines:
        original_line = line
        line_stripped = line.strip()
        
        if not line_stripped:
            continue
        
        # Detect header line to get column positions
        if 'Port' in line and 'Status' in line:
            # Parse header positions
            # Find each column header position
            for col in ['Port', 'Name', 'Status', 'Vlan', 'Duplex', 'Speed', 'Type']:
                pos = line.find(col)
                if pos >= 0:
                    header_positions[col] = pos
            continue
        
        if '----' in line_stripped:
            in_data = True
            continue
        
        if not in_data:
            continue
        
        # v4.8.8: Use column positions if available
        if header_positions and 'Port' in header_positions:
            iface_name = ''
            description = ''
            status = 'unknown'
            
            # Extract interface name (Port column)
            port_start = header_positions.get('Port', 0)
            name_start = header_positions.get('Name', 14)
            
            # Get interface name - from Port position to Name position
            if len(original_line) > port_start:
                port_end = min(name_start, len(original_line))
                iface_name = original_line[port_start:port_end].strip()
            
            # Get description (Name column) - from Name position to Status position
            status_start = header_positions.get('Status', 32)
            if len(original_line) > name_start:
                desc_end = min(status_start, len(original_line))
                description = original_line[name_start:desc_end].strip()
                # v4.8.8: Normalize description to remove hidden characters
                description = normalize_description(description)
            
            # Get status - check Status column area
            if len(original_line) > status_start:
                vlan_start = header_positions.get('Vlan', status_start + 12)
                status_text = original_line[status_start:vlan_start].strip().lower()
                
                if 'connected' in status_text and 'notconnect' not in status_text:
                    status = 'up'
                elif 'notconnect' in status_text:
                    status = 'down'
                elif 'disabled' in status_text:
                    status = 'down'
                elif 'sfp' in status_text or 'xcvr' in status_text:
                    status = 'down'
            
            # Validate interface name
            if iface_name and any(c.isdigit() for c in iface_name):
                interfaces.append({
                    'name': iface_name,
                    'status': status,
                    'description': description,
                })
        else:
            # Fallback: parse without header positions (old method improved)
            parts = line_stripped.split()
            if len(parts) < 3:
                continue
            
            iface_name = parts[0]
            
            if not any(c.isdigit() for c in iface_name):
                continue
            
            status = 'unknown'
            description = ''
            
            line_lower = line_stripped.lower()
            
            # Find status keyword position
            status_keywords = ['connected', 'notconnect', 'disabled', 'sfpabsent', 'xcvrnotse', 'linknotco']
            status_pos = -1
            status_word = ''
            
            for kw in status_keywords:
                pos = line_lower.find(kw)
                if pos > 0:
                    status_pos = pos
                    status_word = kw
                    break
            
            # v4.8.8: Extract description as everything between interface name and status
            if status_pos > 0:
                # Find where interface name ends
                iface_end = len(iface_name)
                while iface_end < len(line_stripped) and line_stripped[iface_end] == ' ':
                    iface_end += 1
                
                # Description is between interface name and status
                if iface_end < status_pos:
                    description = line_stripped[iface_end:status_pos].strip()
                    description = normalize_description(description)
            
            # Determine status
            if 'connected' in line_lower and 'notconnect' not in line_lower:
                status = 'up'
            elif 'notconnect' in line_lower:
                status = 'down'
            elif 'disabled' in line_lower:
                status = 'down'
            elif 'sfp not' in line_lower or 'sfpabsent' in line_lower:
                status = 'down'
            elif 'xcvr not' in line_lower or 'xcvrnotse' in line_lower:
                status = 'down'
            
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
