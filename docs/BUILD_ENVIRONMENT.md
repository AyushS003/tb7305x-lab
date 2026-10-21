# Lenovo Tab M7 (TB-7305X) Custom Recovery Build Environment Audit

**Document Path:** `tb7305x-lab/docs/BUILD_ENVIRONMENT.md`  
**Target Architecture:** MediaTek `MT8765_P` (arm64-v8a / 32-bit binder)  
**Host System:** Microsoft Windows 10 Home (x64)  
**Audit Date:** October 2026  
**Status:** Phase 1 Complete — Host Resource & Toolchain Assessment  

---

## 1. Executive Summary & Build Decision

```
========================================================================================
BUILD ENVIRONMENT DECISION: LOCAL WINDOWS HOST INSUFFICIENT FOR FULL AOSP BUILD
========================================================================================
[FAIL] Disk Space: Drive C: (19.52 GB free), Drive E: (45.94 GB free).
       Minimum required for TWRP 9.0 source checkout and compilation: 65 - 80 GB.
[FAIL] System Memory: 8.00 GB Physical RAM (Available free: ~1.40 GB).
       Minimum required for AOSP Metalava/Ninja/Clang link passes: 16 GB RAM.
[FAIL] Subsystem Availability: Windows Subsystem for Linux (WSL) is NOT installed.
       Docker is NOT installed.
[FAIL] File System Semantics: Windows NTFS is case-insensitive. Android source builds
       strictly require a case-sensitive POSIX filesystem (ext4).
========================================================================================
RECOMMENDATION: Use a 64-bit Linux Environment (Cloud CI / Dedicated Workstation)
========================================================================================
```

To prevent host system instability, disk exhaustion, or Out-Of-Memory (OOM) compiler crashes, **a full Android/OmniROM source tree MUST NOT be downloaded to this local Windows machine**. 

The build pipeline should be executed using a **dedicated Linux build environment** or a **GitHub Actions Ubuntu CI runner** (which natively provides 75+ GB free NVMe disk space and 16 GB RAM).

---

## 2. Host Machine Resource Audit

A comprehensive hardware and software audit was performed directly on the host system:

### 2.1 Storage Capacity
* **Drive `C:` (System Drive):**
  * Total Capacity: `191,097,729,024 bytes` (~177.97 GiB)
  * Free Space: `19,524,325,376 bytes` (**18.18 GiB free**)
  * Evaluation: **CRITICALLY LOW**. Downloading a source tree here would exhaust disk space and crash the Windows operating system.
* **Drive `E:` (Data Drive):**
  * Total Capacity: `240,040,013,824 bytes` (~223.55 GiB)
  * Free Space: `45,942,980,608 bytes` (**42.78 GiB free**)
  * Evaluation: **INSUFFICIENT**. Minimal TWRP 9.0 source checkout alone requires 35–45 GiB. The subsequent build process produces 20–30 GiB of intermediate object files, leading to a hard disk-full build abort during compilation.

### 2.2 CPU & Memory Topology
* **Processor:** Intel(R) Core(TM) i7-9750H CPU @ 2.60GHz
  * Physical Cores: `6`
  * Logical Threads: `12`
  * Architecture: `x86_64`
* **Physical Memory (RAM):**
  * Total Visible Memory: `8,236,260 KB` (~7.85 GiB)
  * Currently Free Physical Memory: `1,463,884 KB` (~1.40 GiB)
* **Memory Bottleneck Analysis:**
  Android 9 AOSP / OmniROM build passes utilize Java-based static analyzers (`metalava`), Dex compilers, and GNU C++ linkers (`lld`/`gold`). Linking 64-bit recovery binaries and compiling recovery core libraries routinely experiences memory spikes of **10–14 GiB RSS**. An 8 GiB host with 1.4 GiB free RAM will suffer catastrophic paging thrashing or process termination via Windows memory exhaustion.

### 2.3 Virtualization & Linux Subsystems
* **Windows Subsystem for Linux (WSL):** **Not Installed / Not Configured** (Command `wsl.exe --status` returned exit code 1).
* **Docker Container Runtime:** **Not Installed** (`docker` command not recognized).
* **Filesystem Considerations:** Compiling on native Windows NTFS fails because Android build tools generate colliding files that differ only by case (e.g. `xt_DSCP.h` vs `xt_dscp.h`). Case-sensitivity is mandatory.

---

## 3. Minimal TWRP 9.0 Resource & Environment Requirements

Compiling a stable custom recovery for MediaTek MT8765 requires the following minimum specifications:

| Requirement | Minimum Specification | Recommended Specification | Local Host Status |
| :--- | :--- | :--- | :---: |
| **Operating System** | Ubuntu 20.04 LTS (64-bit) | Ubuntu 22.04 LTS (64-bit) | **Windows 10 Home (FAIL)** |
| **Filesystem** | ext4 (Case-sensitive) | ext4 / ZFS / btrfs | **NTFS (FAIL)** |
| **Free Disk Space** | 65 GB | 100+ GB NVMe SSD | **42.78 GB max (FAIL)** |
| **Physical RAM** | 16 GB | 32 GB RAM | **7.85 GB (FAIL)** |
| **Swap Space** | 8 GB | 16 GB | **Unconfigured (FAIL)** |
| **CPU Threads** | 4 threads | 8–16 threads | **12 threads (PASS)** |

---

## 4. Evaluation of Build Environment Alternatives

### Option A: GitHub Actions Ubuntu CI Runner (RECOMMENDED)
* **Architecture:** Ubuntu 22.04 LTS cloud runner (`ubuntu-latest`).
* **Specifications:**
  * Free NVMe Disk Space: `~75 GB` (after runner cleanup)
  * System Memory: `16 GB RAM`
  * Virtual Cores: `2–4 vCPU`
* **Advantages:**
  * **Zero local disk or RAM footprint:** Keeps the host computer 100% stable.
  * **Deterministic & Reproducible:** The build script is defined as code in YAML, guaranteeing identical build results across runs.
  * **Identical to Maintainer Pipeline:** Upstream maintainer `mlm-games` built all TWRP artifacts via GitHub Actions runners.
  * **Direct Artifact Hashing:** Output images and SHA-256 hashes can be uploaded directly to GitHub Releases or artifact storage.

### Option B: Dedicated External Linux Workstation / Cloud VPS
* **Architecture:** Dedicated Ubuntu 20.04 LTS instance (e.g. Hetzner, DigitalOcean, or local Linux machine).
* **Specifications:** 16 GB RAM, 100 GB SSD storage.
* **Advantages:** Interactive debugging of compiler errors; persistent `ccache` speeds up iterative builds.
* **Drawbacks:** Requires provisioning external infrastructure.

### Option C: Reconfiguring Local Windows Host (High Friction / Low Reliability)
* **Procedure Required:**
  1. Delete ~35 GB of files on Drive `E:` to free at least 80 GB of continuous space.
  2. Install WSL2 with Ubuntu 20.04 LTS: `wsl --install -d Ubuntu-20.04`.
  3. Configure `.wslconfig` to allocate 6.5 GB RAM and a 16 GB swap file on Drive `E:`.
  4. Perform the entire git checkout and compilation inside the Linux VHDX (`\\wsl$\Ubuntu-20.04\home\...`).
* **Risks:** Severe system slowdowns, high SSD wear from continuous heavy swap paging, and high probability of OOM build abortion.

---

## 5. Toolchain & Package Specifications for Reproducible Compilation

When executing the build in a Linux environment (Option A or B), the following pinned software stack must be used:

### 5.1 Required Linux Packages (Ubuntu 20.04 LTS)
```bash
sudo apt-get update && sudo apt-get install -y \
    bc bison build-essential ccache curl flex g++-multilib gcc-multilib \
    git gnupg gperf imagemagick lib32ncurses5-dev lib32readline-dev lib32z1-dev \
    liblz4-tool libncurses5 libncurses5-dev libsdl1.2-dev libssl-dev libxml2 \
    libxml2-utils lzop pngcrush rsync schedtool squashfs-tools xsltproc \
    zip zlib1g-dev openjdk-8-jdk python2.7 python3
```

### 5.2 Build Manifest Initialization
```bash
# Initialize Google Repo launcher
mkdir -p ~/bin
curl https://storage.googleapis.com/git-repo-downloads/repo > ~/bin/repo
chmod a+x ~/bin/repo
export PATH=~/bin:$PATH

# Initialize Minimal TWRP 9.0 Manifest
mkdir -p ~/twrp-9.0 && cd ~/twrp-9.0
repo init --depth=1 -u https://github.com/minimal-manifest-twrp/platform_manifest_twrp_omni.git -b twrp-9.0

# Shallow clone repository dependencies
repo sync -c -j$(nproc) --no-clone-bundle --no-tags
```

### 5.3 Device Tree Setup & Lunch
```bash
# Clone the pinned device tree
git clone https://github.com/mlm-games/twrp_lenovo_7305x_m7_mt8765_P.git -b test-decrypt device/lenovo/mt8765_P
cd device/lenovo/mt8765_P
git checkout 076e654ed8014cbc46ed532f45a6ca6fe79cf77c
cd ~/twrp-9.0

# Initialize build environment and compile
source build/envsetup.sh
lunch omni_mt8765_P-eng
mka recoveryimage -j$(nproc)
```

---

## 6. Phase 1 Audit Conclusion

1. **Host Constraint:** Local compilation on this Windows PC is definitively blocked due to physical disk and RAM constraints.
2. **Phase 2 Implementation Strategy:** The reproducible build pipeline should be constructed as a verifiable GitHub Actions workflow or a cloud Linux script.
3. **Artifact Verification:** Any compiled image must be cryptographically hashed and compared against the baseline `23,906,304 byte` image before physical testing is even considered.
