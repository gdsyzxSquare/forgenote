@echo off
chcp 65001 >nul
echo ======================================================================
echo   ForgeNote Debug Server
echo ======================================================================
echo.
echo Starting all services...
echo.

python scripts\start_debug_server.py

pause
