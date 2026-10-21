import subprocess
import json
import os
import sys

SERIAL = "HA154H1C"
ADB_PATH = r"C:\Users\ayush\Downloads\platform-tools-latest-windows\platform-tools\adb.exe"
LOGS_DIR = r"E:\Project\Lenovo Tab tb-7305x\tb7305x-lab\logs"

# List of safe, non-essential bloatware, telemetry, and promotional apps
SAFE_DEBLOAT_PACKAGES = [
    # Lenovo Telemetry & Push Services
    ("com.lenovo.ue.device", "Lenovo User Experience Telemetry"),
    ("com.lenovo.lsf.device", "Lenovo Push Out Service"),
    ("com.lenovo.lsf", "Lenovo ID / Account Service"),
    ("com.lenovo.dsa", "Lenovo Deploy Service"),
    ("com.lenovo.ocpl", "Lenovo Client Downloader"),
    ("com.tblenovo.whatsnewclient", "Lenovo WhatsNew Client"),
    ("com.tblenovo.whatsnewhost", "Lenovo WhatsNew Host"),
    ("com.tblenovo.lenovotips", "Lenovo Tips Assistant"),
    ("com.huaqin.lenovoprivacy", "Lenovo Privacy Daemon"),
    ("com.lmsa.app.lmsapad", "Lenovo Rescue and Smart Assistant Diagnostics"),
    
    # MediaTek Debugging Loggers (generates heavy disk I/O in background)
    ("com.mediatek.mtklogger", "MediaTek Background Logger Daemon"),
    
    # OEM Pre-installs & Unused Third Party
    ("ru.yandex.searchplugin", "Yandex Search Plugin"),
    ("com.yandex.browser", "Yandex Browser Preinstall"),
    ("com.motorola.demo", "Motorola Demo Mode"),
    
    # Unused Pre-installed Themes
    ("jp.co.fsi.fskaren.lenovo.theme.aqua", "Theme Aqua"),
    ("jp.co.fsi.fskaren.lenovo.theme.wood", "Theme Wood"),
    ("jp.co.fsi.fskaren.lenovo.theme.stylish", "Theme Stylish"),
    ("jp.co.fsi.fskaren.lenovo.theme.sf", "Theme Sci-Fi"),
    ("jp.co.fsi.fskaren.lenovo.theme.decoCute", "Theme Deco Cute"),
    ("jp.co.fsi.fskaren.lenovo.theme.decoKira", "Theme Deco Kira"),
    ("jp.co.fsi.fskaren.lenovo.theme.pretty", "Theme Pretty"),
    ("jp.co.fsi.fskaren.lenovo.theme.toyBox", "Theme ToyBox"),
    ("jp.co.fsi.fskaren.lenovo.theme.japaneseStyle", "Theme Japanese Style")
]

def run_adb_shell(cmd):
    p = subprocess.run([ADB_PATH, "-s", SERIAL, "shell", cmd], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="replace")
    return p.returncode, p.stdout.strip(), p.stderr.strip()

def main():
    print("=====================================================")
    print("Lenovo Tab M7 (TB-7305X) Safe Reversible Debloater")
    print(f"Target Serial: {SERIAL}")
    print("Mode: User 0 Uninstallation (Reversible, zero system modification)")
    print("=====================================================\n")

    uninstalled = []
    skipped = []

    for pkg, desc in SAFE_DEBLOAT_PACKAGES:
        # Check if package is installed for user 0
        code, out, _ = run_adb_shell(f"pm list packages --user 0 {pkg}")
        if pkg in out:
            print(f"Uninstalling for user 0: {pkg:<40} ({desc})...", end=" ")
            code, u_out, u_err = run_adb_shell(f"pm uninstall -k --user 0 {pkg}")
            if "Success" in u_out:
                print("[SUCCESS]")
                uninstalled.append({"package": pkg, "description": desc, "status": "uninstalled"})
            else:
                print(f"[FAILED: {u_err}]")
        else:
            print(f"Already removed or not present: {pkg:<40} ({desc})")
            skipped.append(pkg)

    # Save log
    log_file = os.path.join(LOGS_DIR, "debloat_action_log.json")
    with open(log_file, "w", encoding="utf-8") as f:
        json.dump({"uninstalled": uninstalled, "skipped": skipped}, f, indent=2)

    print(f"\nDebloating finished. {len(uninstalled)} packages uninstalled for current user.")
    print(f"Log written to: {log_file}")
    print("To restore any or all packages at any time, run: python revert_debloat.py")

if __name__ == "__main__":
    main()
