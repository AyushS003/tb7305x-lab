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

5. **Repository Published & CI Builds Verified**:
   - Repository: `https://github.com/AyushS003/tb7305x-lab` (Public).
   - `.gitignore` verified: Excluded 2.01 GB firmware dumps, recovery archives, and device serial logs.
   - **Target A (Reproduction Build)**: [Run #39560469854](https://github.com/AyushS003/tb7305x-lab/actions/runs/39560469854) — **PASSED**.
   - **Target C (Patched Build)**: [Run #39567280299](https://github.com/AyushS003/tb7305x-lab/actions/runs/39567280299) — **PASSED & VERIFIED**. Generated artifact `twrp-modified_working_tree-39567280299` (`F4E8E3B1...`, 24,131,584 bytes).

6. **In-Memory Testing & Bootloader Findings**:
   - Executed non-destructive `fastboot boot builds/recovery.img` on live tablet (Serial: `HA154H1C`).
   - Fastboot upload succeeded (`OKAY [0.833s]`, `booting OKAY [0.062s]`), but MediaTek Little Kernel (LK) immediately triggered a watchdog warm reset into PreLoader (`VID_0E8D&PID_2000`) and rebooted normal Android system.
   - Controlled baseline test: Executed `fastboot boot firmware/extracted/recovery-verified.img` (100% genuine factory-signed stock recovery). Exact same behavior observed (uploaded OKAY, LK reset into PreLoader, booted Android).
   - **Conclusion**: MediaTek LK on `TB-7305X` (`mt8765_P-1a97443`) does not support RAM execution via `fastboot boot`. Custom recoveries can only run when flashed to the physical recovery partition.
   - **Header & Tree Improvements Applied**:
     - Discovered stock recovery header contains `recovery_dtbo_size: 39838` (matching `prebuilt/dtbo.img`), whereas upstream tree omitted `BOARD_INCLUDE_RECOVERY_DTBO := true`.
     - Discovered stock recovery/boot kernel is 8,608,863 bytes (`bc4e8440...`), whereas upstream tree had an older 8,606,287 byte prebuilt.
     - Updated `BoardConfig.mk` with `BOARD_INCLUDE_RECOVERY_DTBO := true` and synchronized `prebuilt/kernel` with the authentic stock kernel (Commit `c2d8d41`, pushed in `ee38b08`).

7. **Target C Refreshed Build ([Run #39578027764](https://github.com/AyushS003/tb7305x-lab/actions/runs/39578027764)) — PASSED & VERIFIED**:
   - **Workflow Run**: Triggered on `main` (`ee38b08`), completed successfully in 16m 40s.
   - **Artifact**: `twrp-modified_working_tree-39578027764` downloaded to `builds/` (55,436,752 bytes zip).
   - **Output recovery.img**:
     - Size: `24,174,592` bytes (23.05 MiB) — fits partition (`25,165,824` bytes) with **+991,232 bytes (+0.95 MiB)** safety margin.
     - SHA-256: `0B6640B405BE58CD1612A7606AAFF3E9D0DE3849B13E8E3A7F47989DAFF76199`.
     - Recovery DTBO: `39,838` bytes at offset `0x1704000` (100% byte-for-byte match with `prebuilt/dtbo.img` and stock recovery).
     - Kernel: `8,608,863` bytes, SHA-256 `bc4e8440...` (100% byte-for-byte match with authentic stock recovery/boot kernel).
     - Ramdisk: Contains dynamic linker symlinks (`/system/bin/linker` & `linker64`) and FDE metadata block `recovery.fstab`.

### Comparison Matrix

| Image | Size (Bytes) | Margin Remaining | Header Ver | DTBO Size | Kernel Size / Hash | SHA-256 Prefix |
|---|---|---|---|---|---|---|
| **Stock Lenovo (`recovery-verified.img`)** | 13,857,696 | +11,308,128 B | 1 | 39,838 B | 8,608,863 B (`bc4e8440`) | `A6867573...` |
| **Upstream Community Release** | 23,906,304 | +1,259,520 B | 1 | 0 B (missing) | 8,606,287 B (`8bf0c295`) | `79657A7B...` |
| **Run #39567280299 (Prior)** | 24,131,584 | +1,034,240 B | 1 | 0 B (missing) | 8,606,287 B (`8bf0c295`) | `F4E8E3B1...` |
| **Run #39578027764 (Running Recovery)** | 24,174,592 | +991,232 B | 1 | 39,838 B (matched) | 8,608,863 B (`bc4e8440`) | `0B6640B4...` |
| **Run #39586094933 (FDE Crypto Candidate)** | **23,363,584** | **+1,802,240 B** | **1** | **39,838 B (matched)** | **8,608,863 B (`bc4e8440`)** | **`D8253BF3...`** |

---

## 2. FDE Crypto Implementation ([Run #39586094933](https://github.com/AyushS003/tb7305x-lab/actions/runs/39586094933))

- **Workflow Run**: Triggered on `main` (`fc75c47`), completed successfully in 16m 12s.
- **Artifact**: `twrp-modified_working_tree-39586094933` downloaded to `builds/` (53,092,534 bytes zip).
- **Candidate Image (`builds/recovery-crypto.img`)**:
  - Size: `23,363,584` bytes (22.28 MiB) — fits partition (`25,165,824` bytes) with **+1,802,240 bytes (+1.72 MiB)** safety margin (optimized via `TW_EXTRA_LANGUAGES := false`).
  - SHA-256: `D8253BF3B74C8625F936EECA4D15B2CDC51AE44536523C46122C843CED3B0051`.
  - Header Version: 1 (`ANDROID!`), Page size: 2048, Kernel size: 8,608,863 bytes.
  - Recovery DTBO: `39,838` bytes at offset `0x163e000` (100% byte-for-byte match with `prebuilt/dtbo.img` and stock recovery).
- **Crypto & HAL Verification in Ramdisk (`ramdisk-recovery.cpio`)**:
  - `sbin/libcryptfsfde.so` (68,680 B): Compiled from `bootable/recovery/crypto/fde/cryptfs.cpp`.
  - `sbin/libgpt_twrp.so` (68,192 B): GPT table reading utility for partition crypto inspection.
  - `sbin/android.hardware.keymaster@3.0.so` (203,032 B) & `@4.0.so` (203,720 B): HIDL client interfaces.
  - `sbin/hwservicemanager` (136,592 B): Hardware Binder service manager.
  - `sbin/keystore`, `sbin/keystore_cli`, `sbin/libsoftkeymasterdevice.so`: Keymaster crypto stack.
  - `init.recovery.mt8765.rc`: Fully provisions read-only mounts for `/system_root` and `/vendor`, `/system -> /system_root/system` SAR symlink, Microtrust TEE driver nodes, and `keymaster-3-0` / `teei_loader` lifecycle triggers.

---

## 3. CI Runner Resources & Cost Assessment

- **Runner**: GitHub Actions `ubuntu-22.04` (4 vCPUs, 16 GB RAM + 12 GB swap file).
- **Disk**: 65–70 GB free post-debloat (sufficient for minimal TWRP 9.0 shallow tree and build artifacts).
- **Cost**: **$0.00** (100% Free unlimited runner minutes for public GitHub repositories; 0 billing impact).

---

## 4. Physical Flash & Live Execution

1. **Candidate Image Flashed**: User approved flashing [`builds/recovery-crypto.img`](file:///e:/Project/Lenovo%20Tab%20tb-7305x/tb7305x-lab/builds/recovery-crypto.img) (23,363,584 bytes, SHA-256 `D8253BF3...`) to the physical recovery partition (`/dev/block/platform/bootdevice/by-name/recovery`).
2. **Boot Verified**: Device booted cleanly into TWRP 3.7.0 (`omni_mt8765_P-eng 16.1.0 PQ2A.190405.003 test-keys`).
3. **Crypto Detection**: TWRP automatically detected the encrypted `/data` block partition (`ro.crypto.type=block`, `ro.crypto.state=encrypted`) via `/dev/block/platform/bootdevice/by-name/metadata` (`0xD0B5B1C4` magic, `KDF_SCRYPT_KEYMASTER`).
4. **USB / ADB Interface**: ADB connection established (`HA154H1C recovery`, USB VID:PID `18D1:D001`).

---

## 5. Live Diagnostics & Working FDE Decryption Breakthrough

### Diagnostic Root Cause
Live analysis via root ADB shell and `logcat` revealed two critical blockers in the vendor HAL execution chain:
1. **Dynamic Linker VNDK Path**:
   `android.hardware.keymaster@3.0-service` failed to dlopen `android.hardware.keymaster@3.0-impl.so` because `libpuresoftkeymasterdevice.so` is located in `/system/lib64/vndk-28`, which was not in default recovery `LD_LIBRARY_PATH`.
2. **SoC Hardware Naming Mismatch**:
   Android's HAL loader `hw_get_module("keystore", ...)` searches for `keystore.<ro.hardware>.so`. The tablet reports `ro.hardware = mt8765`. However, MediaTek's proprietary TrustZone Keymaster blob is named `keystore.mt6739.so`. Because no `keystore.mt8765.so` existed, the service fell back to software-only implementation and failed to load TrustZone.

### Live Solution & Verification
1. **Module Symlinks Created**:
   - `/vendor/lib64/hw/keystore.mt8765.so -> /vendor/lib64/hw/keystore.mt6739.so`
   - `/vendor/lib64/hw/keystore.default.so -> /vendor/lib64/hw/keystore.mt6739.so`
   - `/vendor/lib/hw/keystore.mt8765.so -> /vendor/lib/hw/keystore.mt6739.so`
   - `/vendor/lib/hw/keystore.default.so -> /vendor/lib/hw/keystore.mt6739.so`
2. **Hardware Keymaster Activated**:
   Started `android.hardware.keymaster@3.0-service` with `LD_LIBRARY_PATH=/vendor/lib64:/vendor/lib64/hw:/system/lib64/vndk-28:/system/lib64:/system/lib64/vndk-sp-28`.
   - Logcat confirmed: `I TrustyKeymaster: Creating device`
   - Service registered with `hwservicemanager`
3. **TrustZone Hardware Cryptographic Handshake**:
   - `libcryptfsfde` queried Keymaster HAL via Binder.
   - Microtrust / TrustZone TEE successfully signed the RSA keymaster blob from the metadata partition.
   - Device mapper created `/dev/block/dm-0`:
     `I:Creating crypto dev "userdata"; cipher=aes-cbc-essiv:sha256, keysize=16, real_dev=/dev/block/platform/bootdevice/by-name/userdata, len=26235354624`
     `I:ioctl err: 0`
4. **Decryption Succeeded**:
   - User submitted PIN via TWRP GUI Mount -> Decrypt Data.
   - Console: `Data successfully decrypted`.
   - Verified active mounts:
     - `/dev/block/dm-0 on /data type ext4 (rw,seclabel,relatime,resuid=10010,resgid=1065,data=ordered)`
     - `/dev/block/dm-0 on /sdcard type ext4 (rw,seclabel,relatime,resuid=10010,resgid=1065,data=ordered)`
   - Verified decrypted contents:
     - Full `/data` hierarchy accessible (`/data/app`, `/data/data`, `/data/system`, etc.).
     - User internal storage accessible (`/data/media/0`: `DCIM`, `Download`, `Pictures`, `Music`, etc.).
     - TWRP File Manager fully operational across internal storage.

---

## 6. Permanent Device Tree Integration

- Updated [`source/device/lenovo/mt8765_P/recovery/root/init.recovery.mt8765.rc`](file:///e:/Project/Lenovo%20Tab%20tb-7305x/tb7305x-lab/source/device/lenovo/mt8765_P/recovery/root/init.recovery.mt8765.rc):
  - Added automated symlink creation for `keystore.mt8765.so` and `keystore.default.so` in `on fs`.
  - Added `setenv LD_LIBRARY_PATH /vendor/lib64:/vendor/lib64/hw:/system/lib64/vndk-28:/system/lib64:/system/lib64/vndk-sp-28` to `service keymaster-3-0`.
  - Added `interface android.hardware.keymaster@3.0::IKeymasterDevice default` declaration to ensure automatic HAL discovery.
