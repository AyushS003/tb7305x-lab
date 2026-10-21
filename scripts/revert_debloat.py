import subprocess
import json
import os
import sys

SERIAL = "HA154H1C"
ADB_PATH = r"C:\Users\ayush\Downloads\platform-tools-latest-windows\platform-tools\adb.exe"
LOGS_DIR = r"E:\Project\Lenovo Tab tb-7305x\tb7305x-lab\logs"

def run_adb_shell(cmd):
    p = subprocess.run([ADB_PATH, "-s", SERIAL, "shell", cmd], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="replace")
    return p.returncode, p.stdout.strip(), p.stderr.strip()

def main():
    print("=====================================================")
    print("Lenovo Tab M7 (TB-7305X) Debloat Reversion Tool")
    print(f"Target Serial: {SERIAL}")
    print("=====================================================\n")

    log_file = os.path.join(LOGS_DIR, "debloat_action_log.json")
    if not os.path.exists(log_file):
        print(f"Error: {log_file} does not exist. Nothing to revert.")
        return

    with open(log_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    uninstalled = data.get("uninstalled", [])
    if not uninstalled:
        print("No uninstalled packages found in log.")
        return

    print(f"Found {len(uninstalled)} packages to restore.\n")
    restored = 0
    for item in uninstalled:
        pkg = item["package"]
        desc = item.get("description", "")
        print(f"Restoring: {pkg:<40} ({desc})...", end=" ")
        code, out, err = run_adb_shell(f"cmd package install-existing {pkg}")
        if "installed for user" in out or "Package" in out or code == 0:
            print("[RESTORED]")
            restored += 1
        else:
            print(f"[STATUS: {out}]")

    print(f"\nReversion complete. Successfully restored {restored} packages.")

if __name__ == "__main__":
    main()
