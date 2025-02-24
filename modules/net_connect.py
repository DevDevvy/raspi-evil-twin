#!/usr/bin/env python3

import subprocess

def run_cmd(cmd):
    return subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT).decode("utf-8").strip()

def connect_to_open_wifi(ssid, interface):
    """
    Uses nmcli to connect to an open Wi-Fi network by SSID on the specified interface.
    Returns True on success, False on failure.
    """
    try:
        output = run_cmd(f"nmcli device wifi connect \"{ssid}\" ifname {interface} --no-passwd")
        # nmcli will throw a CalledProcessError if it fails
        print(f"[INFO - net_connect] Connected to open Wi-Fi: {ssid}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERROR - net_connect] Failed to connect to SSID: {ssid}")
        print(e.output)
        return False
