#!/system/bin/sh
# Lenovo Tab M7 (TB-7305X) LineageOS 16.0 Performance & Dual Swap Daemon

# 1. Ensure /data/swapfile exists and has valid permissions
if [ ! -f /data/swapfile ]; then
    dd if=/dev/zero of=/data/swapfile bs=1048576 count=1024
    chmod 600 /data/swapfile
    mkswap /data/swapfile
fi

chmod 600 /data/swapfile

# 2. Reset zram to Priority 10 (Fast in-memory compressed RAM)
swapoff /dev/block/zram0 2>/dev/null
swapon -p 10 /dev/block/zram0 2>/dev/null

# 3. Mount Flash Storage Swap to Priority 5 (Secondary overflow safety net)
swapon -p 5 /data/swapfile 2>/dev/null

# 4. Kernel Virtual Memory (VM) Latency & Cache Tuning
echo 80 > /proc/sys/vm/swappiness
echo 50 > /proc/sys/vm/vfs_cache_pressure
echo 15 > /proc/sys/vm/dirty_ratio
echo 5 > /proc/sys/vm/dirty_background_ratio
echo 0 > /proc/sys/vm/page-cluster

# 5. Global UI Animation speedups (0.5x scales for instantaneous responsiveness)
settings put global window_animation_scale 0.5
settings put global transition_animation_scale 0.5
settings put global animator_duration_scale 0.5

# 6. Low-latency UI thread scheduling
setprop sys.use_fifo_ui 1
