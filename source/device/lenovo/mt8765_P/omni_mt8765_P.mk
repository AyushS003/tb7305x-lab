#
# Copyright (C) 2024 The Android Open Source Project
# Copyright (C) 2024 SebaUbuntu's TWRP device tree generator
#
# SPDX-License-Identifier: Apache-2.0
#

# Inherit from those products. Most specific first.
$(call inherit-product, $(SRC_TARGET_DIR)/product/core_64_bit.mk)
$(call inherit-product, $(SRC_TARGET_DIR)/product/full_base_telephony.mk)

# Inherit some common Omni stuff.
$(call inherit-product, vendor/omni/config/common.mk)

# Inherit from mt8765_P device
# $(call inherit-product, device/lenovo/mt8765_P/device.mk)

PRODUCT_DEVICE := mt8765_P
PRODUCT_NAME := omni_mt8765_P
PRODUCT_BRAND := Lenovo
PRODUCT_MODEL := Lenovo TB-7305X
PRODUCT_MANUFACTURER := lenovo


# Forcefully add mtp support (adb is already there)
# PRODUCT_DEFAULT_PROPERTY_OVERRIDES += \
#    persist.sys.usb.config=mtp \
#    persist.traced.enable=1 
#    ro.com.google.locationfeatures=1 \
#    ro.setupwizard.mode=DISABLED \

# PRODUCT_PROPERTY_OVERRIDES += \
#    persist.traced.enable=1

PRODUCT_GMS_CLIENTID_BASE := android-lenovo-rev2

PRODUCT_BUILD_PROP_OVERRIDES += \
    PRIVATE_BUILD_DESC="full_mt8765_P-user 9 PPR1.180610.011 39 release-keys"

BUILD_FINGERPRINT := Lenovo/LenovoTB-7305X_S/7305X:9/PPR1.180610.011/S000126_220620_ROW:user/release-keys


