# Lenovo Tab M7 (TB-7305X) Custom Recovery Engineering Log

**Target Hardware:** Lenovo Tab M7 (`TB-7305X`, MediaTek `MT8765_P` / `MT6739`)  
**Stock Firmware:** Android 9 Pie (`TB-7305X_S000126_220620_ROW`)  
**Recovery Partition:** `0x1800000` (25,165,824 bytes / 24.00 MiB)  
**Status:** Published to Private GitHub Repository (`AyushS003/tb7305x-lab`) — Ready for CI Build  

---

## 1. Work Completed

1. **GitHub Actions Workflow Corrections (`.github/workflows/build_recovery.yml`)**:
   - Pinned runner to `ubuntu-22.04` (prevents Ubuntu 24.04 breakages where Python 2.7 and 32-bit build libraries are removed).
   - Added `actions/checkout@v4` step to ensure local tree files are available in `$GITHUB_WORKSPACE`.
   - Added `actions/setup-java@v4` (Zulu OpenJDK 8) for deterministic Java compilation.
   - Added `set -o pipefail` to ensure build errors during compilation are caught and not masked by `tee`.
   - Added three selectable build targets:
     - `reproduction_test_decrypt`: Exact baseline commit `50e0c68dd183f6c71d7d712eab790c177f834d53`.
     - `clean_baseline_main`: Upstream `main` commit `978046687567e3f3d48b2b5996f2a703b195be3b`.
     - `modified_working_tree`: Clones baseline `test-decrypt` and overlays local patches from `source/device/lenovo/mt8765_P`.

2. **Baseline Image Provenance & Integrity**:
   - Upstream GitHub Release: Tag `10829364374` (Run ID `10829364374`, built 2024-09-12).
   - Source Commit: `50e0c68dd183f6c71d7d712eab790c177f834d53` (`test-decrypt` branch).
   - Image File: `recovery/twrp_lenovo_7305x_recovery.img` (23,906,304 bytes).
   - SHA-256: `79657A7BD1D5EC90B0B027F3509807D05C2B2F7DA49932109210DACBA1DFA7C9`.
   - Partition Margin: Fits target partition with +1,259,520 bytes (+1.20 MiB) safety margin.

3. **Subsystem Root-Cause Analysis (Live Device & Binaries)**:
   - **Dynamic Linker Failure (Exit Status 127)**:
     - `teei_loader`: 32-bit ELF with `PT_INTERP: /system/bin/linker`.
     - `android.hardware.keymaster@3.0-service`: 64-bit ELF with `PT_INTERP: /system/bin/linker64`.
     - In TWRP rootfs, linkers reside at `/sbin/linker` and `/sbin/linker64`, and `/system/bin` was missing. The kernel's `execve` returned `ENOENT` (Error 2, shell exit 127) before user code could run.
   - **Encryption Architecture Discovery**:
     - Queried running tablet: `ro.crypto.type = block`, `ro.crypto.fs_crypto_blkdev = /dev/block/dm-1`.
     - The device uses **Full Disk Encryption (FDE)** via `dm-crypt`, with raw key stored on `/dev/block/platform/bootdevice/by-name/metadata` (`/dev/block/mmcblk0p8`).
     - Upstream community tree mistakenly configured File-Based Encryption (FBE) flags, causing boot loops and decryption failures.

4. **Targeted Device Tree Corrections**:
   - `recovery.fstab`: Removed conflicting `encryptable=footer;` duplicate flag from `/data` entry.
   - `recovery/root/init.recovery.mt8765.rc`:
     - Replaced unsupported shell `if [ ... ]; then` syntax with valid Android init property triggers (`sys.usb.config=*`).
     - Added `/system/bin` directory creation and symlinked `/sbin/linker` and `/sbin/linker64` so vendor HAL binaries can execute.
     - Removed non-existent `/sbin/mntl_link` execution.

5. **Repository Published**:
   - Repository: `https://github.com/AyushS003/tb7305x-lab` (Private).
   - Initial commit: `116c4a1` (41 tracked files, 8.4 MB).
   - `.gitignore` verified: Excluded 2.01 GB firmware dumps, recovery archives, and device serial logs.

---

## 2. CI Runner Resources & Cost Assessment

- **Runner**: GitHub Actions `ubuntu-22.04` (2 vCPUs, 8 GB RAM + 12 GB swap file).
- **Disk**: 65–70 GB free post-debloat (sufficient for minimal TWRP 9.0 shallow tree and build artifacts).
- **Cost**: Consumes ~40 minutes from the free 2,000 monthly Actions allowance for private repositories ($0.00 billing impact).

---

## 3. Next Actions

1. Trigger workflow `reproduction_test_decrypt` via GitHub Actions tab on `AyushS003/tb7305x-lab`.
2. Compare output `recovery.img` artifact against baseline SHA-256 (`79657A7BD1...`).
3. Trigger Target C (`modified_working_tree`) to compile the patched device tree.
4. Verify output image size and symbols against partition bounds (`25,165,824 bytes`).
