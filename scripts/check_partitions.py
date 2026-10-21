import subprocess
import os

SERIAL = "HA154H1C"
ADB_PATH = r"C:\Users\ayush\Downloads\platform-tools-latest-windows\platform-tools\adb.exe"

def run_adb_shell(cmd):
    p = subprocess.run([ADB_PATH, "-s", SERIAL, "shell", cmd], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="replace")
    return p.stdout.strip()

print("Partition mapping by-name:")
by_name_out = run_adb_shell("ls -l /dev/block/platform/*/by-name/ 2>/dev/null || ls -l /dev/block/by-name/ 2>/dev/null")
mapping = {}
for line in by_name_out.splitlines():
    parts = line.split()
    if len(parts) >= 2 and "->" in parts:
        idx = parts.index("->")
        name = parts[idx-1]
        target = parts[idx+1]
        mapping[os.path.basename(target)] = name

print("Reading partition block sizes from /sys/block/mmcblk0/:")
res = []
for i in range(1, 40):
    part = f"mmcblk0p{i}"
    size_512 = run_adb_shell(f"cat /sys/block/mmcblk0/{part}/size 2>/dev/null")
    if size_512.isdigit():
        bytes_val = int(size_512) * 512
        mb_val = bytes_val / (1024 * 1024)
        gb_val = bytes_val / (1024 * 1024 * 1024)
        name = mapping.get(part, "unknown")
        res.append((part, name, bytes_val, mb_val, gb_val))

print(f"{'Partition':<14} | {'Name':<14} | {'Bytes':<14} | {'Size MB':<10} | {'Size GB'}")
print("-" * 65)
for p, n, b, mb, gb in res:
    if gb >= 1.0:
        print(f"{p:<14} | {n:<14} | {b:<14} | {mb:<10.1f} | {gb:.2f} GB")
    else:
        print(f"{p:<14} | {n:<14} | {b:<14} | {mb:<10.1f} |")

# Also check Treble system-as-root
sar = run_adb_shell("getprop ro.build.system_root_image")
vndk = run_adb_shell("getprop ro.vndk.version")
flavor = run_adb_shell("getprop ro.build.flavor")
print(f"\nSystem-as-root: {sar}")
print(f"VNDK: {vndk}")
print(f"Build Flavor: {flavor}")
