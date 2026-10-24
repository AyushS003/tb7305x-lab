#!/usr/bin/env python3
"""
scripts/generate_halium_defconfig.py
Generates certified Halium 9.0 defconfig for Lenovo Tab M7 (TB-7305X).
Takes the working base kernel config and applies mandatory Halium/Ubuntu Touch container flags.
"""

import os
import sys

BASE_CONFIG = sys.argv[1] if len(sys.argv) > 1 else (
    r"scratch/k39tv1_64_bsp_defconfig" if os.path.exists("scratch/k39tv1_64_bsp_defconfig")
    else r"source/rom/device/lenovo/mt8765_P/halium_defconfig"
)
OUTPUT_DEFCONFIG = sys.argv[2] if len(sys.argv) > 2 else r"source/rom/device/lenovo/mt8765_P/halium_defconfig"

MANDATORY_HALIUM_CONFIGS = {
    # Namespaces & Containers (LXC)
    "CONFIG_NAMESPACES": "y",
    "CONFIG_UTS_NS": "y",
    "CONFIG_IPC_NS": "y",
    "CONFIG_USER_NS": "y",
    "CONFIG_PID_NS": "y",
    "CONFIG_NET_NS": "y",

    # Devtmpfs (Systemd device management)
    "CONFIG_DEVTMPFS": "y",
    "CONFIG_DEVTMPFS_MOUNT": "y",

    # Control Groups (Cgroups)
    "CONFIG_CGROUPS": "y",
    "CONFIG_CGROUP_DEBUG": "y",
    "CONFIG_CGROUP_FREEZER": "y",
    "CONFIG_CGROUP_PIDS": "y",
    "CONFIG_CGROUP_DEVICE": "y",
    "CONFIG_CPUSETS": "y",
    "CONFIG_PROC_PID_CPUSET": "y",
    "CONFIG_CGROUP_CPUACCT": "y",
    "CONFIG_CGROUP_SCHED": "y",
    "CONFIG_FAIR_GROUP_SCHED": "y",
    "CONFIG_RT_GROUP_SCHED": "y",
    "CONFIG_BLK_CGROUP": "y",
    "CONFIG_MEMCG": "y",
    "CONFIG_MEMCG_SWAP": "y",

    # Systemd Prerequisites
    "CONFIG_FHANDLE": "y",
    "CONFIG_AUTOFS4_FS": "y",
    "CONFIG_CHECKPOINT_RESTORE": "y",
    "CONFIG_FANOTIFY": "y",
    "CONFIG_FANOTIFY_ACCESS_PERMISSIONS": "y",
    "CONFIG_SECCOMP": "y",
    "CONFIG_SECCOMP_FILTER": "y",
    "CONFIG_TMPFS_POSIX_ACL": "y",
    "CONFIG_TMPFS_XATTR": "y",

    # Virtual Terminal / Console (Lomiri & debug)
    "CONFIG_VT": "y",
    "CONFIG_VT_CONSOLE": "y",

    # Kernel Inspection & Debugging
    "CONFIG_IKCONFIG": "y",
    "CONFIG_IKCONFIG_PROC": "y",

    # Networking permissions for systemd users
    "CONFIG_ANDROID_PARANOID_NETWORK": "n"
}

def main():
    if not os.path.exists(BASE_CONFIG):
        print(f"[ERROR] Base config not found: {BASE_CONFIG}")
        sys.exit(1)

    print(f"Reading base kernel config: {BASE_CONFIG}")
    with open(BASE_CONFIG, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()

    config_dict = {}
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            if "is not set" in line:
                parts = line.split()
                if len(parts) >= 3 and parts[1].startswith("CONFIG_"):
                    config_dict[parts[1]] = "n"
            continue
        if "=" in line:
            key, val = line.split("=", 1)
            config_dict[key.strip()] = val.strip()

    print(f"Loaded {len(config_dict)} existing kernel symbols.")

    # Apply Halium overrides
    applied = 0
    for key, val in MANDATORY_HALIUM_CONFIGS.items():
        old_val = config_dict.get(key, "unset")
        if old_val != val:
            config_dict[key] = val
            applied += 1
            print(f"  [OVERRIDE] {key}: {old_val} -> {val}")

    print(f"Applied {applied} Halium container configuration overrides.")

    # Write output defconfig
    os.makedirs(os.path.dirname(OUTPUT_DEFCONFIG), exist_ok=True)
    with open(OUTPUT_DEFCONFIG, "w", encoding="utf-8") as f:
        f.write("#\n")
        f.write("# Certified Halium 9.0 Defconfig for Lenovo Tab M7 (TB-7305X)\n")
        f.write("# Generated for Linux Kernel 4.4.146 + LXC Container & Systemd Support\n")
        f.write("#\n\n")

        for key in sorted(config_dict.keys()):
            val = config_dict[key]
            if val == "n":
                f.write(f"# {key} is not set\n")
            else:
                f.write(f"{key}={val}\n")

    print(f"\n[SUCCESS] Halium defconfig generated at: {OUTPUT_DEFCONFIG}")
    print(f"File size: {os.path.getsize(OUTPUT_DEFCONFIG):,} bytes")

if __name__ == "__main__":
    main()
