#
# Copyright (C) 2024 The Android Open Source Project
# Copyright (C) 2024 SebaUbuntu's TWRP device tree generator
#
# SPDX-License-Identifier: Apache-2.0
#

DEVICE_PATH := device/lenovo/mt8765_P

# For building with minimal manifest
ALLOW_MISSING_DEPENDENCIES := true

# Architecture
TARGET_ARCH := arm64
TARGET_ARCH_VARIANT := armv8-a
TARGET_CPU_ABI := arm64-v8a
TARGET_CPU_ABI2 := 
TARGET_CPU_VARIANT := generic
TARGET_CPU_VARIANT_RUNTIME := generic

TARGET_2ND_ARCH := arm
TARGET_2ND_ARCH_VARIANT := armv7-a-neon
TARGET_2ND_CPU_ABI := armeabi-v7a
TARGET_2ND_CPU_ABI2 := armeabi
TARGET_2ND_CPU_VARIANT := generic
TARGET_2ND_CPU_VARIANT_RUNTIME := generic

# APEX
OVERRIDE_TARGET_FLATTEN_APEX := true

# Bootloader
TARGET_BOOTLOADER_BOARD_NAME := mt8765_P
TARGET_NO_BOOTLOADER := true

# Display
TARGET_SCREEN_DENSITY := 160

# Kernel
BOARD_BOOTIMG_HEADER_VERSION := 1
BOARD_KERNEL_BASE := 0x40078000
BOARD_KERNEL_CMDLINE := bootopt=64S3,32N2,64N2 buildvariant=user veritykeyid=id:7e4333f9bba00adfe0ede979e28ed1920492b40f
BOARD_KERNEL_PAGESIZE := 2048
BOARD_RAMDISK_OFFSET := 0x04f88000
BOARD_KERNEL_TAGS_OFFSET := 0x03f88000
TARGET_KERNEL_ARCH := arm64
TARGET_KERNEL_HEADER_ARCH := arm64
# BOARD_KERNEL_IMAGE_NAME := Image
# BOARD_KERNEL_SEPARATED_DTBO := true
# TARGET_KERNEL_CONFIG := mt8765_P_defconfig
# TARGET_KERNEL_SOURCE := kernel/lenovo/mt8765_P
BOARD_MKBOOTIMG_ARGS += --header_version $(BOARD_BOOTIMG_HEADER_VERSION)
BOARD_MKBOOTIMG_ARGS += --ramdisk_offset $(BOARD_RAMDISK_OFFSET)
BOARD_MKBOOTIMG_ARGS += --tags_offset $(BOARD_KERNEL_TAGS_OFFSET)

# Kernel - prebuilt
# TARGET_FORCE_PREBUILT_KERNEL := true
# ifeq ($(TARGET_FORCE_PREBUILT_KERNEL),true)
TARGET_PREBUILT_KERNEL := $(DEVICE_PATH)/prebuilt/kernel
BOARD_PREBUILT_DTBOIMAGE := $(DEVICE_PATH)/prebuilt/dtbo.img

# Partitions
BOARD_BUILD_SYSTEM_ROOT_IMAGE := true
BOARD_FLASH_BLOCK_SIZE := 131072 # (BOARD_KERNEL_PAGESIZE * 64)
BOARD_BOOTIMAGE_PARTITION_SIZE := 13859744
BOARD_RECOVERYIMAGE_PARTITION_SIZE := 25165824
BOARD_HAS_LARGE_FILESYSTEM := true
BOARD_SYSTEMIMAGE_PARTITION_TYPE := ext4
BOARD_SYSTEMIMAGE_PARTITION_SIZE := 3909091328 # 3709MB
BOARD_USERDATAIMAGE_FILE_SYSTEM_TYPE := ext4

# Workaround for error copy vendor files to ramdisk (if any)
BOARD_VENDORIMAGE_FILE_SYSTEM_TYPE := ext4
BOARD_VENDORIMAGE_PARTITION_SIZE := 400556032 # 381MB
TARGET_COPY_OUT_VENDOR := vendor

# Platform
TARGET_BOARD_PLATFORM := mt6739

# File systems
TARGET_USERIMAGES_USE_EXT4 := true
TARGET_USERIMAGES_USE_F2FS := true

# Security patch level
VENDOR_SECURITY_PATCH := 2021-08-01

# Hack: prevent anti rollback
PLATFORM_SECURITY_PATCH := 2099-12-31
VENDOR_SECURITY_PATCH := 2099-12-31
PLATFORM_VERSION := 16.1.0

# TWRP Configuration
TW_THEME := portrait_hdpi
TW_SCREEN_BLANK_ON_BOOT := true
TW_INPUT_BLACKLIST := "hbtp_vm"
TW_USE_TOOLBOX := true
TW_DEVICE_VERSION := ragebreaker
TW_MAX_BRIGHTNESS := 190

# System as root
BOARD_BUILD_SYSTEM_ROOT_IMAGE := true
# BOARD_ROOT_EXTRA_FOLDERS := bluetooth dsp firmware persist
BOARD_SUPPRESS_SECURE_ERASE := true

# # Data partition
# BOARD_USERDATAIMAGE_FILE_SYSTEM_TYPE := ext4
# BOARD_USERDATAIMAGE_PARTITION_SIZE := 25686630400 # 24499MB in bytes

# # MTP
# TW_MTP_DEVICE := /dev/mtp_usb
# TW_MTP_STORAGE_ID := 65537
# TW_MTP_DEVICE := ? #(name of device to will show on pc)
# TARGET_VENDOR_ID := 0x0e8d
# TARGET_PRODUCT_ID := 0x2008
# BOARD_USES_MTP := true


# Internal storage settings
#TW_INTERNAL_STORAGE_PATH := "/data/media"
#TW_INTERNAL_STORAGE_MOUNT_POINT := "data"

#  FDE or FBE
# # Crypto (Doesnt work)
# TW_INCLUDE_CRYPTO := true
# TW_INCLUDE_FBE := true
# TW_CRYPTO_FS_TYPE := "ext4"
# TW_CRYPTO_REAL_BLKDEV := "/dev/block/mmcblk0p33"
# TW_CRYPTO_MNT_POINT := "/data"
# TW_CRYPTO_FS_OPTIONS := "noatime,nosuid,nodev,noauto_da_alloc,errors=panic wait,check,formattable,quota,reservedsize=128m,formattable,resize"
# TW_CRYPTO_KEY_LOC := "/dev/block/platform/bootdevice/by-name/metadata"
# TW_INCLUDE_CRYPTO_FBE := true
# TW_USE_FSCRYPT_POLICY := 1
# TW_INCLUDE_FBE_METADATA_DECRYPT := true
# BOARD_USES_METADATA_PARTITION := true
# # TW_INCLUDE_CRYPTO_FDE := true

# Save Space (Flags from - https://xdaforums.com/t/twrp-flags-for-boardconfig-mk.3333970/)
# TW_EXCLUDE_ENCRYPTED_BACKUPS := true
TW_EXCLUDE_APP_MANAGER := true
# BOARD_HAS_NO_REAL_SDCARD := true # disables things like sdcard partitioning and may save you some space if TWRP isn't fitting in your recovery partition (for system-as-root?)
TW_NO_EXFAT_FUSE := true
TARGET_BOOTANIMATION_TEXTURE_CACHE := false
TARGET_BOOTANIMATION_USE_RGB565 := true
#TW_NO_SCREEN_TIMEOUT := true
TW_EXTRA_LANGUAGES := true


# This would work here? (for system-as-root)
RECOVERY_SDCARD_ON_DATA := true

# # Disables MTP
#TW_NO_USB_STORAGE := true #(if set, disables MTP)
#TW_EXCLUDE_MTP := true #(if set, excludes MTP support)

# # ?
#TARGET_USE_CUSTOM_LUN_FILE_PATH := "/sys/class/android_usb/android0/f_mass_storage/lun0/file"
# # Not very sure, I guess it allows you to simply pop in the lunfile itself
#BOARD_UMS_LUNFILE := 

# TW_HAS_NO_RECOVERY_PARTITION := true (if recovery in boot.img)

# USB driver path = /sys/bus/usb/drivers/usbfs
