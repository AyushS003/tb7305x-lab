import subprocess
import json
import os
import re
import sys

SERIAL = "HA154H1C"
ADB_PATH = r"C:\Users\ayush\Downloads\platform-tools-latest-windows\platform-tools\adb.exe"
OUTPUT_DIR = r"E:\Project\Lenovo Tab tb-7305x\tb7305x-lab\inventory"
LOGS_DIR = r"E:\Project\Lenovo Tab tb-7305x\tb7305x-lab\logs"

def run_adb(args, timeout=20):
    cmd = [ADB_PATH, "-s", SERIAL] + args
    try:
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=timeout, encoding='utf-8', errors='replace')
        return proc.returncode, proc.stdout.strip(), proc.stderr.strip()
    except subprocess.TimeoutExpired:
        return -1, "", "Timeout expired"
    except Exception as e:
        return -2, "", str(e)

def run_adb_shell(shell_cmd, timeout=20):
    return run_adb(["shell", shell_cmd], timeout=timeout)

def sanitize(text):
    if not text:
        return ""
    # Mask IMEI (14-16 digits)
    text = re.sub(r'\b\d{14,16}\b', '[REDACTED_IMEI_OR_ID]', text)
    # Mask MAC addresses
    text = re.sub(r'([0-9a-fA-F]{2}[:-]){5}([0-9a-fA-F]{2})', '[REDACTED_MAC]', text)
    # Mask phone numbers
    text = re.sub(r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', '[REDACTED_PHONE]', text)
    return text

def main():
    print(f"Starting inventory collection on target device: {SERIAL}")
    inventory = {
        "device_serial_masked": SERIAL[:2] + "****" + SERIAL[-2:],
        "target_serial": SERIAL,
        "phase": "Phase 1 - Comprehensive Read-Only Inventory",
        "timestamp": None
    }
    
    # Check date on device
    code, out, _ = run_adb_shell("date")
    inventory["device_datetime"] = out

    # 1. Privileges
    code, id_out, _ = run_adb_shell("id")
    code, su_out, _ = run_adb_shell("which su")
    inventory["privileges"] = {
        "adb_shell_id": id_out,
        "su_present": bool(su_out and "not found" not in su_out and code == 0),
        "su_path": su_out if code == 0 else "None"
    }

    # 2. Getprop
    print("Collecting system properties...")
    code, props_raw, _ = run_adb_shell("getprop")
    props = {}
    for line in props_raw.splitlines():
        m = re.match(r'\[(.*?)\]:\s*\[(.*?)\]', line)
        if m:
            props[m.group(1)] = m.group(2)
            
    # Key properties extraction
    key_prop_names = [
        "ro.product.manufacturer", "ro.product.brand", "ro.product.model", "ro.product.device",
        "ro.product.name", "ro.build.fingerprint", "ro.build.version.release", "ro.build.version.sdk",
        "ro.build.version.security_patch", "ro.build.version.incremental", "ro.build.type",
        "ro.build.tags", "ro.build.flavor", "ro.hardware", "ro.board.platform", "ro.boot.hardware",
        "ro.bootloader", "ro.product.cpu.abi", "ro.product.cpu.abilist", "ro.product.cpu.abilist32",
        "ro.product.cpu.abilist64", "ro.zygote", "ro.treble.enabled", "ro.build.ab_update",
        "ro.virtual_ab.enabled", "ro.boot.verifiedbootstate", "ro.boot.vbmeta.device_state",
        "ro.boot.flash.locked", "ro.boot.warranty_bit", "ro.oem_unlock_supported", "sys.oem_unlock_allowed",
        "ro.crypto.state", "ro.crypto.type", "gsm.version.baseband", "ro.mediatek.platform",
        "ro.vendor.mediatek.platform", "ro.config.low_ram", "ro.lmk.low", "ro.vndk.version"
    ]
    key_props = {k: props.get(k, "UNKNOWN") for k in key_prop_names}
    inventory["key_properties"] = key_props
    inventory["all_properties"] = {k: sanitize(v) for k, v in props.items()}

    # 3. CPU & Memory
    print("Collecting CPU and memory topology...")
    _, cpuinfo, _ = run_adb_shell("cat /proc/cpuinfo")
    _, meminfo, _ = run_adb_shell("cat /proc/meminfo")
    _, cpu_freq, _ = run_adb_shell("cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_available_frequencies 2>/dev/null || cat /sys/devices/system/cpu/cpu0/cpufreq/cpuinfo_cur_freq 2>/dev/null")
    _, cpu_gov, _ = run_adb_shell("cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor 2>/dev/null")
    _, cpu_govs_avail, _ = run_adb_shell("cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_available_governors 2>/dev/null")
    _, cpu_online, _ = run_adb_shell("cat /sys/devices/system/cpu/online 2>/dev/null")
    _, zram_stat, _ = run_adb_shell("cat /sys/block/zram0/stat 2>/dev/null || cat /proc/swaps")
    _, top_proc, _ = run_adb_shell("top -n 1 -b -m 10")
    _, dumpsys_mem, _ = run_adb_shell("dumpsys meminfo")

    inventory["cpu_and_memory"] = {
        "cpuinfo": cpuinfo,
        "meminfo": meminfo,
        "cpu_scaling_available_frequencies": cpu_freq,
        "cpu_governor": cpu_gov,
        "cpu_available_governors": cpu_govs_avail,
        "cpu_online": cpu_online,
        "zram_stat": zram_stat,
        "top_processes": top_proc,
        "dumpsys_meminfo_summary": "\n".join([line for line in dumpsys_mem.splitlines() if "Total RAM:" in line or "Free RAM:" in line or "Used RAM:" in line or "Lost RAM:" in line or "ZRAM:" in line])
    }

    # 4. Storage & Partitions
    print("Collecting storage and partition details...")
    _, df_h, _ = run_adb_shell("df -h")
    _, mounts, _ = run_adb_shell("cat /proc/mounts")
    _, partitions, _ = run_adb_shell("cat /proc/partitions")
    _, by_name, _ = run_adb_shell("ls -la /dev/block/platform/*/by-name/ 2>/dev/null || ls -la /dev/block/by-name/ 2>/dev/null")
    _, fstab, _ = run_adb_shell("cat /vendor/etc/fstab* 2>/dev/null || cat /fstab* 2>/dev/null")

    inventory["storage"] = {
        "df_h": df_h,
        "mounts": mounts,
        "partitions": partitions,
        "block_devices_by_name": by_name,
        "fstab": fstab
    }

    # 5. Graphics & Display
    print("Collecting graphics and display details...")
    _, wm_size, _ = run_adb_shell("wm size")
    _, wm_density, _ = run_adb_shell("wm density")
    _, sf_dumpsys, _ = run_adb_shell("dumpsys SurfaceFlinger")
    _, vk_features, _ = run_adb_shell("pm list features | grep -i vulkan")
    _, gl_features, _ = run_adb_shell("pm list features | grep -i opengl")

    inventory["graphics_and_display"] = {
        "wm_size": wm_size,
        "wm_density": wm_density,
        "vulkan_features": vk_features,
        "opengl_features": gl_features,
        "surfaceflinger_summary": "\n".join([l for l in sf_dumpsys.splitlines() if any(k in l for k in ["GLES:", "Hardware Composer", "Display", "Refresh Rate", "EGL"])][:40])
    }

    # 6. Battery & Thermal
    print("Collecting battery and thermal status...")
    _, battery, _ = run_adb_shell("dumpsys battery")
    _, thermal, _ = run_adb_shell("dumpsys thermalservice 2>/dev/null || cat /sys/class/thermal/thermal_zone*/type 2>/dev/null")
    _, thermal_temps, _ = run_adb_shell("cat /sys/class/thermal/thermal_zone*/temp 2>/dev/null")

    inventory["battery_and_thermal"] = {
        "dumpsys_battery": battery,
        "thermal_info": thermal,
        "thermal_temps": thermal_temps
    }

    # 7. VINTF & Architecture
    print("Collecting VINTF manifest and vendor info...")
    _, vintf_manifest, _ = run_adb_shell("cat /vendor/etc/vintf/manifest.xml 2>/dev/null || cat /system/etc/vintf/manifest.xml 2>/dev/null")
    _, apex_list, _ = run_adb_shell("ls -la /apex 2>/dev/null")
    _, packages_list, _ = run_adb_shell("pm list packages -f")

    inventory["android_architecture"] = {
        "vintf_manifest": vintf_manifest,
        "apex_available": apex_list,
        "installed_packages_count": len(packages_list.splitlines()) if packages_list else 0
    }

    # Save package list separately for backup/inventory
    pkg_file = os.path.join(r"E:\Project\Lenovo Tab tb-7305x\tb7305x-lab\backups", "installed_packages.txt")
    with open(pkg_file, "w", encoding="utf-8") as f:
        f.write(packages_list)

    # 8. Radio & Telephony (Sanitized)
    print("Collecting radio architecture (sanitized)...")
    _, baseband, _ = run_adb_shell("getprop gsm.version.baseband")
    _, telephony_dumpsys, _ = run_adb_shell("dumpsys telephony.registry")
    sanitized_telephony = sanitize(telephony_dumpsys)

    inventory["telephony_architecture"] = {
        "baseband": baseband,
        "telephony_summary": "\n".join([l for l in sanitized_telephony.splitlines() if any(k in l for k in ["mDataConnectionState", "mServiceState", "mVoiceRegState", "mRilRadioTechnology"])][:25])
    }

    # Save inventory.json
    json_path = os.path.join(OUTPUT_DIR, "inventory.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(inventory, f, indent=2)
    print(f"Saved inventory.json to {json_path}")

    # Generate inventory.md
    md_path = os.path.join(OUTPUT_DIR, "inventory.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(f"# Lenovo Tab M7 (TB-7305X) Comprehensive Read-Only Inventory\n\n")
        f.write(f"**Target Device Serial**: `{SERIAL}`\n")
        f.write(f"**Inspection Date**: `{inventory.get('device_datetime', 'N/A')}`\n\n")
        
        f.write("## 1. Executive Hardware & Platform Summary\n\n")
        f.write("| Attribute | Value |\n|---|---|\n")
        f.write(f"| **Manufacturer / Brand** | `{key_props.get('ro.product.manufacturer')}` / `{key_props.get('ro.product.brand')}` |\n")
        f.write(f"| **Model / Product** | `{key_props.get('ro.product.model')}` / `{key_props.get('ro.product.name')}` |\n")
        f.write(f"| **Device Codename** | `{key_props.get('ro.product.device')}` |\n")
        f.write(f"| **SoC / Platform** | `{key_props.get('ro.board.platform')}` / `{key_props.get('ro.mediatek.platform')}` |\n")
        f.write(f"| **Hardware ID** | `{key_props.get('ro.hardware')}` |\n")
        f.write(f"| **CPU ABI** | Primary: `{key_props.get('ro.product.cpu.abi')}`, List: `{key_props.get('ro.product.cpu.abilist')}` |\n")
        f.write(f"| **Zygote Process Architecture** | `{key_props.get('ro.zygote')}` |\n")
        f.write(f"| **Android OS Version** | Android `{key_props.get('ro.build.version.release')}` (SDK `{key_props.get('ro.build.version.sdk')}`) |\n")
        f.write(f"| **Android Go Mode (`ro.config.low_ram`)** | `{key_props.get('ro.config.low_ram')}` |\n")
        f.write(f"| **Security Patch** | `{key_props.get('ro.build.version.security_patch')}` |\n")
        f.write(f"| **Build Fingerprint** | `{key_props.get('ro.build.fingerprint')}` |\n")
        f.write(f"| **Baseband / Modem** | `{key_props.get('gsm.version.baseband')}` |\n\n")

        f.write("## 2. Bootloader, Treble & Security State\n\n")
        f.write("| Security / Treble Parameter | Status | Implication |\n|---|---|---|\n")
        f.write(f"| `ro.treble.enabled` | `{key_props.get('ro.treble.enabled')}` | {'Treble GSI architecture is supported' if key_props.get('ro.treble.enabled') == 'true' else 'Non-Treble device'} |\n")
        f.write(f"| `ro.build.ab_update` (A/B Partitioning) | `{key_props.get('ro.build.ab_update')}` | {'A/B Seamless partition layout' if key_props.get('ro.build.ab_update') == 'true' else 'A-only partition layout (System-As-Root or standard)'} |\n")
        f.write(f"| `ro.virtual_ab.enabled` | `{key_props.get('ro.virtual_ab.enabled')}` | Virtual A/B support |\n")
        f.write(f"| `ro.vndk.version` | `{key_props.get('ro.vndk.version')}` | MediaTek Vendor NDK interface version |\n")
        f.write(f"| `ro.boot.flash.locked` | `{key_props.get('ro.boot.flash.locked')}` | 1 = Bootloader Locked, 0 = Unlocked |\n")
        f.write(f"| `ro.boot.verifiedbootstate` | `{key_props.get('ro.boot.verifiedbootstate')}` | Android Verified Boot state |\n")
        f.write(f"| `ro.boot.vbmeta.device_state` | `{key_props.get('ro.boot.vbmeta.device_state')}` | VBMeta verification state |\n")
        f.write(f"| `sys.oem_unlock_allowed` | `{key_props.get('sys.oem_unlock_allowed')}` | OEM unlock toggled in developer options |\n")
        f.write(f"| Shell Privileges | `{inventory['privileges']['adb_shell_id']}` | Shell UID/GID |\n")
        f.write(f"| Root (`su`) Binary | `{inventory['privileges']['su_present']}` | Stock unrooted environment |\n\n")

        f.write("## 3. Display, SurfaceFlinger & Graphics\n\n")
        f.write(f"- **Resolution**: `{inventory['graphics_and_display']['wm_size']}`\n")
        f.write(f"- **Density**: `{inventory['graphics_and_display']['wm_density']}`\n")
        f.write(f"- **Vulkan Features**: `{inventory['graphics_and_display']['vulkan_features']}`\n")
        f.write(f"- **OpenGL ES Features**: `{inventory['graphics_and_display']['opengl_features']}`\n\n")
        f.write("```\n" + inventory['graphics_and_display']['surfaceflinger_summary'] + "\n```\n\n")

        f.write("## 4. CPU & Memory Diagnostics\n\n")
        f.write("### Scaling Frequencies & Governor\n")
        f.write(f"- Online Cores: `{inventory['cpu_and_memory']['cpu_online']}`\n")
        f.write(f"- Active Governor: `{inventory['cpu_and_memory']['cpu_governor']}`\n")
        f.write(f"- Available Governors: `{inventory['cpu_and_memory']['cpu_available_governors']}`\n")
        f.write(f"- Frequencies: `{inventory['cpu_and_memory']['cpu_scaling_available_frequencies']}`\n\n")
        f.write("### RAM Summary\n")
        f.write("```\n" + inventory['cpu_and_memory']['dumpsys_meminfo_summary'] + "\n```\n\n")

        f.write("## 5. Storage Topology & Partitions\n\n")
        f.write("```\n" + inventory['storage']['df_h'] + "\n```\n\n")
        f.write("### Block Device Mapping\n")
        f.write("```\n" + inventory['storage']['block_devices_by_name'] + "\n```\n\n")

        f.write("## 6. Battery & Thermal Status\n\n")
        f.write("```\n" + inventory['battery_and_thermal']['dumpsys_battery'] + "\n```\n")

    print(f"Saved inventory.md to {md_path}")

if __name__ == "__main__":
    main()
