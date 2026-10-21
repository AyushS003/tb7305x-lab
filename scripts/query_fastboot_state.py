import subprocess
import time
import sys
import os

ADB = r"C:\Users\ayush\Downloads\platform-tools-latest-windows\platform-tools\adb.exe"
FASTBOOT = r"C:\Users\ayush\Downloads\platform-tools-latest-windows\platform-tools\fastboot.exe"
SERIAL = "HA154H1C"

def run_cmd(cmd_list, timeout=15):
    try:
        p = subprocess.run(cmd_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="replace", timeout=timeout)
        return p.returncode, p.stdout.strip(), p.stderr.strip()
    except subprocess.TimeoutExpired:
        return -1, "", "TIMEOUT"

def main():
    print("=================================================================")
    print("Lenovo Tab M7 (TB-7305X) Non-Destructive Fastboot Query Diagnostic")
    print(f"Target Serial: {SERIAL}")
    print("=================================================================\n")

    # Step 1: Verify current ADB connectivity
    print("[1/5] Checking current ADB connection...")
    code, out, err = run_cmd([ADB, "-s", SERIAL, "get-state"])
    print(f"  ADB State: {out} (code: {code})")
    if out != "device":
        print("Error: Device is not ready in ADB mode. Aborting.")
        sys.exit(1)

    code, build, _ = run_cmd([ADB, "-s", SERIAL, "shell", "getprop", "ro.build.display.id"])
    print(f"  Running OS Build: {build}\n")

    # Step 2: Reboot to bootloader
    print("[2/5] Rebooting device to bootloader (Fastboot mode)...")
    code, out, err = run_cmd([ADB, "-s", SERIAL, "reboot", "bootloader"])
    print(f"  Issued 'adb reboot bootloader' (code: {code})")
    time.sleep(3)

    # Step 3: Poll for fastboot device
    print("[3/5] Polling for fastboot enumeration...")
    fastboot_detected = False
    start_time = time.time()
    while time.time() - start_time < 30:
        code, out, err = run_cmd([FASTBOOT, "devices"])
        if out:
            print(f"  Detected Fastboot Device: {out}")
            fastboot_detected = True
            break
        time.sleep(2)
        print(".", end="", flush=True)
    print()

    fastboot_results = {}
    if fastboot_detected:
        print("\n--- FASTBOOT READ-ONLY QUERIES ---")
        for var in ["all", "unlocked", "secure", "product", "version-bootloader", "version-baseband", "partition-type:recovery", "partition-size:recovery"]:
            code, out, err = run_cmd([FASTBOOT, "getvar", var], timeout=5)
            combined = (out + "\n" + err).strip()
            print(f"  fastboot getvar {var}:")
            for line in combined.splitlines():
                if line.strip():
                    print(f"    {line}")
            fastboot_results[var] = combined

        print("\n[4/5] Rebooting back to Android OS via fastboot...")
        code, out, err = run_cmd([FASTBOOT, "reboot"])
        print(f"  Issued 'fastboot reboot': {out} {err} (code: {code})")
    else:
        print("\n[WARNING]: Device did not enumerate via Fastboot USB interface.")
        print("  Possible causes: Fastboot USB VID/PID driver not bound in Windows or device still in transition.")
        print("  Attempting blind 'fastboot reboot'...")
        run_cmd([FASTBOOT, "reboot"], timeout=5)

    # Step 5: Wait for Android OS to boot back up and verify ADB
    print("\n[5/5] Waiting for Android OS to boot up and reconnect to ADB...")
    adb_reconnected = False
    start_reboot = time.time()
    while time.time() - start_reboot < 90:
        code, out, err = run_cmd([ADB, "-s", SERIAL, "get-state"])
        if out == "device":
            adb_reconnected = True
            break
        time.sleep(3)
        print(".", end="", flush=True)
    print()

    if adb_reconnected:
        code, uptime, _ = run_cmd([ADB, "-s", SERIAL, "shell", "cat", "/proc/uptime"])
        code, post_build, _ = run_cmd([ADB, "-s", SERIAL, "shell", "getprop", "ro.build.display.id"])
        print(f"[PASS] Successfully reconnected to ADB in Android OS!")
        print(f"  Running OS Build: {post_build}")
        print(f"  System Uptime: {uptime} seconds")
    else:
        print("[FAIL] Did not reconnect to ADB within 90 seconds.")

    print("\n=================================================================")
    print("Fastboot Diagnostic Run Complete.")
    print("=================================================================")

if __name__ == "__main__":
    main()
