@echo off
setlocal enabledelayedexpansion
title Lenovo Tab M7 (TB-7305X) - Emergency Boot Restore (MTKClient)
color 0b

echo ============================================================
echo   Lenovo Tab M7 (TB-7305X) - Direct BROM / Preloader Flash
echo ============================================================
echo.
echo [*] Terminating any hung SP Flash Tool instances...
taskkill /f /im flash_tool.exe >nul 2>&1

set "SCRIPT_DIR=%~dp0"
set "MTK_DIR=%SCRIPT_DIR%firmware\tools\mtkclient"
set "BOOT_IMG=%SCRIPT_DIR%releases\LineageOS-16.0-TB-7305X\boot.img"
set "PRELOADER=%SCRIPT_DIR%firmware\extracted\preloader_mt8765_P.bin"

if not exist "%BOOT_IMG%" (
    echo [ERROR] boot.img not found at: %BOOT_IMG%
    pause
    exit /b 1
)

echo [*] Target Boot Image : %BOOT_IMG%
echo [*] Target Preloader  : %PRELOADER%
echo.
echo ============================================================
echo INSTRUCTIONS TO CONNECT TABLET:
echo 1. Disconnect the USB cable from the tablet.
echo 2. Press and HOLD [Volume Up] + [Volume Down] together.
echo 3. While holding both buttons, PLUG IN THE USB CABLE to PC.
echo    (Or if tablet is already plugged in, hold [Power] for 15s)
echo ============================================================
echo.
echo [*] Starting MTK Direct Writer (bypassing SLA/DAA security)...
cd /d "%MTK_DIR%"
python mtk.py w boot "%BOOT_IMG%" --preloader "%PRELOADER%"

if %ERRORLEVEL% equ 0 (
    echo.
    echo ============================================================
    echo [SUCCESS] LineageOS 16.0 boot.img flashed successfully!
    echo [*] Rebooting tablet into system...
    echo ============================================================
    python mtk.py reset
) else (
    echo.
    echo [!] Flash did not complete. If it timed out, run this bat again and reconnect.
)

echo.
pause
