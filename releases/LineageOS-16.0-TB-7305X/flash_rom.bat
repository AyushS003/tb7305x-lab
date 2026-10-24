@echo off
setlocal enabledelayedexpansion
title Lenovo Tab M7 (TB-7305X) LineageOS 16.0 & TWRP Installer
color 0B

echo ====================================================================
echo      Lenovo Tab M7 (TB-7305X) LineageOS 16.0 Fastboot Installer
echo ====================================================================
echo.
echo This tool will flash:
echo   1. TWRP 3.3.1 Custom Recovery     [recovery.img]
echo   2. LineageOS 16.0 Kernel           [boot.img]
echo   3. LineageOS 16.0 System Image     [system.img]
echo.
echo Make sure your tablet is connected in FASTBOOT mode!
echo (Screen should show "FASTBOOT mode...")
echo.
echo Press any key to start flashing, or close this window to cancel.
pause >nul

echo.
echo [1/4] Checking fastboot device connection...
fastboot devices
if errorlevel 1 (
    echo.
    echo [ERROR] No Fastboot device detected!
    echo Please make sure:
    echo  - Your tablet is in Fastboot mode (adb reboot bootloader)
    echo  - USB cable is securely connected
    echo  - Fastboot / MediaTek drivers are installed on Windows
    echo.
    pause
    exit /b 1
)

echo.
echo [2/4] Flashing TWRP Custom Recovery...
fastboot flash recovery recovery.img
if errorlevel 1 (
    echo [ERROR] Failed to flash recovery!
    pause
    exit /b 1
)
echo [PASS] Recovery flashed successfully.

echo.
echo [3/4] Flashing LineageOS 16.0 Boot Kernel...
fastboot flash boot boot.img
if errorlevel 1 (
    echo [ERROR] Failed to flash boot partition!
    pause
    exit /b 1
)
echo [PASS] Boot kernel flashed successfully.

echo.
echo [4/4] Flashing LineageOS 16.0 System-as-Root Image...
echo (Please wait, this will take approximately 1-2 minutes...)
fastboot flash system system.img
if errorlevel 1 (
    echo [ERROR] Failed to flash system partition!
    pause
    exit /b 1
)
echo [PASS] System partition flashed successfully.

echo.
echo ====================================================================
echo                 FLASHING COMPLETED SUCCESSFULLY!
echo ====================================================================
echo.
echo IMPORTANT: If this is your first time installing LineageOS on a stock tablet:
echo  1. You must format data in TWRP to remove stock encryption!
echo  2. To do so, reboot to TWRP: Wipe -^> Format Data -^> type 'yes'
echo.
set /p CHOICE="Do you want to reboot into TWRP Recovery now? (Y/N): "
if /i "!CHOICE!"=="Y" (
    echo Rebooting into TWRP Recovery...
    fastboot reboot recovery
) else (
    echo Rebooting into LineageOS 16.0...
    fastboot reboot
)

echo.
echo Done! Enjoy LineageOS 16.0 on your Lenovo Tab M7!
pause
