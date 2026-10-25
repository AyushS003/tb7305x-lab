#!/usr/bin/env python3
"""
scripts/check_kernel_config_halium.py
Audits a kernel .config / defconfig against official Halium 9 / Ubuntu Touch requirements.
"""

import sys
import os

REQUIRED_CONFIGS = {
    # Systemd & Init
    "CONFIG_DEVTMPFS": "y",
    "CONFIG_DEVTMPFS_MOUNT": "y",
    "CONFIG_FHANDLE": "y",
    "CONFIG_AUTOFS4_FS": "y",
    "CONFIG_TMPFS_POSIX_ACL": "y",
    "CONFIG_TMPFS_XATTR": "y",
    "CONFIG_SECCOMP": "y",
    "CONFIG_SECCOMP_FILTER": "y",
    
    # Namespaces & IPC (Mandatory for LXC Android container)
    "CONFIG_NAMESPACES": "y",
    "CONFIG_SYSVIPC": "y",
    "CONFIG_POSIX_MQUEUE": "y",
    "CONFIG_UTS_NS": "y",
    "CONFIG_IPC_NS": "y",
    "CONFIG_USER_NS": "y",
    "CONFIG_PID_NS": "y",
    "CONFIG_NET_NS": "y",
    "CONFIG_DEVPTS_MULTIPLE_INSTANCES": "y",

    # Cgroups
    "CONFIG_CGROUPS": "y",
    "CONFIG_CGROUP_DEVICE": "y",
    "CONFIG_CGROUP_FREEZER": "y",
    "CONFIG_CGROUP_PIDS": "y",
    "CONFIG_CPUSETS": "y",
    "CONFIG_MEMCG": "y",

    # Console & Display
    "CONFIG_VT": "y",
    "CONFIG_VT_CONSOLE": "y",

    # Security & Networking
    "CONFIG_ANDROID_PARANOID_NETWORK": "n"
}

def parse_config(filepath):
    configs = {}
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if line.startswith("# CONFIG_") and line.endswith("is not set"):
                parts = line.split()
                if len(parts) >= 3:
                    configs[parts[1]] = "n"
            elif "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                configs[k.strip()] = v.strip()
    return configs

def audit_config(filepath):
    print("=" * 70)
    print(f"Halium 9 / Ubuntu Touch Kernel Config Audit: {os.path.basename(filepath)}")
    print("=" * 70)
    
    if not os.path.exists(filepath):
        print(f"[ERROR] File not found: {filepath}")
        return False

    parsed = parse_config(filepath)
    passed = 0
    failed = 0

    print(f"{'Option':<35} | {'Required':<10} | {'Found':<10} | {'Status'}")
    print("-" * 70)

    for opt, expected in REQUIRED_CONFIGS.items():
        actual = parsed.get(opt, "unset")
        status = "[PASS]" if actual == expected else "[FAIL]"
        if actual == expected:
            passed += 1
        else:
            failed += 1
        print(f"{opt:<35} | {expected:<10} | {actual:<10} | {status}")

    print("-" * 70)
    print(f"Summary: {passed} Passed, {failed} Failed out of {len(REQUIRED_CONFIGS)} critical options.")
    
    if failed == 0:
        print("[RESULT] PASS: Kernel config meets all Halium 9.0 requirements!\n")
        return True
    else:
        print("[RESULT] FAIL: Kernel config is missing container/systemd prerequisites.\n")
        return False

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else r"e:\Project\Lenovo Tab tb-7305x\tb7305x-lab\source\rom\device\lenovo\mt8765_P\halium_defconfig"
    success = audit_config(target)
    sys.exit(0 if success else 1)
