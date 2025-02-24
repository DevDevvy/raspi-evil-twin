#!/usr/bin/env python3

import subprocess
import re

def run_cmd(cmd):
    """
    Utility to run a shell command and return stdout as a string.
    Raises subprocess.CalledProcessError on errors.
    """
    return subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT).decode("utf-8").strip()

def scan_for_open_networks(interface):
    """
    Scans for open (unencrypted) Wi-Fi networks using nmcli on the specified interface.
    Returns a list of dicts: [{'ssid': SSID, 'signal': int, 'channel': int}, ...]
    """
    networks = []
    try:
        # Example: nmcli -f SSID,SECURITY,SIGNAL,CHAN dev wifi list ifname wlan0 --rescan yes
        output = run_cmd(f"nmcli -f SSID,SECURITY,SIGNAL,CHAN device wifi list ifname {interface} --rescan yes")
    except subprocess.CalledProcessError as e:
        print("[ERROR - net_scan] Could not scan for networks.")
        print(e.output)
        return networks  # Return empty list

    for line in output.split("\n"):
        line = line.strip()
        if not line or "SSID" in line or "IN-USE" in line:
            # Skip header lines or empty lines
            continue

        # Example line might look like: "MyOpenWiFi  --  70  6"
        # We can split on multiple spaces
        parts = re.split(r"\s{2,}", line)
        if len(parts) < 4:
            continue

        ssid = parts[0].strip()
        security = parts[1].strip()
        signal_str = parts[2].strip()
        channel_str = parts[3].strip()

        if security == "--":  # means open network
            try:
                signal_int = int(signal_str)
            except ValueError:
                signal_int = 0
            try:
                channel_int = int(channel_str)
            except ValueError:
                channel_int = 6  # fallback

            networks.append({
                "ssid": ssid,
                "signal": signal_int,
                "channel": channel_int
            })

    return networks

def pick_strongest_open_network(networks):
    """
    From the list of open networks, pick the strongest by signal.
    Returns a dict with {ssid, signal, channel} or None if empty.
    """
    if not networks:
        return None
    sorted_networks = sorted(networks, key=lambda x: x["signal"], reverse=True)
    return sorted_networks[0]
