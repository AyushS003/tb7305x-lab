# Halium 9.0 (Ubuntu Touch Base) for Lenovo Tab M7 (TB-7305X)

Official Halium 9.0 bringup release package containing the customized Linux 4.4.146 container-compliant kernel and `halium-boot.img` for the **Lenovo Tab M7 (TB-7305X)**.

---

## Device & Platform Specifications

| Parameter | Value |
|---|---|
| **Target Device** | Lenovo Tab M7 |
| **Model Code** | TB-7305X |
| **SoC / Chipset** | MediaTek MT8765 / MT6739 (Quad-Core Cortex-A53 @ 1.30 GHz) |
| **GPU** | Imagination PowerVR Rogue GE8100 |
| **Architecture** | 64-bit ARM (`aarch64` / `arm64-v8a`) |
| **RAM** | 2.0 GB Physical RAM |
| **Storage Architecture** | MediaTek eMMC 5.1 (ComboA) |
| **Base Android Platform** | Android 9.0 (Pie) / ALPS MT8765 |
| **Halium Version** | Halium 9.0 (Ubuntu Touch 20.04 Focal / Lomiri Container Target) |
| **Kernel Version** | Linux 4.4.146 (`Image.gz-dtb` bundled) |
| **Compiler** | Google AOSP GCC 4.9 (`aarch64-linux-android-4.9`) |

---

## Halium 9.0 Container & Systemd Compliance

This kernel was compiled from source with the certified `halium_defconfig` (based on MediaTek's `k39tv1_64_bsp_defconfig`) and passed all **23 Halium & Ubuntu Touch container prerequisites**:

- **Namespaces**: `CONFIG_NAMESPACES=y`, `CONFIG_UTS_NS=y`, `CONFIG_IPC_NS=y`, `CONFIG_USER_NS=y`, `CONFIG_PID_NS=y`, `CONFIG_NET_NS=y`
- **Control Groups (cgroups)**: `CONFIG_CGROUPS=y`, `CONFIG_MEMCG=y`, `CONFIG_CGROUP_SCHED=y`, `CONFIG_CPUSETS=y`, `CONFIG_CGROUP_DEVICE=y`, `CONFIG_CGROUP_FREEZER=y`
- **Container Storage**: `CONFIG_OVERLAY_FS=y`, `CONFIG_DEVPTS_MULTIPLE_INSTANCES=y`, `CONFIG_POSIX_MQUEUE=y`
- **Lomiri & Ubuntu Security**: `CONFIG_SECURITY_APPARMOR=y` (Default security enabled for Lomiri click apps)
- **Android IPC Binder**: `CONFIG_ANDROID_BINDER_IPC=y`, `CONFIG_ANDROID_BINDERFS=y`, `CONFIG_ANDROID_BINDER_DEVICES="binder,hwbinder,vndbinder"`
- **Systemd Cgroups**: Unified hierarchy disabled in cmdline (`systemd.unified_cgroup_hierarchy=0`) for legacy v1 cgroups container compatibility.

---

## Boot Header Verification

Extracted and verified via Android AOSP `unpack_bootimg`:
- **Kernel Physical Base**: `0x40078000`
- **Kernel Entry Offset**: `0x00008000` (Load Address: `0x40080000`)
- **Ramdisk Offset**: `0x04f88000` (Load Address: `0x45000000`)
- **Tags Offset**: `0x03f88000` (Tags Address: `0x44000000`)
- **Page Size**: `2048` bytes
- **Header Version**: `1`
- **Cmdline**: `bootopt=64S3,32N2,64N2 buildvariant=userdebug systemd.unified_cgroup_hierarchy=0 console=tty0 console=ttyMT0,921600n1 androidboot.selinux=permissive`

---

## Included Files

- `halium-boot.img`: Complete Halium 9 boot image containing the certified Linux 4.4.146 kernel + continuous ARM64 Halium initramfs.
- `boot_halium.bat`: 1-click script to test-boot Halium in live RAM without flashing (Safe, non-destructive).
- `boot_halium.sh`: Linux/macOS equivalent live boot script.
- `flash_halium_boot.bat`: 1-click script to permanently flash `halium-boot.img` to the `boot` partition.
- `flash_halium_boot.sh`: Linux/macOS permanent boot flasher script.
- `INSTRUCTIONS.txt`: Detailed walkthrough and telnet debugging guide.
- `MD5SUMS.txt` / `SHA256SUMS.txt`: Cryptographic checksums.

---

## Quick Start (Zero-Risk Live Test)

1. Put your tablet into **FASTBOOT MODE**:
   - Power off tablet.
   - Hold **Volume Down + Power** until `FASTBOOT mode...` appears on screen.
2. Connect tablet via USB to PC.
3. Double-click **`boot_halium.bat`** (or `./boot_halium.sh` on Linux).
4. The tablet will load the Halium kernel directly into memory while leaving your installed LineageOS ROM untouched!
