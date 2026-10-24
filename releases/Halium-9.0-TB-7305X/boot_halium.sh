#!/usr/bin/env bash
# Lenovo Tab M7 (TB-7305X) - Halium 9.0 Live Boot
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "================================================================"
echo "  Lenovo Tab M7 (TB-7305X) - Halium 9.0 Live Boot Test"
echo "================================================================"
echo ""
echo " This script boots Halium 9.0 in live mode using 'fastboot boot'."
echo " Your existing ROM (LineageOS) and boot partition will NOT be touched!"
echo ""

if ! command -v fastboot &> /dev/null; then
    echo "[ERROR] 'fastboot' command was not found in your PATH."
    echo "Please install android-tools-fastboot or platform-tools."
    exit 1
fi

if [ ! -f "$SCRIPT_DIR/halium-boot.img" ]; then
    echo "[ERROR] halium-boot.img was not found in $SCRIPT_DIR!"
    exit 1
fi

echo "[*] Checking fastboot device connection..."
fastboot devices
echo ""

echo "[*] Booting Halium 9.0 live kernel into device RAM..."
fastboot boot "$SCRIPT_DIR/halium-boot.img"

echo ""
echo "================================================================"
echo "[SUCCESS] Halium 9.0 kernel dispatched to TB-7305X RAM!"
echo ""
echo "Next Steps for Halium Debugging:"
echo "  1. The tablet screen may remain black or show the Lenovo splash."
echo "  2. A USB Ethernet / RNDIS network interface will appear (e.g., usb0)."
echo "  3. Configure your interface:"
echo "       sudo ip addr add 192.168.2.1/24 dev usb0"
echo "       sudo ip link set usb0 up"
echo "  4. Connect to Halium initramfs shell:"
echo "       telnet 192.168.2.15"
echo "  5. Inspect kernel logs:"
echo "       dmesg | grep -i error"
echo "================================================================"
