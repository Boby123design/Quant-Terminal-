@echo off
title RENAISSANCE QUANT TERMINAL
color 0C

echo ===================================================
echo   🚨 INITIALIZING SYSTEM CLEANUP (ANTI-GHOST) 🚨
echo ===================================================
echo.
echo [*] Destroying all previous background bot instances...

:: Ye commands system mein chhipe hue purane terminals ko force-kill karegi
taskkill /F /FI "WINDOWTITLE eq HFT Backend*" >nul 2>&1
taskkill /F /FI "WINDOWTITLE eq HFT Dashboard*" >nul 2>&1

:: Delete old locks and files
if exist bot_running.lock del bot_running.lock
if exist kill_switch.txt del kill_switch.txt
if exist live_status.csv del live_status.csv

echo [*] Cleanup 100%% Complete. Environment is pure.
echo.

color 0A
echo ===================================================
echo       🚀 LAUNCHING MODEL 18 SECURE ENGINE 🚀
echo ===================================================

echo.
echo [1] Starting AI Backend Engine...
start "HFT Backend Engine" cmd /k "python auto_executor.py"

echo.
echo ⏳ Waiting 3 seconds for MT5 handshake...
timeout /t 3 /nobreak > NUL

echo.
echo [2] Starting Command Center Dashboard...
start "HFT Dashboard" cmd /k "python -m streamlit run hft_dashboard.py"

echo.
echo ✅ ALL SYSTEMS ONLINE!
echo.
pause