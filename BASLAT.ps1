# PowerShell başlatıcı scripti
# UTF-8 encoding ayarla
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host "   ADB Telefon Veri Alma Uygulaması" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
Write-Host ""
Write-Host "[BILGI] Uygulama başlatılıyor..." -ForegroundColor Cyan
Write-Host ""

# Python'un yüklü olup olmadığını kontrol et
try {
    $pythonVersion = python --version 2>&1
    Write-Host "[OK] Python bulundu: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "[HATA] Python bulunamadı!" -ForegroundColor Red
    Write-Host "[BILGI] Lütfen Python'u yükleyin: https://www.python.org/downloads/" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Devam etmek için Enter'a basın"
    exit 1
}

# Ana uygulamayı çalıştır
try {
    python main.py
} catch {
    Write-Host ""
    Write-Host "[HATA] Uygulama bir hata ile sonlandı!" -ForegroundColor Red
    Write-Host "Hata: $_" -ForegroundColor Red
    Read-Host "Devam etmek için Enter'a basın"
}

