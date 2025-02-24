#!/usr/bin/env python3

import os
import subprocess
import sys

def run_cmd(cmd):
    return subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT).decode("utf-8").strip()

def write_hostapd_config(template_path, output_path, ap_interface, cloned_ssid, channel):
    """
    Reads a template, replaces placeholders, writes to output_path.
    """
    if not os.path.exists(template_path):
        raise FileNotFoundError(f"[ERROR - ap_config] hostapd template not found at {template_path}")

    with open(template_path, "r") as f:
        template = f.read()

    config_data = template.replace("{{AP_INTERFACE}}", ap_interface)
    config_data = config_data.replace("{{CLONED_SSID}}", cloned_ssid)
    config_data = config_data.replace("{{CHANNEL}}", str(channel))

    with open(output_path, "w") as f:
        f.write(config_data)

def write_dnsmasq_config(template_path, output_path, ap_interface,
                         ap_ip, dhcp_range_start, dhcp_range_end, netmask):
    """
    Reads a dnsmasq config template, replaces placeholders.
    """
    if not os.path.exists(template_path):
        raise FileNotFoundError(f"[ERROR - ap_config] dnsmasq template not found at {template_path}")

    with open(template_path, "r") as f:
        template = f.read()

    config_data = template.replace("{{AP_INTERFACE}}", ap_interface)
    config_data = config_data.replace("{{AP_IP}}", ap_ip)
    config_data = config_data.replace("{{DHCP_RANGE_START}}", dhcp_range_start)
    config_data = config_data.replace("{{DHCP_RANGE_END}}", dhcp_range_end)
    config_data = config_data.replace("{{NETMASK}}", netmask)

    with open(output_path, "w") as f:
        f.write(config_data)

def configure_ap_interface(ap_interface, ap_ip):
    """
    Assign static IP to the AP interface, bring it up.
    """
    try:
        run_cmd(f"sudo ip link set {ap_interface} down")
        run_cmd(f"sudo ip addr flush dev {ap_interface}")
        run_cmd(f"sudo ip addr add {ap_ip}/24 dev {ap_interface}")
        run_cmd(f"sudo ip link set {ap_interface} up")
        print(f"[INFO - ap_config] {ap_interface} configured with IP {ap_ip}/24.")
    except subprocess.CalledProcessError as e:
        print(f"[ERROR - ap_config] Failed to configure AP interface {ap_interface}")
        print(e.output)
        sys.exit(1)

def start_hostapd_dnsmasq():
    """
    Stops existing services, clears old leases, restarts them with updated configs.
    """
    try:
        run_cmd("sudo systemctl stop hostapd || true")
        run_cmd("sudo systemctl stop dnsmasq || true")

        # Remove old DHCP leases if any
        run_cmd("sudo rm -f /var/lib/misc/dnsmasq.leases")

        run_cmd("sudo systemctl start dnsmasq")
        run_cmd("sudo systemctl start hostapd")

        print("[INFO - ap_config] hostapd and dnsmasq started successfully.")
    except subprocess.CalledProcessError as e:
        print("[ERROR - ap_config] Failed to start services.")
        print(e.output)
        sys.exit(1)
