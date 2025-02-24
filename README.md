# Raspberry Pi Evil Twin Automation

**Disclaimer**: This project is for authorized security research and legal pentesting **only**.  
Do **not** use it to intercept or manipulate network traffic on any network you do not own or have explicit written permission to test.

## Overview

This repository contains Python scripts that automate:

1. Scanning for open (unencrypted) Wi-Fi networks
2. Connecting to the strongest open network on `STA_INTERFACE`
3. Matching the real AP's channel (when possible)
4. Setting up a cloned Evil Twin AP on `AP_INTERFACE`
5. Forwarding traffic via NAT

**Tested on**: Raspberry Pi Zero W / Pi 3 / Pi 4 with Raspberry Pi OS (Debian-based)  
**Dependencies**: `nmcli`, `hostapd`, `dnsmasq`, `iptables` (installed via `apt`), plus Python 3.

## Installation

1. **Clone this repo**:
   ```bash
   git clone https://github.com/YourName/auto_evil_twin.git
   cd auto_evil_twin
   ```
