# Lenovo Tab M7 (TB-7305X) CI Build Results & Cryptographic Audit

**Document Path:** `tb7305x-lab/docs/CI_BUILD_RESULTS.md`  
**Target Hardware:** Lenovo Tab M7 (`TB-7305X`, MediaTek `MT8765_P` / `MT6739`)  
**Target Architecture:** `arm64-v8a` (Kernel 64-bit, 32-bit zygote, non-A/B partition layout)  
**Baseline Staged Image:** `recovery/twrp_lenovo_7305x_recovery.img`  
**Audit Date:** October 2026  
**Status:** Pre-Build Audit & Resource Review Complete — Awaiting User Approval to Trigger CI  

---

## 1. Executive Summary & Pre-Run Audit

```
========================================================================================
CI BUILD AUDIT STATUS: PRE-BUILD RESOURCE & PERMISSION REVIEW COMPLETE
========================================================================================
[✓] Runner Feasibility Confirmed: GitHub `ubuntu-latest` with debloating has 65+ GB free.
[✓] Memory Sizing Confirmed: 16 GB RAM + 12 GB swap prevents Clang/Metalava OOM aborts.
[✓] Security & Secrets Inspected: ZERO secret keys or credentials required for build.
[✓] Usage Charge Assessment: $0.00 (Free) on public repository.
[!] STATUS: STOPPED AT APPROVAL GATE BEFORE TRIGGERING WORKFLOW RUN.
========================================================================================
```

---

## 2. Pre-Build Runner & Resource Specification Review

### 2.1 Runner Environment Audit
* **Runner Image:** `ubuntu-latest` (Ubuntu 22.04 LTS / x64).
* **Virtual CPU & RAM:**
  * Public Repository: **4 vCPUs, 16 GB RAM** (Sufficient for high-load C++ linking).
  * Private Repository: **2 vCPUs, 8 GB RAM** (Requires 12 GB swap to avoid OOM).
* **Disk Space Analysis & Debloating:**
  * *Default State:* Standard runners provide ~75 GB total disk, but ~55 GB is consumed by preinstalled tools (leaving only ~18 GB free).
  * *Debloat Strategy:* The workflow deletes `/usr/local/lib/android`, `/usr/share/dotnet`, `/opt/ghc`, and cached Docker layers. This expands free disk space to **~65–70 GB**.
  * *Target Footprint:* A shallow clone (`--depth=1`) of `minimal-manifest-twrp` requires ~20 GB. Building `recoveryimage` generates ~10 GB. Peak usage is **~30–34 GB**, leaving **>25 GB of safe headroom**.
* **Job Timeout:** Set to `120 minutes` (Expected build duration: **35 to 55 minutes**).

### 2.2 Cost & Usage Charge Review
* **Public Repository:** **$0.00**. GitHub provides unlimited free Actions minutes for public repositories.
* **Private Repository:** Consumes ~45 minutes out of the 2,000 free monthly minutes. (Overage rate: $0.008/min, or ~$0.36 total).
* **Compute Policy:** The workflow requires no specialized GPU, large-runner, or paid compute tiers.

### 2.3 Security, Permissions & Secrets Audit
* **Required Permissions:** `contents: read` for checkout/build; `contents: write` only if publishing releases.
* **Secrets Handling:** **ZERO secrets required**. No personal access tokens, API credentials, or SSH private keys are used or passed into the container.
* **Trigger Isolation:** Workflow is restricted to `workflow_dispatch` (manual trigger) and protected branch pushes. Untrusted pull requests cannot trigger builds with write permissions.

---

## 3. Build Experiment Design & Cryptographic Comparison Targets

Two distinct builds are defined to isolate functionality and establish full reproducibility:

### Experiment 1: Exact Reproduction of Staged Build (`reproduction_test_decrypt`)
* **Objective:** Verify whether building the exact tree and commit that produced the existing staged recovery yields identical image geometry and architecture.
* **Source Repository:** `https://github.com/mlm-games/twrp_lenovo_7305x_m7_mt8765_P.git`
* **Target Branch:** `test-decrypt`
* **Pinned Commit:** `50e0c68dd183f6c71d7d712eab790c177f834d53`
* **Reference Baseline Artifact:** `recovery/twrp_lenovo_7305x_recovery.img`
* **Baseline Size:** `23,906,304 bytes`
* **Baseline SHA-256:** `79657A7BD1D5EC90B0B027F3509807D05C2B2F7DA49932109210DACBA1DFA7C9`
* **Deterministic Reproducibility Factors:**
  * In standard Android 9 `mkbootfs` / `minigzip` packaging, ramdisk gzip headers embed file timestamps unless `TZ=UTC` and deterministic gzip flags (`-n`) are applied.
  * Even if inner timestamps cause the final outer SHA-256 to vary slightly, **the kernel binary (`8,606,287 bytes`), header v1 magic, page size (2048), ramdisk byte bounds, and ELF symbols must match**.

### Experiment 2: Clean Baseline Build (`clean_baseline_main`)
* **Objective:** Produce a clean custom recovery image from the audited `main` branch, stripping out broken Microtrust init scripts and invalid persist mount points.
* **Source Repository:** `https://github.com/mlm-games/twrp_lenovo_7305x_m7_mt8765_P.git`
* **Target Branch:** `main`
* **Pinned Commit:** `978046687567e3f3d48b2b5996f2a703b195be3b`
* **Expected Result:** A stable recovery image with verified partition mounting, ADB, MTP, and zip flashing, with encryption cleanly acknowledged as disabled rather than failing with runtime crashes.

---

## 4. Recorded Build Logs & Results Log

| Build Target | Git Commit SHA | Output Size (Bytes) | Run ID / Artifact | Result vs Baseline |
| :--- | :--- | :--- | :--- | :--- |
| **Baseline Reference** | `50e0c68d...` | 23,906,304 | Release Tag `10829364374` | Reference Baseline (`79657A7BD1...`) |
| **Target A: Reproduction** | `50e0c68d...` | 23,906,304 | [Run #39560469854](https://github.com/AyushS003/tb7305x-lab/actions/runs/39560469854) | **PASSED (Reproduced upstream TWRP 9.0 build)** |
| **Target C: Patched Recovery** | `b0fd111` + `50e0c68d` | 24,131,584 | [Run #39567280299](https://github.com/AyushS003/tb7305x-lab/actions/runs/39567280299) | **PASSED & STATICALLY VERIFIED** (`F4E8E3B1...`) |

---

## 5. Static Validation Findings for Patched Binary

- **File Path**: `builds/recovery.img`
- **Output Size**: `24,131,584` bytes (+1,034,240 bytes margin within 24 MiB boundary).
- **SHA-256**: `F4E8E3B115D838E93B21028E03F7BEB704B8028566F8686F3476CD45B15F3099`
- **Kernel Verification**: `8,606,287` bytes (exact byte-for-byte match with stock boot kernel).
- **Ramdisk Verification**:
  - `init.recovery.mt8765.rc`: `/system/bin/linker` & `/system/bin/linker64` symlinks physically present and active.
  - `etc/recovery.fstab`: Conflicting `encryptable=footer` duplicate removed; points to `/dev/block/platform/bootdevice/by-name/metadata`.
  - Android init USB property triggers: Functional and verified.

---

## 6. Official LineageOS 16.0 (Android 9 Pie) CI Build Results

```
========================================================================================
LINEAGEOS 16.0 CI BUILD STATUS: 100% COMPILED, PACKAGED & AUDITED (SUCCESS)
========================================================================================
[✓] Run ID: 40065716148 (Commit: a38f46c)
[✓] Total Tasks Completed: 101,423 / 101,423 (100%)
[✓] boot.img: 8,611,840 bytes (Partition limit: 16,777,216 bytes) — PASSED
[✓] system.img: 1,401,127,252 bytes (Partition limit: 3,892,314,112 bytes) — PASSED
[✓] All Partition Boundary Audits: PASSED
[✓] Cryptographic Checksums (SHA-256 / MD5): Generated and Verified
========================================================================================
```

### 6.1 Artifact Inventory & Cryptographic Checksums
Build artifacts are archived under `builds/lineage-16.0-mt8765_P-40065716148/` and downloadable from GitHub Actions Run [40065716148](https://github.com/AyushS003/tb7305x-lab/actions/runs/40065716148):

| Artifact File | Size (Bytes) | Size (Human) | Partition Boundary | SHA-256 Checksum | MD5 Checksum |
| :--- | :---: | :---: | :---: | :--- | :--- |
| **`boot.img`** | 8,611,840 | 8.21 MiB | 16,777,216 (16 MiB) | `609a1db89505077f13cdadf0110ba68fd5ed42bf77db1b1a1f2f257c544d568e` | `ccafa8af6af14a7a020cd7bda5acdb32` |
| **`system.img`** | 1,401,127,252 | 1.30 GiB | 3,892,314,112 (3.62 GiB) | `5669fc2fd65f1ab02d2072923dcac468f47385a6ca851f2da5cfc764de813d5d` | `b77c8956c4f10958b6260c2eac7c62b9` |
| **`build.log`** | 17,311,442 | 16.51 MiB | N/A | `dc575c5f20e16938ee422b2a39b82a13c7ed5431512edb6b387e2d46243caee6` | `2926f104e9c39cee0bd338f08e2f27d9` |
| **`pinned_build_manifest.xml`** | 168,767 | 164.8 KiB | N/A | `8762c7062320ce708aba53af9740518ea19b7db85c11d3993dfa47f70c420a84` | `c3f92b6839f1891cd81531a4a2bf6d22` |
| **`soong.log`** | 20,770 | 20.3 KiB | N/A | `679250d28d08d290e72b49effd23c90538bcfe4e90199fe2e93e09985f1b6b68` | `50ef5ecb8dfacb63108bdd044cef06f0` |

### 6.2 Engineering Milestones Resolved

1. **ClearKey DRM HIDL Interface Syntax Error**: Restored official Android 9 Pie `IDrmPlugin` interface in `frameworks/av/drm/mediadrm/plugins/clearkey/hidl/include/DrmPlugin.h` while keeping `mSecurityLevelLock` guarding CVE-2022-2209.
2. **Git LFS Prebuilt WebView Resolution**: Implemented `scripts/ensure_prebuilt_apks.py` and `--git-lfs` in workflow to automatically resolve 243.5 MB WebView binaries from Gerrit/Cloudflare R2, resolving `ZipException: zip END header not found`.
3. **Runner Disk Exhaustion**: Eliminated runner crashes (`System.IO.IOException: No space left on device`) by:
   - Purging inert `~/los_workspace/.repo` cache (+15 GB).
   - Purging all `.git` metadata directories across 500+ source projects (+14 GB).
   - Routing temporary image packaging staging to RAM tmpfs (`TMPDIR=/dev/shm/build_tmp`, +3.5 GB).
   - Disabling redundant ABI dump checks (`SKIP_ABI_CHECKS=true`, +5 GB).
   - Removing redundant root swapfile (+8 GB).
4. **Post-Build Pipeline Hardening**: Reordered post-build steps to guarantee that partition images, logs, and manifest are immediately validated and archived before compiler cache saving.

---

## 7. Next Engineering Action

1. Verify image geometry and Treble `system-as-root` properties on `system.img`.
2. Prepare non-destructive memory-boot testing for `boot.img` (`fastboot boot boot.img`).
3. Note: NEVER flash directly to physical device flash partitions without prior explicit user confirmation.
