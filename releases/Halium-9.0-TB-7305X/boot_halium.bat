@echo off
title Lenovo Tab M7 (TB-7305X) - Halium 9.0 Live Boot
color 0B
echo ================================================================
echo   Lenovo Tab M7 (TB-7305X) - Halium 9.0 Live Boot Test
echo ================================================================
echo.
echo  This script boots Halium 9.0 in live mode using "fastboot boot".
echo  Your existing ROM (LineageOS) and boot partition will NOT be touched!
echo.
echo  Prerequisites:
echo    1. USB Cable connected to PC
echo    2. Device in FASTBOOT mode ("FASTBOOT mode..." on screen)
echo.

set "FASTBOOT_BIN=fastboot"
where fastboot >nul 2>nul
if %errorlevel% neq 0 (
    if exist "C:\Users\ayush\Downloads\platform-tools-latest-windows\platform-tools\fastboot.exe" (
        set "FASTBOOT_BIN=C:\Users\ayush\Downloads\platform-tools-latest-windows\platform-tools\fastboot.exe"
    ) else (
        echo [ERROR] 'fastboot' was not found in your system PATH or platform-tools folder.
        pause
        exit /b 1
    )
)

if not exist "%~dp0halium-boot.img" (
    echo [ERROR] halium-boot.img was not found in this folder!
    pause
    exit /b 1
)

echo [*] Checking fastboot device connection...
%FASTBOOT_BIN% devices
echo.

echo [*] Booting Halium 9.0 live kernel into device RAM...
%FASTBOOT_BIN% boot "%~dp0halium-boot.img"

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Fastboot boot failed. Ensure device bootloader is unlocked.
    pause
    exit /b 1
)

echo.
echo ================================================================
echo [SUCCESS] Halium 9.0 kernel dispatched to TB-7305X RAM!
echo.
echo Next Steps for Halium Debugging:
echo   1. The tablet screen may remain black or show the Lenovo splash.
echo   2. A USB Ethernet / RNDIS network adapter will appear on your PC.
echo   3. Set PC IP to 192.168.2.1 / Subnet 255.255.255.0.
echo   4. Connect to Halium initramfs shell via:
echo        telnet 192.168.2.15
echo   5. Inspect kernel logs inside telnet:
echo        dmesg ^| grep -i error
echo ================================================================
pause
