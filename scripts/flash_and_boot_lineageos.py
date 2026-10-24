#!/usr/bin/env python3
"""
scripts/flash_and_boot_lineageos.py
Performs verified flashing of LineageOS 16.0 boot.img and system.img to Lenovo Tab M7 (TB-7305X).
"""

import subprocess
import hashlib
import sys
import os
import time

SERIAL = "HA154H1C"
FASTBOOT_PATH = r"C:\Users\ayush\Downloads\platform-tools-latest-windows\platform-tools\fastboot.exe"
ADB_PATH = r"C:\Users\ayush\Downloads\platform-tools-latest-windows\platform-tools\adb.exe"

BUILD_DIR = r"E:\Project\Lenovo Tab tb-7305x\tb7305x-lab\builds\lineage-16.0-mt8765_P-40065716148"
BOOT_IMG = os.path.join(BUILD_DIR, "boot.img")
SYSTEM_IMG = os.path.join(BUILD_DIR, "system.img")

EXPECTED_BOOT_SHA256 = "609A1DB89505077F13CDADF0110BA68FD5ED42BF77DB1B1A1F2F257C544D568E"
EXPECTED_SYS_SHA256 = "5669FC2FD65F1AB02D2072923DCAC468F47385A6CA851F2DA5CFC764DE813D5D"

def hash_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(1024 * 1024):
            h.update(chunk)
    return h.hexdigest().upper()

def run_cmd(cmd, check=True):
    print(f"\n>>> Running: {' '.join(cmd)}")
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if res.stdout:
        print(res.stdout.strip())
    if res.stderr:
        print(res.stderr.strip())
    if check and res.returncode != 0:
        raise RuntimeError(f"Command failed with exit code {res.returncode}")
    return res

def main():
    print("=" * 70)
    print("Lenovo Tab M7 (TB-7305X) LineageOS 16.0 Fastboot Flash & Boot Installer")
    print("=" * 70)

    # 1. Verify Image files
    print("\n[1/6] Verifying Target Images & Cryptographic Hashes...")
    for name, path, expected in [("boot.img", BOOT_IMG, EXPECTED_BOOT_SHA256), ("system.img", SYSTEM_IMG, EXPECTED_SYS_SHA256)]:
        if not os.path.exists(path):
            print(f"[ERROR] Image not found: {path}")
            sys.exit(1)
        actual = hash_file(path)
        print(f"  {name}: {os.path.getsize(path):,} bytes | SHA-256: {actual}")
        if actual != expected:
            print(f"[ERROR] Checksum mismatch for {name}! Expected: {expected}")
            sys.exit(1)
    print("  [PASS] All cryptographic hashes verified.")

    # 2. Check current device state
    print("\n[2/6] Checking attached device via ADB...")
    res = run_cmd([ADB_PATH, "devices"], check=False)
    if SERIAL in res.stdout:
        print(f"  Detected {SERIAL} via ADB. Rebooting to bootloader...")
        run_cmd([ADB_PATH, "-s", SERIAL, "reboot", "bootloader"], check=False)
    else:
        print("  Device not in ADB; checking fastboot directly...")

    # 3. Poll for fastboot enumeration
    print("\n[3/6] Polling for fastboot device enumeration...")
    fastboot_ready = False
    for attempt in range(15):
        time.sleep(2)
        res = subprocess.run([FASTBOOT_PATH, "devices"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if SERIAL in res.stdout or (res.stdout and "fastboot" in res.stdout):
            print(f"  Detected fastboot device: {res.stdout.strip()}")
            fastboot_ready = True
            break
        print(f"  Waiting for fastboot... ({attempt+1}/15)")

    if not fastboot_ready:
        print("[ERROR] Device did not enumerate in Fastboot mode.")
        sys.exit(1)

    # Query device parameters
    print("\n[4/6] Querying Fastboot Device Variables...")
    run_cmd([FASTBOOT_PATH, "getvar", "product"], check=False)
    run_cmd([FASTBOOT_PATH, "getvar", "unlocked"], check=False)
    run_cmd([FASTBOOT_PATH, "getvar", "max-download-size"], check=False)

    # 4. Flash boot.img
    print("\n[5/6] Flashing LineageOS 16.0 boot.img...")
    run_cmd([FASTBOOT_PATH, "flash", "boot", BOOT_IMG])

    # 5. Flash system.img
    print("\n[6/6] Flashing LineageOS 16.0 system.img (Sparse ext4)...")
    run_cmd([FASTBOOT_PATH, "flash", "system", SYSTEM_IMG])

    # 6. Reboot device
    print("\n>>> Flashing complete! Rebooting device into LineageOS 16.0...")
    run_cmd([FASTBOOT_PATH, "reboot"])
    print("\n" + "=" * 70)
    print("SUCCESS: Device rebooted into LineageOS 16.0!")
    print("=" * 70)

if __name__ == '__main__':
    main()
