# Lenovo Tab M7 (TB-7305X) Custom Recovery Source & Environment Audit

**Document Path:** `tb7305x-lab/docs/SOURCE_AUDIT.md`  
**Target Hardware:** Lenovo Tab M7 (`TB-7305X`, Serial: `HA154H1C`, SoC: MediaTek `MT8765_P` / `MT6739`)  
**Active Firmware Baseline:** Android 9 Pie (`TB-7305X_S000126_220620_ROW`)  
**Author / Engineering Role:** Android Platform & Recovery Engineer  
**Audit Date:** October 2026  
**Status:** Phase 1 Complete — Source & Upstream Audit  

---

## 1. Executive Summary & Audit Objectives

The objective of this engineering initiative is to establish a **verifiable, reproducible, and fully understood device-specific custom recovery** for the Lenovo Tab M7 TB-7305X, rather than relying on unauthenticated binary images.

Phase 1 provides a comprehensive, ground-truth audit of:
1. The community device tree repository (`mlm-games/twrp_lenovo_7305x_m7_mt8765_P`).
2. Exact commit hashes, branch discrepancies, and dependency chains.
3. Hardware subsystem reality checks (Kernel, Ramdisk, Keymaster/TEE, Encryption, Fstab, Display, Touch, AVB).
4. Root causes of documented runtime crashes and decryption failures.

```
========================================================================================
AUDIT SUMMARY: UPSTREAM RECOVERY SOURCE STATUS
========================================================================================
[✓] Device Tree Skeleton: Generated via SebaUbuntu's `twrpdtgen` (minimal baseline).
[✓] Kernel Origin: Prebuilt binary blob (8,606,287 bytes) extracted from stock boot/recovery.
[✓] Hardware Fit: Target partition 0x1800000 (24.00 MiB) matches image geometry (22.80 MiB).
[!] ENCRYPTION SUB-SYSTEM: CRITICALLY BROKEN in upstream `test-decrypt` branch.
    - Microtrust TEE HAL services (`teei_loader`, `keymaster@3.0`) exit with status 127.
    - Init script syntax errors (`mount ext4 /dev/block/.../by-name /mnt/vendor/persist`).
    - Upstream maintainer openly confirmed in GitHub Issue #11 that /data decryption fails.
[!] REPRODUCIBILITY CONSTRAINT: Upstream binaries are unauthenticated GitHub Actions CI builds;
    source requires minimal-manifest-twrp (twrp-9.0) on a Linux host (60+ GB disk, 16 GB RAM).
========================================================================================
```

---

## 2. Upstream Repository Topology & Resolved Commit Pins

The community recovery implementation resides in GitHub repository:
`https://github.com/mlm-games/twrp_lenovo_7305x_m7_mt8765_P`

### 2.1 Branch Architecture & Commit Pinning

To avoid building from floating branches, the exact resolved Git commit identifiers are recorded below:

| Branch Name | Resolved HEAD Commit SHA-1 | Tree State / Purpose |
| :--- | :--- | :--- |
| **`main`** | `978046687567e3f3d48b2b5996f2a703b195be3b` | "Clean" minimal TWRP device tree; decryption explicitly disabled. |
| **`test-decrypt`** | `076e654ed8014cbc46ed532f45a6ca6fe79cf77c` | **Origin of staged image**. Contains experimental Microtrust binaries. |
| **`test`** | `e8a205fd369dde1dbf2559da05a4faf064d0b5ef` | Experimental scratch branch. |
| **`pbrp-9.0`** | `59704a665453820d79bd86cc6bb4acdedbf8489c` | PitchBlack Recovery Project 9.0 port attempt. |
| **`shrp-9.0`** | `b65538669bc58d7228834817e681f79af92eefb2` | SKY HAWK Recovery Project 9.0 port attempt. |

### 2.2 Provenance of the Staged Image (`recovery/twrp_lenovo_7305x_recovery.img`)

* **Upstream Release Tag:** `10829364374` (Release ID: `174736970`)
* **Build Date:** September 12, 2024 (11:19:37 UTC)
* **Build Runner:** `github-actions[bot]`
* **Exact Build Commit:** `50e0c68dd183f6c71d7d712eab790c177f834d53` on branch `test-decrypt`
* **Output Image Size:** `23,906,304 bytes`
* **Local Image SHA-256:** `79657A7BD1D5EC90B0B027F3509807D05C2B2F7DA49932109210DACBA1DFA7C9`
* **Cryptographic Signatures:** **None**. Upstream API reports `digest: null`.

---

## 3. Kernel, Vendor & Build Manifest Dependencies

### 3.1 Kernel Source vs. Prebuilt Binary
* **Configuration Setting (`BoardConfig.mk`):**
  ```makefile
  TARGET_PREBUILT_KERNEL := $(DEVICE_PATH)/prebuilt/kernel
  BOARD_PREBUILT_DTBOIMAGE := $(DEVICE_PATH)/prebuilt/dtbo.img
  ```
* **Analysis:** The repository **does not compile a kernel from source**. It bundles a stock MediaTek Linux 4.4.146+ kernel binary (`8,606,287 bytes`, SHA-1 `fcf67655eeeeacee04ad6246c081dda31f951728`) and a prebuilt DTBO (`39,838 bytes`, SHA-1 `b5eae6e73b797fb1235b04584bb7ac89125a9618`).
* **Source Availability:** Official GPL-compliant kernel sources for the Lenovo Tab M7 are archived on the [Lenovo Open Source Portal](https://support.lenovo.com/solutions/ht511330-lenovo-open-source-portal). While the source exists upstream, building custom recovery with the stock prebuilt kernel avoids kernel compilation regressions (panel timing, PMIC drivers).

### 3.2 Vendor Blobs
* **Source Origin:** Extracted from retail stock firmware dumps (`https://github.com/fw-dumps/lenovo_7305x_dump`).
* **Bundled Proprietary Binaries (`recovery/root/`):**
  * `vendor/bin/hw/android.hardware.gatekeeper@1.0-service`
  * `vendor/bin/hw/vendor.mediatek.hardware.keymaster_attestation@1.1-service`
  * `sbin/android.hardware.keymaster@3.0-service`
  * `sbin/teei_loader`
  * `sbin/istorageproxyd`
  * 32-bit and 64-bit HAL implementations (`keystore.itrusty.so`, `keystore.mt6739.so`, `libitrusty.so`, `libtrusty.so`).

### 3.3 Build Manifest & Build System
* **Manifest Target:** Minimal TWRP Manifest for Android 9:
  `https://github.com/minimal-manifest-twrp/platform_manifest_twrp_omni.git` (Branch: `twrp-9.0`)
* **Build System:** Android Build System (GNU Make / Soong / Kati / Ninja)
* **Build Targets Defined:**
  * Product Makefiles: `AndroidProducts.mk`, `omni_mt8765_P.mk`
  * Lunch Combo: `omni_mt8765_P-eng`

---

## 4. Hardware Subsystem & Source File Reality Checks

A rigorous comparison between the device tree configuration files, documentation claims, and actual system behavior:

### 4.1 Encryption, TEE & Keymaster Subsystem: **CRITICALLY BROKEN**
* **Claim:** Branch `test-decrypt` was created to support on-device decryption of encrypted `/data`.
* **Empirical Reality:** Decryption is completely non-functional.
* **Root Cause 1 — Dynamic Linker & Missing Shared Libraries (Exit 127):**
  When init parses `recovery/root/vendor/etc/init/android.hardware.keymaster@3.0-service.rc` and launches the services, the Linux kernel aborts with error 127:
  ```text
  init: cannot execve('/vendor/bin/teei_loader'): No such file or directory
  init: Service 'teei_loader' (pid 306) exited with status 127
  init: cannot execve('/vendor/bin/hw/android.hardware.keymaster@3.0-service'): No such file or directory
  init: Service 'keymaster-3-0' (pid 307) exited with status 127
  ```
  In Linux, `execve` returning `ENOENT` (status 127) for an existing executable indicates that the **dynamic linker (`/system/bin/linker64`) cannot locate the ELF interpreter or required dynamic library dependencies**. The maintainer copied `.so` files into `vendor/lib64/` but omitted core AOSP Android 9 runtime dependencies (e.g. `libhidlbase.so`, `libbinder.so`, `libutils.so`) or failed to map linker namespace paths.
* **Root Cause 2 — Critical Syntax Error in Init Scripts:**
  In `recovery/root/init.recovery.mt8765.rc` line 20:
  ```text
  mount ext4 /dev/block/platform/bootdevice/by-name /mnt/vendor/persist rw
  ```
  The path `/dev/block/platform/bootdevice/by-name` is a **directory**, not a block device node! The correct device path is `/dev/block/platform/bootdevice/by-name/persist`. This error causes the persist mount to fail immediately, preventing Keymaster from accessing device-specific keystore salts.
* **Root Cause 3 — Upstream Maintainer Concession (GitHub Issue #11):**
  In GitHub Issue #11 ("Decryption (Uses microtrust -> itrusty)"), maintainer `mlm-games` confirmed:
  > *"When TWRP launches, it says unable to find the default password and asks me to enter when there is no password... I had recently used Software Fix from Lenovo to get it back to stock."*

### 4.2 Display Subsystem
* **Configuration (`BoardConfig.mk`):**
  * Resolution: `600 x 1024` (7.0-inch IPS LCD)
  * Pixel Density: `TARGET_SCREEN_DENSITY := 160`
* **Driver Implementation:** Display driver is integrated into the prebuilt kernel (`[DISP]DSI read long packet size`).
* **Assessment:** **PASS on maintainer unit; UNVERIFIED on retail variations**. Lenovo used different LCD panel vendors across production batches.

### 4.3 Touchscreen Subsystem
* **Driver:** MediaTek Touch Panel Driver (`mtk-tpd`) built into prebuilt kernel.
* **Assessment:** Touch input functions via standard kernel event device `/dev/input/eventX`.

### 4.4 File System & Partition Configuration (`fstab`)
* **Partition Map:**
  * Hardware Recovery Size: `25,165,824 bytes` (`0x1800000`, 24.00 MiB)
  * Partition Type: `raw data`
  * Bootloader slot count: `0` (Standard Non-A/B layout with dedicated recovery partition).
* **Fstab Inconsistencies:**
  * `recovery/root/etc/recovery.fstab` line 24 specifies `forcefdeorfbe=/dev/block/platform/bootdevice/by-name/metadata`.
  * However, `recovery/root/etc/twrp.fstab` omits `/metadata` entirely. On MediaTek Android 9 devices with File-Based Encryption (FBE), failure to mount `/metadata` prevents encryption key derivation.

### 4.5 Android Verified Boot (AVB) & dm-verity
* **Device Topology:** The TB-7305X does **not** have a dedicated `vbmeta` partition.
* **AVB Implementation:** Verification flags are embedded directly inside the signed boot/recovery image headers (`veritykeyid=id:7e4333f9...`).
* **Maintainer Warning:** Booting modified system or recovery images without disabling AVB causes bootloops. The stock boot image must have dm-verity disabled.

---

## 5. Branch Discrepancies & Divergence Summary

| Subsystem / Feature | `main` Branch | `test-decrypt` Branch (Staged Image) | Root Problem / Gap |
| :--- | :--- | :--- | :--- |
| **Decryption Support** | Explicitly disabled (`# Decryption`) | Attempted via Microtrust binaries | Binaries fail to execute (exit 127). |
| **Init RC Scripts** | Minimal, stock `init.rc` | Custom `microtrust.rc` + `init.recovery.mt8765.rc` | Syntax errors (mounting `/by-name` folder). |
| **Vendor Blobs** | Minimal vendor tree | ~25 MB of `.so` and daemon blobs | Missing dynamic linker dependencies. |
| **Recovery Fstab** | Clean mount points | Hardcoded FDE/FBE flags pointing to `/metadata` | `/metadata` not mounted in TWRP. |
| **Build Artifact** | Tag `twrp-9.0_1` (24.23 MB) | Tag `10829364374` (23.90 MB) | Both fail decryption in userland. |

---

## 6. Conclusions & Engineering Requirements for Phase 2

1. **The Existing Prebuilt Image Cannot Be Trusted for Decryption:** The staged image is built from the broken `test-decrypt` branch. It will not decrypt user data on Android 9.
2. **Proper Recovery Architecture:**
   * A clean, stable build should be established first from the `main` branch (with unencrypted backup/restore, ADB, MTP, and zip flashing working reliably).
   * For encryption, either the full Microtrust linker dependency tree must be solved (requiring proprietary linker namespace mapping), or a clean decryption-disabled workflow must be formally documented.
3. **Build Environment Constraint:** As documented in `docs/BUILD_ENVIRONMENT.md`, compiling this recovery requires a dedicated 64-bit Linux environment with at least 60 GB of disk space and 16 GB of RAM.
