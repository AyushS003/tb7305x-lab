@echo off
title Lenovo Tab M7 (TB-7305X) - Flash Halium 9.0 Boot Partition
color 0C
echo ================================================================
echo   Lenovo Tab M7 (TB-7305X) - Flash Halium 9.0 Boot Partition
echo ================================================================
echo.
echo  WARNING:
echo  This will overwrite the current "boot" partition with halium-boot.img.
echo  To revert back to LineageOS later, reflash the LineageOS boot.img
echo  from the LineageOS-16.0-TB-7305X release folder.
echo.
set /p CONFIRM="Type 'YES' to proceed with flashing boot partition: "
if /i not "%CONFIRM%"=="YES" (
    echo [ABORTED] Flashing cancelled.
    pause
    exit /b 0
)

where fastboot >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] 'fastboot' was not found in your system PATH.
    pause
    exit /b 1
)

if not exist "%~dp0halium-boot.img" (
    echo [ERROR] halium-boot.img was not found!
    pause
    exit /b 1
)

echo [*] Flashing boot partition with halium-boot.img...
fastboot flash boot "%~dp0halium-boot.img"

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Flashing boot failed.
    pause
    exit /b 1
)

echo.
echo [*] Rebooting tablet into Halium 9.0...
fastboot reboot

echo.
echo ================================================================
echo [SUCCESS] Halium 9.0 boot partition flashed successfully!
echo ================================================================
pause
