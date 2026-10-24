#!/usr/bin/env bash
# Lenovo Tab M7 (TB-7305X) LineageOS 16.0 & TWRP Fastboot Installer

set -e

echo "===================================================================="
echo "     Lenovo Tab M7 (TB-7305X) LineageOS 16.0 Fastboot Installer"
echo "===================================================================="
echo ""
echo "This tool will flash:"
echo "  1. TWRP 3.3.1 Custom Recovery     [recovery.img]"
echo "  2. LineageOS 16.0 Kernel           [boot.img]"
echo "  3. LineageOS 16.0 System Image     [system.img]"
echo ""
echo "Ensure your tablet is connected in FASTBOOT mode ('FASTBOOT mode...')."
echo ""
read -rp "Press [Enter] to start flashing, or Ctrl+C to cancel..."

echo ""
echo "[1/4] Checking fastboot device connection..."
fastboot devices
echo ""

echo "[2/4] Flashing TWRP Custom Recovery..."
fastboot flash recovery recovery.img
echo "[PASS] Recovery flashed successfully."

echo ""
echo "[3/4] Flashing LineageOS 16.0 Boot Kernel..."
fastboot flash boot boot.img
echo "[PASS] Boot kernel flashed successfully."

echo ""
echo "[4/4] Flashing LineageOS 16.0 System-as-Root Image..."
echo "(Please wait, this will take approximately 1-2 minutes...)"
fastboot flash system system.img
echo "[PASS] System partition flashed successfully."

echo ""
echo "===================================================================="
echo "                FLASHING COMPLETED SUCCESSFULLY!"
echo "===================================================================="
echo ""
echo "IMPORTANT: If this is your first time installing LineageOS on a stock tablet:"
echo " 1. You must format data in TWRP to remove stock encryption!"
echo " 2. To do so, reboot to TWRP: Wipe -> Format Data -> type 'yes'"
echo ""
read -rp "Do you want to reboot into TWRP Recovery now? (y/n): " choice
if [[ "$choice" =~ ^[Yy]$ ]]; then
    echo "Rebooting into TWRP Recovery..."
    fastboot reboot recovery
else
    echo "Rebooting into LineageOS 16.0..."
    fastboot reboot
fi

echo ""
echo "Done! Enjoy LineageOS 16.0 on your Lenovo Tab M7!"
