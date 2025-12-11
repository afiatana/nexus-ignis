@echo off
title Nexus Ignis - Auto Deploy System
color 0a
echo ===================================================
echo   NEXUS IGNIS - AUTO DEPLOY TO GITHUB REPOSITORY
echo ===================================================
echo.
echo [1/3] Menyiapkan file...
git add .
echo.

:prompt
set /p "commit_msg=Masukkan catatan update (Tekan Enter untuk default): "
if "%commit_msg%"=="" set commit_msg="Auto update Nexus Ignis"

echo.
echo [2/3] Menyimpan snapshot versi...
git commit -m "%commit_msg%"
echo.

echo [3/3] Mengirim data ke Awan (GitHub)...
git push origin master
echo.

if %ERRORLEVEL% EQU 0 (
    echo [SUKSES] Proyek berhasil di-update di repository!
    echo Link Repository: https://github.com/afiatana/nexus-ignis
) else (
    echo [ERROR] Terjadi kesalahan saat pengiriman.
)
echo.
pause
