#!/usr/bin/env python3

import subprocess
import time
import os

def run_cmd(cmd):
    return subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT).decode("utf-8").strip()

def connect_to_open_wifi(ssid, interface="wlan0"):
    """
    Connects to an open Wi-Fi network using wpa_supplicant.
    """
    wpa_supplicant_config = "/etc/wpa_supplicant/wpa_supplicant.conf"
    
    # Create a temporary wpa_supplicant config
    config_content = f"""
    network={{
        ssid="{ssid}"
        key_mgmt=NONE
    }}
    """

    with open(wpa_supplicant_config, "w") as f:
        f.write(config_content)

    try:
        run_cmd(f"sudo wpa_supplicant -B -i {interface} -c {wpa_supplicant_config}")
        time.sleep(5)  # Give it time to connect
        run_cmd(f"sudo dhclient {interface}")  # Get an IP address
        print(f"[INFO - net_connect] Connected to {ssid}")
        return True
    except Exception as e:
        print(f"[ERROR - net_connect] Failed to connect: {e}")
        return False
