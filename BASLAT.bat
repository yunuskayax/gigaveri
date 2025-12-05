@echo off
chcp 65001 >nul
title ADB Telefon Veri Alma Uygulaması
color 0A

echo.
echo ============================================================
echo    ADB Telefon Veri Alma Uygulaması
echo ============================================================
echo.
echo [BILGI] Uygulama başlatılıyor...
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

REM Ana uygulamayı çalıştır
python main.py

REM Hata durumunda bekle
if errorlevel 1 (
    echo.
    echo [HATA] Uygulama bir hata ile sonlandı!
    pause
)

