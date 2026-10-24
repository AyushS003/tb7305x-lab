#!/usr/bin/env bash
# Lenovo Tab M7 (TB-7305X) - Flash Halium 9.0 Boot Partition
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "================================================================"
echo "  Lenovo Tab M7 (TB-7305X) - Flash Halium 9.0 Boot Partition"
echo "================================================================"
echo ""
echo " WARNING:"
echo " This will overwrite the current 'boot' partition with halium-boot.img."
echo " To revert back to LineageOS later, reflash the LineageOS boot.img."
echo ""
read -r -p "Type 'YES' to proceed with flashing boot partition: " CONFIRM
if [ "$CONFIRM" != "YES" ]; then
    echo "[ABORTED] Flashing cancelled."
    exit 0
fi

if ! command -v fastboot &> /dev/null; then
    echo "[ERROR] 'fastboot' was not found in your PATH."
    exit 1
fi

if [ ! -f "$SCRIPT_DIR/halium-boot.img" ]; then
    echo "[ERROR] halium-boot.img was not found!"
    exit 1
fi

echo "[*] Flashing boot partition with halium-boot.img..."
fastboot flash boot "$SCRIPT_DIR/halium-boot.img"

echo ""
echo "[*] Rebooting tablet into Halium 9.0..."
fastboot reboot

echo ""
echo "================================================================"
echo "[SUCCESS] Halium 9.0 boot partition flashed successfully!"
echo "================================================================"
