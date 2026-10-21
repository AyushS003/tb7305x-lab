# Lenovo Tab M7 (TB-7305X) Autonomous Android Benchmark, Firmware Research & Custom ROM Engineering Lab

## Device Context
- **Target Serial**: `HA154H1C`
- **Product**: `LenovoTB-7305X_S`
- **Model**: `Lenovo_TB_7305X`
- **Device Codename**: `7305X`
- **Host System**: Windows NT 10.0.19045 (PowerShell / Python 3.12.10)
- **Platform-Tools Path**: `C:\Users\ayush\Downloads\platform-tools-latest-windows\platform-tools\adb.exe`

## Workspace Organization
- `reports/`: Comprehensive engineering reports, markdown and HTML outputs, compatibility matrices, recovery plans.
- `scripts/`: Automated diagnostics, benchmark drivers, debloating scripts, rollback scripts.
- `logs/`: Verbatim console logs, exit codes, stderr/stdout from commands and diagnostic probes.
- `benchmarks/`: Raw metrics, CSV/JSON outputs for CPU, RAM, storage, UI, battery/thermal tests.
- `inventory/`: Complete hardware, partition, kernel, vendor, and Treble property inventory (`inventory.json`, `inventory.md`).
- `firmware/`: Stock ROM packages, scatter files, partition table metadata, recovery documentation.
- `recovery/`: TWRP and recovery analysis, partition layout mappings.
- `roms/`: Evaluated GSI / ROM images, SHA-256 checksums, compatibility analysis.
- `source/`: Kernel, device tree, and vendor HAL references.
- `builds/`: Build artifacts and scripts.
- `checksums/`: SHA-256 hashes of all analyzed files, binaries, images.
- `backups/`: Backups of safe-to-read partitions, user package lists, device properties.
