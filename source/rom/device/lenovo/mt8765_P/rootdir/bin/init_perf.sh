#!/system/bin/sh
# Lenovo Tab M7 (TB-7305X) LineageOS 16.0 Performance Engine

# 1. Dual-Tier Swap (zRAM 1GB Priority 10, Storage Swapfile 1GB Priority 5)
if [ ! -f /data/swapfile ]; then
    dd if=/dev/zero of=/data/swapfile bs=1048576 count=1024
    chmod 600 /data/swapfile
    mkswap /data/swapfile
fi
chmod 600 /data/swapfile

# Only reset zram priority if not already priority 10
if ! grep -q "zram0.*10" /proc/swaps 2>/dev/null; then
    swapoff /dev/block/zram0 2>/dev/null
    swapon -p 10 /dev/block/zram0 2>/dev/null
fi

if ! grep -q "swapfile" /proc/swaps 2>/dev/null; then
    swapon -p 5 /data/swapfile 2>/dev/null
fi

# 2. Kernel Virtual Memory (VM) Latency Tuning
echo 80 > /proc/sys/vm/swappiness
echo 50 > /proc/sys/vm/vfs_cache_pressure
echo 15 > /proc/sys/vm/dirty_ratio
echo 5 > /proc/sys/vm/dirty_background_ratio
echo 0 > /proc/sys/vm/page-cluster

# 3. Flash Storage (eMMC) I/O Optimization
for q in /sys/block/mmcblk*/queue; do
    if [ -d "$q" ]; then
        echo deadline > "$q/scheduler" 2>/dev/null
        echo 512 > "$q/read_ahead_kb" 2>/dev/null
        echo 0 > "$q/add_random" 2>/dev/null
        echo 0 > "$q/iostats" 2>/dev/null
    fi
done

# 4. SurfaceFlinger & GPU Hardware Composition
setprop debug.sf.hw 1
setprop debug.egl.hw 1
setprop debug.sf.latch_unsignaled 1
setprop persist.sys.use_dithering 0
setprop video.accelerate.hw 1
setprop sys.use_fifo_ui 1

# 5. Touchscreen Latency & Scroll Responsiveness
setprop view.touch_slop 8
setprop view.scroll_friction 0.005

# 6. Disable MediaTek Background Debug Engine (AEE)
setprop ctl.stop aee_aedv
setprop ctl.stop aee_aedv64
setprop persist.vendor.aev.enable 0
setprop persist.vendor.aeev.core.direct disable

# 7. Global UI Animation Speedups (0.5x scales)
settings put global window_animation_scale 0.5
settings put global transition_animation_scale 0.5
settings put global animator_duration_scale 0.5
