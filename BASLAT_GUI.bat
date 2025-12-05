@echo off
chcp 65001 >nul
title ADB Telefon Veri Alma - GUI Başlatıcı
color 0A

echo.
echo ============================================================
echo    ADB Telefon Veri Alma - GUI Başlatıcı
echo ============================================================
echo.
echo [BILGI] GUI başlatılıyor...
echo.

REM Python'un yüklü olup olmadığını kontrol et
python --version >nul 2>&1
if errorlevel 1 (
    echo [HATA] Python bulunamadı!
    echo [BILGI] Lütfen Python'u yükleyin: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

REM GUI başlatıcıyı çalıştır
python baslat_gui.py

REM Hata durumunda bekle
if errorlevel 1 (
    echo.
    echo [HATA] GUI başlatılamadı!
    echo [BILGI] Konsol versiyonunu deneyin: BASLAT.bat
    pause
)

