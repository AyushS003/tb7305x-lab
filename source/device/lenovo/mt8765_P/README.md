# Android twrp device tree for Lenovo TB-7305X (mt8765_P)

Works after unlocking bootloader and flashing recovery by fastboot.

```
fastboot flash recovery recovery.img
```

You can use the recovery name instead of <recovery.img>

## Features

Works:

- [X] ADB
- [ ] Decryption
- [X] Display
- [X] Touch
- [X] Flashing
- [X] MTP
- [X] Sideload
- [X] USB OTG
- [X] Vibrator


#### Thanks to 
- Twrptdgen
- The recovery from 4pda for reference

## Notes
> This device does not have a vbmeta partition so you may have to either replace hexcode of string "verify" in boot.img to 0s or flash the disable_dm_verity_force_decrypt.zip afterwards to disable avb

> The kernel (i think but it could also be the modem parts or nvdata as the logcat show errors based on them) does not allow booting into some GSIs (tested, didn't go past boot animation -> lineage-os A14 to A9, arrowos A11, caos-A11, /e/-a10) but it does allow adb logcatting for AOSP A9 (look at the start)...

> If you have tried any GSI and it boots, please open an issue
