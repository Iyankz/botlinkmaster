#!/usr/bin/env python3
"""
BotLinkMaster - Vendor Commands v4.5.2
Multi-vendor support with improved ZTE OLT and MikroTik parsing

Author: BotLinkMaster
Version: 4.5.2
"""

import re
from typing import Dict, Any, List
from dataclasses import dataclass, field
from enum import Enum


class Vendor(Enum):
    CISCO_IOS = "cisco_ios"
    CISCO_NXOS = "cisco_nxos"
    HUAWEI = "huawei"
    HUAWEI_OLT = "huawei_olt"
    ZTE = "zte"
    ZTE_OLT = "zte_olt"
    JUNIPER = "juniper"
    MIKROTIK = "mikrotik"
    NOKIA = "nokia"
    HP_ARUBA = "hp_aruba"
    FIBERHOME = "fiberhome"
    FIBERHOME_OLT = "fiberhome_olt"
    DCN = "dcn"
    H3C = "h3c"
    RUIJIE = "ruijie"
    BDCOM = "bdcom"
    BDCOM_OLT = "bdcom_olt"
    RAISECOM = "raisecom"
    FS = "fs"
    ALLIED = "allied"
    DATACOM = "datacom"
    VSOL_OLT = "vsol_olt"
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
    show_onu_optical: str = ""
    show_onu_list: str = ""
    alt_optical_commands: List[str] = field(default_factory=list)
    alt_interface_commands: List[str] = field(default_factory=list)
    rx_power_patterns: List[str] = field(default_factory=list)
    tx_power_patterns: List[str] = field(default_factory=list)
    attenuation_patterns: List[str] = field(default_factory=list)
    status_up_patterns: List[str] = field(default_factory=list)
    status_down_patterns: List[str] = field(default_factory=list)
    description_pattern: str = ""
    interface_parser: str = "default"  # default, mikrotik, zte_olt
    notes: str = ""


VENDOR_CONFIGS: Dict[str, VendorConfig] = {
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
    
    Vendor.CISCO_NXOS.value: VendorConfig(
        name="Cisco NX-OS",
        disable_paging="terminal length 0",
        show_interface="show interface {interface}",
        show_interface_brief="show interface brief",
        show_interface_status="show interface status",
        show_interface_description="show interface description",
        show_optical_all="show interface transceiver details",
        show_optical_interface="show interface {interface} transceiver details",
        show_optical_detail="show interface {interface} transceiver details",
        rx_power_patterns=[r"Rx\s+Power[:\s]+(-?\d+\.?\d*)\s*dBm"],
        tx_power_patterns=[r"Tx\s+Power[:\s]+(-?\d+\.?\d*)\s*dBm"],
        status_up_patterns=[r"line protocol is up"],
        status_down_patterns=[r"line protocol is down"],
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
    
    Vendor.HUAWEI_OLT.value: VendorConfig(
        name="Huawei OLT",
        disable_paging="scroll",
        show_interface="display interface {interface}",
        show_interface_brief="display board 0",
        show_interface_status="display port state all",
        show_interface_description="display ont info summary 0",
        show_optical_all="display ont optical-info all",
        show_optical_interface="display transceiver interface {interface}",
        show_optical_detail="display transceiver diagnosis interface {interface}",
        show_onu_optical="display ont optical-info {port} {onu_id}",
        show_onu_list="display ont info 0 all",
        alt_optical_commands=[
            "display ont optical-info all",
        ],
        rx_power_patterns=[
            r"Rx\s*optical\s*power[:\s]+(-?\d+\.?\d*)",
            r"OLT\s+Rx[:\s]+(-?\d+\.?\d*)",
        ],
        tx_power_patterns=[
            r"Tx\s*optical\s*power[:\s]+(-?\d+\.?\d*)",
            r"ONU\s+Tx[:\s]+(-?\d+\.?\d*)",
        ],
        status_up_patterns=[r"Run\s+state[:\s]*online", r"Status[:\s]*UP"],
        status_down_patterns=[r"Run\s+state[:\s]*offline", r"Status[:\s]*DOWN"],
        notes="Huawei OLT MA5600/MA5800",
    ),
    
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
    # ZTE OLT - IMPROVED
    # ==========================================================================
    Vendor.ZTE_OLT.value: VendorConfig(
        name="ZTE OLT",
        disable_paging="terminal length 0",
        show_interface="show interface {interface}",
        show_interface_brief="show card",
        show_interface_status="show card",
        show_interface_description="show card",
        show_optical_all="show pon power attenuation {interface}",
        show_optical_interface="show pon power attenuation {interface}",
        show_optical_detail="show pon power attenuation {interface}",
        show_onu_optical="show pon power attenuation {interface}",
        show_onu_list="show gpon onu state {interface}",
        alt_optical_commands=[
            "show pon power attenuation {interface}",
            "show gpon onu detail-info {interface}",
            "show gpon remote-onu interface {interface}",
        ],
        alt_interface_commands=[
            "show gpon onu state {interface}",
            "show gpon onu baseinfo {interface}",
        ],
        interface_parser="zte_olt",
        # ZTE OLT output format:
        # up      Rx :-32.285(dbm)      Tx:2.491(dbm)        34.776(dB)
        # down    Tx :8.164(dbm)        Rx:-23.872(dbm)      32.036(dB)
        rx_power_patterns=[
            r"up\s+Rx\s*[:\s]*(-?\d+\.?\d*)\s*\(?[dD][bB][mM]?\)?",
            r"Rx\s*[:\s]*(-?\d+\.?\d*)\s*\(?[dD][bB][mM]?\)?",
            r"down\s+.*Rx\s*[:\s]*(-?\d+\.?\d*)\s*\(?[dD][bB][mM]?\)?",
        ],
        tx_power_patterns=[
            r"up\s+.*Tx\s*[:\s]*(-?\d+\.?\d*)\s*\(?[dD][bB][mM]?\)?",
            r"Tx\s*[:\s]*(-?\d+\.?\d*)\s*\(?[dD][bB][mM]?\)?",
            r"down\s+Tx\s*[:\s]*(-?\d+\.?\d*)\s*\(?[dD][bB][mM]?\)?",
        ],
        attenuation_patterns=[
            r"(\d+\.?\d*)\s*\(?[dD][bB]\)?\s*$",
            r"Attenuation[:\s]+(\d+\.?\d*)",
        ],
        status_up_patterns=[
            r"Phase[:\s]*working",
            r"working",
            r"OperState[:\s]*up",
        ],
        status_down_patterns=[
            r"Phase[:\s]*offline",
            r"Phase[:\s]*LOS",
            r"OperState[:\s]*down",
            r"offline",
        ],
        notes="ZTE OLT C300/C600. Format: gpon-onu_1/2/1:10",
    ),
    
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
    # MIKROTIK - IMPROVED v4.5.3
    # ==========================================================================
    Vendor.MIKROTIK.value: VendorConfig(
        name="MikroTik RouterOS",
        disable_paging="",
        show_interface="/interface print detail where name={interface}",
        show_interface_brief="/interface print",
        show_interface_status="/interface print",
        show_interface_description="/interface print",
        show_optical_all="/interface ethernet monitor [find] once",
        show_optical_interface="/interface ethernet monitor {interface} once",
        show_optical_detail="/interface ethernet monitor {interface} once",
        alt_optical_commands=[
            "/interface sfp-sfpplus monitor {interface} once",
            "/interface sfp monitor {interface} once",
            "/interface ethernet monitor {interface} once",
        ],
        alt_interface_commands=[
            "/interface print",
            "/interface print brief", 
            "/interface ethernet print",
            "/interface print without-paging",
            "interface print",
        ],
        interface_parser="mikrotik",
        rx_power_patterns=[
            r"sfp-rx-power[:\s]+(-?\d+\.?\d*)\s*dBm",
            r"sfp-rx-power[:\s]+(-?\d+\.?\d*)",
            r"rx-power[:\s]+(-?\d+\.?\d*)",
            r"Rx\s*Power[:\s]+(-?\d+\.?\d*)",
        ],
        tx_power_patterns=[
            r"sfp-tx-power[:\s]+(-?\d+\.?\d*)\s*dBm",
            r"sfp-tx-power[:\s]+(-?\d+\.?\d*)",
            r"tx-power[:\s]+(-?\d+\.?\d*)",
            r"Tx\s*Power[:\s]+(-?\d+\.?\d*)",
        ],
        # MikroTik flags: R=RUNNING, S=SLAVE, X=DISABLED
        status_up_patterns=[
            r"^\s*\d+\s+R",
            r"^\s*\d+\s+RS",
            r"\bR\b.*\b(ether|sfp|bond|bridge|vlan)",
            r"running=yes",
            r"flags=.*R",
            r"status=link-ok",
        ],
        status_down_patterns=[
            r"^\s*\d+\s+X",
            r"running=no",
            r"disabled=yes",
            r"status=no-link",
        ],
        description_pattern=r"comment=([^\n]+)",
        notes="MikroTik RouterOS - Flags: R=RUNNING, RS=RUNNING+SLAVE, S=SLAVE, X=DISABLED",
    ),
    
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
    
    Vendor.FIBERHOME_OLT.value: VendorConfig(
        name="FiberHome OLT",
        disable_paging="terminal length 0",
        show_interface="show interface {interface}",
        show_interface_brief="show card",
        show_interface_status="show ont status",
        show_interface_description="show interface description",
        show_optical_all="show transceiver detail",
        show_optical_interface="show transceiver interface {interface}",
        show_optical_detail="show transceiver interface {interface}",
        show_onu_optical="show ont optical-info {interface}",
        show_onu_list="show ont info",
        rx_power_patterns=[r"Rx\s*Power[:\s]+(-?\d+\.?\d*)"],
        tx_power_patterns=[r"Tx\s*Power[:\s]+(-?\d+\.?\d*)"],
        status_up_patterns=[r"Status[:\s]+online"],
        status_down_patterns=[r"Status[:\s]+offline"],
        notes="FiberHome OLT",
    ),
    
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
    
    Vendor.BDCOM_OLT.value: VendorConfig(
        name="BDCOM OLT",
        disable_paging="terminal length 0",
        show_interface="show interface {interface}",
        show_interface_brief="show card",
        show_interface_status="show epon onu-info interface {interface}",
        show_interface_description="show interface description",
        show_optical_all="show transceiver",
        show_optical_interface="show transceiver interface {interface}",
        show_optical_detail="show transceiver interface {interface}",
        show_onu_optical="show epon optical-transceiver-diagnosis interface {interface}",
        show_onu_list="show epon onu-info interface {interface}",
        rx_power_patterns=[r"Rx\s*Power[:\s]+(-?\d+\.?\d*)"],
        tx_power_patterns=[r"Tx\s*Power[:\s]+(-?\d+\.?\d*)"],
        status_up_patterns=[r"Status[:\s]+online"],
        status_down_patterns=[r"Status[:\s]+offline"],
        notes="BDCOM OLT EPON/GPON",
    ),
    
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
    
    Vendor.VSOL_OLT.value: VendorConfig(
        name="VSOL OLT",
        disable_paging="terminal length 0",
        show_interface="show interface {interface}",
        show_interface_brief="show interface status",
        show_interface_status="show interface status",
        show_interface_description="show interface description",
        show_optical_all="show transceiver",
        show_optical_interface="show transceiver interface {interface}",
        show_optical_detail="show transceiver interface {interface}",
        show_onu_optical="show onu power {interface}",
        show_onu_list="show onu status",
        rx_power_patterns=[r"Rx[:\s]+(-?\d+\.?\d*)"],
        tx_power_patterns=[r"Tx[:\s]+(-?\d+\.?\d*)"],
        status_up_patterns=[r"Status[:\s]+online"],
        status_down_patterns=[r"Status[:\s]+offline"],
        notes="VSOL OLT",
    ),
    
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
    vendor_lower = vendor.lower().strip().replace(" ", "_").replace("-", "_")
    if vendor_lower in VENDOR_CONFIGS:
        return VENDOR_CONFIGS[vendor_lower]
    for key in VENDOR_CONFIGS:
        if vendor_lower in key or key in vendor_lower:
            return VENDOR_CONFIGS[key]
    return VENDOR_CONFIGS[Vendor.GENERIC.value]


def get_supported_vendors() -> List[str]:
    return [v.value for v in Vendor]


def get_optical_commands(vendor: str, interface: str) -> List[str]:
    config = get_vendor_config(vendor)
    commands = []
    
    # Primary commands
    if config.show_optical_interface:
        commands.append(config.show_optical_interface.format(interface=interface))
    if config.show_optical_detail:
        commands.append(config.show_optical_detail.format(interface=interface))
    if config.show_onu_optical:
        commands.append(config.show_onu_optical.format(interface=interface))
    
    # Alternative commands
    for alt_cmd in config.alt_optical_commands:
        if '{interface}' in alt_cmd:
            commands.append(alt_cmd.format(interface=interface))
    
    return list(dict.fromkeys(commands))  # Remove duplicates while preserving order


class OpticalParser:
    def __init__(self, vendor: str = "generic"):
        self.vendor = vendor
        self.config = get_vendor_config(vendor)
    
    def parse_optical_power(self, output: str) -> Dict[str, Any]:
        result = {
            'rx_power': None, 'tx_power': None,
            'rx_power_dbm': 'N/A', 'tx_power_dbm': 'N/A',
            'attenuation': None, 'attenuation_db': 'N/A',
            'signal_status': 'unknown', 'raw_output': output, 'found': False,
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
                except:
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
                except:
                    continue
        
        # Try attenuation patterns
        for pattern in self.config.attenuation_patterns:
            match = re.search(pattern, output, re.IGNORECASE | re.MULTILINE)
            if match:
                try:
                    result['attenuation'] = float(match.group(1))
                    result['attenuation_db'] = f"{result['attenuation']:.2f} dB"
                    break
                except:
                    continue
        
        # Fallback: find any dBm values
        if not result['found']:
            dbm_matches = re.findall(r'(-?\d+\.?\d*)\s*\(?[dD][bB][mM]\)?', output)
            if len(dbm_matches) >= 2:
                try:
                    result['tx_power'] = float(dbm_matches[0])
                    result['rx_power'] = float(dbm_matches[1])
                    result['tx_power_dbm'] = f"{result['tx_power']:.2f} dBm"
                    result['rx_power_dbm'] = f"{result['rx_power']:.2f} dBm"
                    result['found'] = True
                except:
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
            elif rx >= -30:
                result['signal_status'] = 'very_weak'
            else:
                result['signal_status'] = 'critical'
        
        return result
    
    def parse_interface_status(self, output: str) -> str:
        if not output:
            return 'unknown'
        
        # Special handling for MikroTik
        if self.vendor.lower() == 'mikrotik':
            return self._parse_mikrotik_status(output)
        
        # Standard pattern matching for other vendors
        for pattern in self.config.status_up_patterns:
            if re.search(pattern, output, re.IGNORECASE | re.MULTILINE):
                return 'up'
        for pattern in self.config.status_down_patterns:
            if re.search(pattern, output, re.IGNORECASE | re.MULTILINE):
                return 'down'
        return 'unknown'
    
    def _parse_mikrotik_status(self, output: str) -> str:
        """
        Parse MikroTik interface status from output.
        
        MikroTik format:
        - /interface print brief: " 1 RS sfp-sfpplus1   ether"
        - /interface print detail: "flags=X,S running=no disabled=yes"
        
        Flags: R=RUNNING, S=SLAVE, X=DISABLED
        """
        # Check for detail output format first
        if 'running=' in output.lower():
            if re.search(r'running=yes', output, re.IGNORECASE):
                return 'up'
            elif re.search(r'running=no', output, re.IGNORECASE):
                return 'down'
        
        # Check for disabled
        if re.search(r'disabled=yes', output, re.IGNORECASE):
            return 'down'
        
        # Check for brief format (line with number and flags)
        # Format: " 1 RS sfp-sfpplus1" or " 0    ether1"
        lines = output.split('\n')
        for line in lines:
            line = line.strip()
            if not line or not line[0].isdigit():
                continue
            
            parts = line.split()
            if len(parts) < 2:
                continue
            
            # Skip the number, check second part for flags
            # Flags are: R, RS, S, X or empty
            if len(parts) >= 2:
                second_part = parts[1]
                
                # Check if it's a flag
                if len(second_part) <= 3 and all(c in 'RSXrsx' for c in second_part):
                    flags = second_part.upper()
                    if 'R' in flags:
                        return 'up'  # R or RS = RUNNING
                    elif 'X' in flags:
                        return 'down'  # X = DISABLED
                    elif 'S' in flags:
                        return 'up'  # S = SLAVE (usually up if part of bonding)
                else:
                    # No flag column, means not running
                    # But check if the interface name is in the output
                    # This could be a "down" interface
                    return 'down'
        
        return 'unknown'
    
    def parse_description(self, output: str) -> str:
        if not output or not self.config.description_pattern:
            return ''
        match = re.search(self.config.description_pattern, output, re.IGNORECASE)
        return match.group(1).strip() if match else ''


# =============================================================================
# SPECIAL INTERFACE PARSERS
# =============================================================================

def parse_mikrotik_interfaces(output: str) -> List[Dict[str, Any]]:
    """
    Parse MikroTik /interface print output
    
    Supports multiple formats:
    
    Format 1 (brief):
    Flags: R - RUNNING; S - SLAVE
    Columns: NAME, TYPE, ACTUAL-MTU, L2MTU, MAX-L2MTU, MAC-ADDRESS
     #    NAME           TYPE      ACTUAL-MTU  L2MTU  MAX-L2MTU  MAC-ADDRESS      
     0    ether1         ether           1500   1584      10218  48:8F:5A:05:51:79
     1 RS sfp-sfpplus1   ether           1500   1584      10218  48:8F:5A:05:51:69
    
    Format 2 (standard):
    Flags: D - dynamic, X - disabled, R - running, S - slave
     #     NAME            TYPE       ACTUAL-MTU L2MTU
     0  R  ether1          ether            1500  1598
     1  RS sfp-sfpplus1    ether            1500  1598
    
    Flags:
    - R = RUNNING (UP)
    - RS = RUNNING + SLAVE (UP)
    - S = SLAVE only 
    - X = DISABLED (DOWN)
    - D = DYNAMIC
    - (empty) = not running (DOWN)
    """
    interfaces = []
    
    if not output:
        return interfaces
    
    # Clean output - remove ANSI escape codes
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    output = ansi_escape.sub('', output)
    
    lines = output.split('\n')
    current_comment = ''
    
    for line in lines:
        original_line = line
        line = line.strip()
        
        if not line:
            continue
        
        # Skip header lines
        if line.startswith('Flags:') or line.startswith('Columns:'):
            continue
        
        # Skip column header lines
        if 'NAME' in line and ('TYPE' in line or 'MTU' in line):
            continue
        
        # Skip prompt lines
        if line.endswith('>') or line.endswith('#') or '[admin@' in line:
            continue
        
        # Skip banner/logo lines (MikroTik ASCII art)
        if 'MikroTik' in line or 'MMM' in line or 'MMMM' in line:
            continue
        if all(c in 'MTKR |-_/\\' for c in line.replace(' ', '')):
            continue
        
        # Capture comment lines (;;; description)
        if line.startswith(';;;'):
            current_comment = line[3:].strip()
            continue
        
        # Interface lines start with a number
        # Match: "0", " 0", "0 ", " 0 R", etc.
        match = re.match(r'^(\d+)\s+(.*)$', line)
        if not match:
            continue
        
        num = match.group(1)
        rest = match.group(2).strip()
        
        if not rest:
            continue
        
        # Parse the rest: "[FLAGS] NAME [TYPE] [MTU] ..."
        parts = rest.split()
        if not parts:
            continue
        
        # Determine if first part is flags or name
        flags = ''
        name_idx = 0
        
        first_part = parts[0]
        
        # Check if first part looks like flags (R, RS, S, X, D, DR, DRS, etc.)
        # Flags contain only R, S, X, D and are typically 1-3 chars
        if len(first_part) <= 4 and all(c in 'RSDXrsdx' for c in first_part):
            flags = first_part.upper()
            name_idx = 1
        
        # Get interface name
        if name_idx >= len(parts):
            continue
        
        name = parts[name_idx]
        
        # Skip invalid names
        if not name or name.startswith(';;;') or name.startswith('['):
            continue
        
        # Skip if name looks like a type or number
        if name.lower() in ['ether', 'bond', 'bridge', 'vlan', 'loopback', 'pppoe', 'gre', 'ipip']:
            continue
        
        # Determine status based on flags
        # R = RUNNING = UP
        # RS = RUNNING + SLAVE = UP  
        # S = SLAVE = UP (part of bonding)
        # X = DISABLED = DOWN
        # D = DYNAMIC (depends on R flag)
        # (empty) = not running = DOWN
        
        if 'R' in flags:
            status = 'up'
        elif 'X' in flags:
            status = 'down'
        elif 'S' in flags:
            status = 'up'  # Slave typically means active
        else:
            status = 'down'
        
        # Get type if available
        iface_type = ''
        if len(parts) > name_idx + 1:
            potential_type = parts[name_idx + 1].lower()
            if potential_type in ['ether', 'bond', 'bridge', 'vlan', 'loopback', 'pppoe', 'gre', 'ipip', 'ovpn']:
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


def parse_zte_olt_interfaces(output: str) -> List[Dict[str, Any]]:
    """Parse ZTE OLT show card output"""
    interfaces = []
    
    if not output:
        return interfaces
    
    lines = output.split('\n')
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # ZTE OLT card output usually shows slots/cards
        # Look for GPON/EPON cards
        if 'GTGO' in line or 'GTGH' in line or 'ETGO' in line or 'GPON' in line:
            parts = line.split()
            if len(parts) >= 2:
                # First part is usually slot number
                slot = parts[0]
                card_type = parts[1] if len(parts) > 1 else 'Unknown'
                status = 'up' if 'INSERVICE' in line or 'online' in line.lower() else 'unknown'
                
                interfaces.append({
                    'name': f"Slot {slot}",
                    'status': status,
                    'description': card_type,
                })
    
    return interfaces


INTERFACE_ALIASES = {
    'gi': 'GigabitEthernet', 'gig': 'GigabitEthernet',
    'fa': 'FastEthernet', 'te': 'TenGigabitEthernet',
    'eth': 'Ethernet', 'ge': 'GigabitEthernet',
    'xge': 'XGigabitEthernet', '10ge': '10GE',
    '25ge': '25GE', '40ge': '40GE', '100ge': '100GE',
}


def expand_interface_name(short_name: str) -> str:
    for full in INTERFACE_ALIASES.values():
        if short_name.lower().startswith(full.lower()):
            return short_name
    for alias, full in INTERFACE_ALIASES.items():
        if short_name.lower().startswith(alias):
            return f"{full}{short_name[len(alias):]}"
    return short_name