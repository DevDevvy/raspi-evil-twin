#!/usr/bin/env python3

import subprocess
import sys

def run_cmd(cmd):
    return subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT).decode("utf-8").strip()

def enable_nat(sta_iface, ap_iface):
    """
    Enable IP forwarding and set up iptables NAT rules so traffic from the AP
    is forwarded out via the STA interface.
    """
    try:
        # Enable kernel IP forwarding
        run_cmd("sudo sysctl -w net.ipv4.ip_forward=1")

        # Flush existing NAT rules first (optional but safer for repeated runs)
        run_cmd("sudo iptables -t nat -F")
        run_cmd("sudo iptables -F FORWARD")

        # NAT rule (masquerade)
        run_cmd(f"sudo iptables -t nat -A POSTROUTING -o {sta_iface} -j MASQUERADE")

        # Forward traffic from AP to STA
        run_cmd(f"sudo iptables -A FORWARD -i {ap_iface} -o {sta_iface} -j ACCEPT")
        run_cmd(f"sudo iptables -A FORWARD -i {sta_iface} -o {ap_iface} -m state --state ESTABLISHED,RELATED -j ACCEPT")

        print("[INFO - nat_config] NAT/masquerade rules applied.")
    except subprocess.CalledProcessError as e:
        print("[ERROR - nat_config] Failed to set iptables NAT rules.")
        print(e.output)
        sys.exit(1)
