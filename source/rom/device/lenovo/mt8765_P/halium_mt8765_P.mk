#
# Copyright (C) 2024 The Halium Project
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

# Inherit 64-bit architecture
$(call inherit-product, $(SRC_TARGET_DIR)/product/core_64_bit.mk)

# Target uses Halium container architecture
TARGET_USES_HALIUM := true

# Inherit device configuration
$(call inherit-product, device/lenovo/mt8765_P/device.mk)

PRODUCT_DEVICE := mt8765_P
PRODUCT_NAME := halium_mt8765_P
PRODUCT_BRAND := Lenovo
PRODUCT_MODEL := Lenovo TB-7305X
PRODUCT_MANUFACTURER := lenovo

PRODUCT_GMS_CLIENTID_BASE := android-lenovo-rev2

PRODUCT_BUILD_PROP_OVERRIDES += \
    PRIVATE_BUILD_DESC="full_mt8765_P-user 9 PPR1.180610.011 39 release-keys"

BUILD_FINGERPRINT := Lenovo/LenovoTB-7305X_S/7305X:9/PPR1.180610.011/S000126_220620_ROW:user/release-keys
