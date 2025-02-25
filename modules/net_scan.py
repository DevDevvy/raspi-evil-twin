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
    """
    networks = []
    try:
        # Example: nmcli -f SSID,SECURITY,SIGNAL,CHAN dev wifi list ifname wlan0 --rescan yes
        output = run_cmd(f"sudo iwlist {interface} scan")
    except Exception as e:
        print(f"[ERROR - net_scan] Could not scan for networks: {e}")
        return []

    ssid, channel, signal, encryption = None, None, None, None
    for line in output.split("\n"):
        line = line.strip()
        if "ESSID" in line:
            ssid = re.search(r'ESSID:"(.*?)"', line).group(1)
        elif "Frequency" in line:
            channel = int(float(re.search(r"Frequency:([\d.]+)", line).group(1)) * 10)
        elif "Quality=" in line:
            signal = int(line.split("Signal level=")[1].split()[0].strip("+"))
        elif "Encryption key:off" in line:
            encryption = False
        
        if ssid and signal and channel is not None and encryption is False:
            networks.append({"ssid": ssid, "signal": signal, "channel": channel})
            ssid, channel, signal, encryption = None, None, None, None  # Reset for next network

    return sorted(networks, key=lambda x: x["signal"], reverse=True)

def pick_strongest_open_network(networks):
    """
    Selects the strongest open Wi-Fi network.
    """
    return networks[0] if networks else None
