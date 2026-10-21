# Lenovo Tab M7 (TB-7305X) Custom Recovery Build Instructions

**Target Hardware:** Lenovo Tab M7 (`TB-7305X`, MediaTek `MT8765_P` / `MT6739`)  
**Target Recovery:** TWRP 9.0 (OmniROM minimal manifest)  
**Host Environment Required:** 64-bit Linux (Ubuntu 20.04 / 22.04 LTS) or GitHub Actions Cloud Runner  
**Document Path:** `tb7305x-lab/docs/BUILD_INSTRUCTIONS.md`  
**Status:** Validated Build Specification & Workflow Template  

---

## 1. Executive Summary & Build Strategy

Due to physical resource limitations on the local Windows PC (8 GB RAM, 18 GB free on C:, 43 GB free on E:), local compilation is not possible. 

This document defines the **reproducible build pipeline** executed via **GitHub Actions Cloud CI** on a clean `ubuntu-latest` runner (or equivalent dedicated Linux environment).

### Target Builds Defined:
1. **Target A (Reproduction Build):**
   * Tree Branch: `test-decrypt`
   * Pinned Commit: `50e0c68dd183f6c71d7d712eab790c177f834d53`
   * Objective: Verify whether compiling this commit reproduces the baseline image (`23,906,304 bytes`, SHA-256 `79657A7BD1D5EC90B0B027F3509807D05C2B2F7DA49932109210DACBA1DFA7C9`).
2. **Target B (Clean Baseline Build):**
   * Tree Branch: `main`
   * Pinned Commit: `978046687567e3f3d48b2b5996f2a703b195be3b`
   * Objective: Produce an unpolluted recovery binary with stock init scripts, clean partition tables, and unencrypted backup/restore functionality.

---

## 2. GitHub Actions Runner Specifications & Cost Model

### 2.1 Runner Resource Profile (`ubuntu-latest`)
* **Operating System:** Ubuntu 22.04 LTS (x64)
* **Compute Resources:**
  * Public Repository: **4 vCPUs, 16 GB RAM**
  * Private Repository: **2 vCPUs, 8 GB RAM**
* **Disk Footprint Management:**
  * Initial Free Space: ~18–21 GB (Insufficient for full checkout).
  * Post-Debloat Free Space: **~65–70 GB free** (via aggressive removal of preinstalled Android SDKs, .NET, Haskell, and Docker caches).
  * Swap Allocation: **12 GB swap file** created to guarantee zero OOM compiler aborts during Clang link passes.
  * Shallow Checkout Footprint: `--depth=1` download requires ~20 GB. Output build directory requires ~10 GB. Peak disk usage is ~30–34 GB, leaving >25 GB headroom.

### 2.2 Expected Runtime & Cost Model
* **Expected Runtime:** **35 to 55 minutes** for shallow checkout, dependency setup, and recovery image build.
* **Cost in Public Repository:** **$0.00 (100% Free)**. GitHub Actions provides unlimited runner minutes for public repositories.
* **Cost in Private Repository:** Consumes ~45 minutes from GitHub's 2,000 free monthly minutes. (If monthly allowance is exhausted, billed at $0.008/min = **~$0.36**).
* **Policy:** Always execute in a **public repository** or with explicit approval.

---

## 3. GitHub Actions CI Workflow (`.github/workflows/build_recovery.yml`)

The following workflow definition provides automated disk debloating, pinned checkouts, build execution, log preservation, and artifact hashing:

```yaml
name: Reproducible TWRP Recovery Build

on:
  workflow_dispatch:
    inputs:
      build_target:
        description: 'Select Build Target'
        required: true
        type: choice
        default: 'reproduction_test_decrypt'
        options:
          - 'reproduction_test_decrypt'
          - 'clean_baseline_main'
      upload_release:
        description: 'Publish as GitHub Release'
        required: false
        type: boolean
        default: false

permissions:
  contents: write

jobs:
  build_recovery:
    name: Build Recovery (${{ github.event.inputs.build_target }})
    runs-on: ubuntu-latest
    timeout-minutes: 120

    steps:
      - name: 1. Audit Runner Environment
        run: |
          echo "=== CPU Profile ==="
          nproc
          cat /proc/cpuinfo | grep "model name" | head -n 1
          echo "=== Memory Profile ==="
          free -h
          echo "=== Initial Disk Space ==="
          df -h

      - name: 2. Free Disk Space (Debloat Runner)
        run: |
          echo "Purging unnecessary preinstalled tools and SDKs..."
          sudo rm -rf /usr/local/lib/android
          sudo rm -rf /usr/share/dotnet
          sudo rm -rf /opt/ghc
          sudo rm -rf /opt/hostedtoolcache/CodeQL
          sudo rm -rf /usr/local/share/boost
          sudo docker image prune --all --force || true
          sudo docker builder prune --all --force || true
          echo "=== Disk Space After Debloat ==="
          df -h

      - name: 3. Configure 12 GB Swap Space
        run: |
          sudo fallocate -l 12G /swapfile
          sudo chmod 600 /swapfile
          sudo mkswap /swapfile
          sudo swapon /swapfile
          echo "=== Memory with Swap ==="
          free -h

      - name: 4. Install Toolchain Dependencies
        run: |
          sudo apt-get update
          sudo apt-get install -y \
            bc bison build-essential ccache curl flex g++-multilib gcc-multilib \
            git gnupg gperf imagemagick lib32ncurses5-dev lib32readline-dev lib32z1-dev \
            liblz4-tool libncurses5 libncurses5-dev libsdl1.2-dev libssl-dev libxml2 \
            libxml2-utils lzop pngcrush rsync schedtool squashfs-tools xsltproc \
            zip zlib1g-dev openjdk-8-jdk python2 python3
          
          # Force Python 2 as system python for Android 9 build tools
          sudo update-alternatives --install /usr/bin/python python /usr/bin/python2 1
          sudo update-alternatives --install /usr/bin/python python /usr/bin/python3 2
          sudo update-alternatives --set python /usr/bin/python2
          python --version

      - name: 5. Install Google Repo Tool
        run: |
          mkdir -p ~/bin
          curl -s https://storage.googleapis.com/git-repo-downloads/repo > ~/bin/repo
          chmod a+x ~/bin/repo
          sudo ln -sf ~/bin/repo /usr/bin/repo
          git config --global user.name "Recovery-CI-Builder"
          git config --global user.email "ci-builder@users.noreply.github.com"
          git config --global color.ui false

      - name: 6. Initialize Minimal TWRP 9.0 Manifest
        run: |
          mkdir -p ~/twrp_workspace
          cd ~/twrp_workspace
          repo init --depth=1 -u https://github.com/minimal-manifest-twrp/platform_manifest_twrp_omni.git -b twrp-9.0
          repo sync -c -j$(nproc) --no-clone-bundle --no-tags --force-sync

      - name: 7. Checkout Pinned Device Tree
        run: |
          cd ~/twrp_workspace
          mkdir -p device/lenovo/mt8765_P
          
          if [ "${{ github.event.inputs.build_target }}" == "reproduction_test_decrypt" ]; then
            echo "Checking out REPRODUCTION target (branch test-decrypt, commit 50e0c68dd183f6c71d7d712eab790c177f834d53)..."
            git clone https://github.com/mlm-games/twrp_lenovo_7305x_m7_mt8765_P.git -b test-decrypt device/lenovo/mt8765_P
            cd device/lenovo/mt8765_P
            git checkout 50e0c68dd183f6c71d7d712eab790c177f834d53
          else
            echo "Checking out CLEAN BASELINE target (branch main, commit 978046687567e3f3d48b2b5996f2a703b195be3b)..."
            git clone https://github.com/mlm-games/twrp_lenovo_7305x_m7_mt8765_P.git -b main device/lenovo/mt8765_P
            cd device/lenovo/mt8765_P
            git checkout 978046687567e3f3d48b2b5996f2a703b195be3b
          fi
          
          echo "Resolved Device Tree Commit:"
          git log -n 1 --oneline

      - name: 8. Snapshot Exact Manifest Revisions
        run: |
          cd ~/twrp_workspace
          repo manifest -r -o pinned_build_manifest.xml
          cp pinned_build_manifest.xml $GITHUB_WORKSPACE/

      - name: 9. Compile TWRP Recovery Image
        run: |
          cd ~/twrp_workspace
          export ALLOW_MISSING_DEPENDENCIES=true
          source build/envsetup.sh
          lunch omni_mt8765_P-eng
          
          # Clean previous build artifacts and build recoveryimage
          make clean
          make -j$(nproc) recoveryimage 2>&1 | tee $GITHUB_WORKSPACE/build.log

      - name: 10. Audit Build Outputs & Generate Cryptographic Hashes
        run: |
          cd ~/twrp_workspace/out/target/product/mt8765_P
          mkdir -p $GITHUB_WORKSPACE/artifacts
          
          # Copy outputs
          cp recovery.img $GITHUB_WORKSPACE/artifacts/recovery.img
          cp ramdisk-recovery.cpio $GITHUB_WORKSPACE/artifacts/ramdisk-recovery.cpio
          cp $GITHUB_WORKSPACE/build.log $GITHUB_WORKSPACE/artifacts/build.log
          cp $GITHUB_WORKSPACE/pinned_build_manifest.xml $GITHUB_WORKSPACE/artifacts/pinned_build_manifest.xml
          
          # Generate Checksums
          cd $GITHUB_WORKSPACE/artifacts
          sha256sum * > SHA256SUMS.txt
          md5sum * > MD5SUMS.txt
          
          echo "=== BUILD ARTIFACTS AND HASHES ==="
          cat SHA256SUMS.txt
          ls -lah

      - name: 11. Archive Build Artifacts & Logs
        uses: actions/upload-artifact@v4
        with:
          name: twrp-${{ github.event.inputs.build_target }}-${{ github.run_id }}
          path: artifacts/
          retention-days: 90

      - name: 12. Publish Release (Optional)
        if: ${{ github.event.inputs.upload_release == 'true' }}
        uses: softprops/action-gh-release@v2
        with:
          files: artifacts/*
          tag_name: twrp-build-${{ github.run_id }}
          name: TWRP Build - ${{ github.event.inputs.build_target }} (${{ github.run_id }})
          body_path: artifacts/SHA256SUMS.txt
```

---

## 4. Manual Linux Build Instructions (Alternative Local/VM Workflow)

For developers building on a local Ubuntu 20.04/22.04 LTS workstation with at least 80 GB free disk space and 16 GB RAM:

```bash
# 1. Update and install packages
sudo apt-get update && sudo apt-get install -y \
  bc bison build-essential curl flex g++-multilib gcc-multilib git gnupg gperf \
  imagemagick lib32ncurses5-dev lib32readline-dev lib32z1-dev liblz4-tool \
  libncurses5 libncurses5-dev libsdl1.2-dev libssl-dev libxml2 libxml2-utils \
  lzop pngcrush rsync schedtool squashfs-tools xsltproc zip zlib1g-dev \
  openjdk-8-jdk python2 python3

# 2. Configure python2
sudo update-alternatives --install /usr/bin/python python /usr/bin/python2 1
sudo update-alternatives --install /usr/bin/python python /usr/bin/python3 2
sudo update-alternatives --set python /usr/bin/python2

# 3. Setup workspace
mkdir -p ~/twrp-build && cd ~/twrp-build
repo init --depth=1 -u https://github.com/minimal-manifest-twrp/platform_manifest_twrp_omni.git -b twrp-9.0
repo sync -c -j$(nproc) --no-clone-bundle --no-tags

# 4. Clone pinned device tree
git clone https://github.com/mlm-games/twrp_lenovo_7305x_m7_mt8765_P.git -b test-decrypt device/lenovo/mt8765_P
cd device/lenovo/mt8765_P
git checkout 50e0c68dd183f6c71d7d712eab790c177f834d53
cd ~/twrp-build

# 5. Build
export ALLOW_MISSING_DEPENDENCIES=true
source build/envsetup.sh
lunch omni_mt8765_P-eng
make -j$(nproc) recoveryimage
```

---

## 5. Build Validation & Checksum Verification SOP

Upon completion of any CI or manual build pass:
1. Verify output file size is exactly `<= 25,165,824 bytes` (partition boundary).
2. Calculate SHA-256 of `recovery.img`:
   ```bash
   sha256sum recovery.img
   ```
3. Record hash, linker logs, and build manifest in `docs/CI_BUILD_RESULTS.md`.
4. Run static validation ([docs/STATIC_VALIDATION.md](file:///E:/Project/Lenovo%20Tab%20tb-7305x/tb7305x-lab/docs/STATIC_VALIDATION.md)) before any device testing.
