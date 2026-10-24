# LineageOS 16.0 (Android 9 Pie) & TWRP 3.3.1 for Lenovo Tab M7 (TB-7305X)

**Device**: Lenovo Tab M7 (`TB-7305X`)  
**Chipset**: MediaTek MT8765 / MT6739 (4x Cortex-A53)  
**GPU**: PowerVR Rogue GE8100  
**Android Version**: 9.0 (Pie) / LineageOS 16.0  
**Kernel**: Linux 4.4.146 (permissive, dm-verity disabled)  

---

## 1. What Works
- **Display & GPU**: Native 600x1024 resolution with PowerVR GE8100 hardware acceleration.
- **Touchscreen**: `mtk-tpd` capacitive multitouch with tuned low latency (`touch_slop = 8`).
- **Audio & Media**: Sound playback, volume attenuation, and hardware codecs.
- **Physical Keys**: Power and Volume Up/Down buttons.
- **Battery & Charging**: USB charging controller and accurate battery level/voltage reporting.
- **Storage & I/O**: Solid-state `deadline` I/O scheduler + 512 KB read-ahead cache.
- **Memory Optimization**: 4.0 GB virtual memory (1.9 GB physical RAM + 1.0 GB compressed zRAM + 1.0 GB flash storage swapfile).
- **AOT Machine Code**: Core apps (`SystemUI`, `Settings`, `Launcher3`) precompiled to native 64-bit ARM machine code (`speed` profile) for zero-stutter performance.
- **UI Responsiveness**: 0.5x animation scales + real-time UI thread scheduling (`sys.use_fifo_ui = 1`).
- **Bloatware Free**: Pure LineageOS without OEM spyware or MediaTek AEE debug overhead.
- **Root Shell**: Unsecured root ADB enabled (`adbd` runs as root).

---

## 2. Package Contents
| File | Description | Partition |
| :--- | :--- | :--- |
| `recovery.img` | TWRP 3.3.1 Custom Recovery with touch & MTP support | `recovery` |
| `boot.img` | LineageOS 16.0 Linux Kernel 4.4.146 | `boot` |
| `system.img` | LineageOS 16.0 System-as-Root partition image | `system` |
| `flash_rom.bat` | Windows 1-Click Fastboot automated flasher | Host Script |
| `flash_rom.sh` | Linux/macOS Fastboot automated flasher | Host Script |
| `INSTRUCTIONS.txt` | Quick-start step-by-step guide | Documentation |
| `SHA256SUMS.txt` | Cryptographic SHA-256 verification hashes | Verification |

---

## 3. Quick Installation Steps

### Step 1: Unlock Bootloader
1. On your tablet, go to **Settings > About Tablet** and tap **Build Number** 7 times.
2. Go to **Settings > System > Developer Options**.
3. Enable **OEM Unlocking** and **USB Debugging**.
4. In terminal/cmd on PC:
   ```cmd
   adb reboot bootloader
   fastboot flashing unlock
   ```
5. Press **Volume Up** on the tablet when prompted to confirm the bootloader unlock.

### Step 2: Flash the ROM
Double-click `flash_rom.bat` on Windows (or run `./flash_rom.sh` on Linux/macOS) while your tablet is connected in Fastboot mode.

Or run manually:
```cmd
fastboot flash recovery recovery.img
fastboot flash boot boot.img
fastboot flash system system.img
```

### Step 3: Format Data in TWRP (Critical First-Time Step)
To remove stock factory encryption and allow LineageOS to boot:
1. Boot into TWRP Recovery:
   ```cmd
   fastboot reboot recovery
   ```
2. In TWRP, tap **Wipe > Format Data**, type `yes`, and press Enter.
3. Tap **Wipe > Advanced Wipe**, select **Cache** and **Dalvik / ART Cache**, then swipe to wipe.
4. Tap **Reboot > System**.

### Step 4: First Boot
The first boot takes approximately 2 to 3 minutes. The LineageOS Setup Wizard will appear upon completion!
