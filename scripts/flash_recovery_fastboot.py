import subprocess
import hashlib
import sys
import os

SERIAL = "HA154H1C"
FASTBOOT_PATH = r"C:\Users\ayush\Downloads\platform-tools-latest-windows\platform-tools\fastboot.exe"
ADB_PATH = r"C:\Users\ayush\Downloads\platform-tools-latest-windows\platform-tools\adb.exe"
RECOVERY_IMG = r"E:\Project\Lenovo Tab tb-7305x\tb7305x-lab\recovery\twrp_lenovo_7305x_recovery.img"
EXPECTED_SHA256 = "79657A7BD1D5EC90B0B027F3509807D05C2B2F7DA49932109210DACBA1DFA7C9"

def verify_checksum(path, expected):
    if not os.path.exists(path):
        return False, f"File {path} does not exist"
    hasher = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    actual = hasher.hexdigest().upper()
    return (actual == expected.upper()), actual

def main():
    print("==================================================================")
    print("Lenovo Tab M7 (TB-7305X) Custom Recovery (TWRP) Fastboot Installer")
    print("==================================================================")
    
    # 1. Verify Image Checksum
    valid, actual_hash = verify_checksum(RECOVERY_IMG, EXPECTED_SHA256)
    print(f"Target Image: {RECOVERY_IMG}")
    print(f"File Size:    {os.path.getsize(RECOVERY_IMG):,} bytes")
    print(f"SHA-256 Hash: {actual_hash}")
    if not valid:
        print("[ERROR] SHA-256 verification FAILED. Aborting.")
        sys.exit(1)
    print("[PASS] SHA-256 Checksum verified.\n")

    # Safety Notice
    print("PLANNED ACTION:")
    print("1. Reboot device to bootloader: adb -s HA154H1C reboot bootloader")
    print("2. Flash recovery partition:    fastboot flash recovery <image>")
    print("3. Reboot to TWRP:              fastboot reboot recovery\n")

    if "--execute" not in sys.argv:
        print("------------------------------------------------------------------")
        print("SAFETY GUARD ACTIVE: Explicit user approval required.")
        print("To execute this operation after obtaining user approval, run:")
        print("    python flash_recovery_fastboot.py --execute")
        print("------------------------------------------------------------------")
        return

    # Execution path only if explicitly approved
    print("Rebooting device into bootloader...")
    subprocess.run([ADB_PATH, "-s", SERIAL, "reboot", "bootloader"])
    print("Waiting 10 seconds for bootloader enumeration...")
    import time
    time.sleep(10)

    print("Checking fastboot devices...")
    fb_dev = subprocess.run([FASTBOOT_PATH, "devices"], stdout=subprocess.PIPE, text=True)
    print(fb_dev.stdout)

    print(f"Flashing recovery partition with {RECOVERY_IMG}...")
    flash_res = subprocess.run([FASTBOOT_PATH, "flash", "recovery", RECOVERY_IMG], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    print("Stdout:", flash_res.stdout)
    print("Stderr:", flash_res.stderr)

    if flash_res.returncode == 0:
        print("[SUCCESS] Recovery flashed successfully.")
        print("Rebooting directly into recovery mode...")
        subprocess.run([FASTBOOT_PATH, "reboot", "recovery"])
    else:
        print(f"[FAILED] Fastboot returned exit code {flash_res.returncode}")

if __name__ == "__main__":
    main()
