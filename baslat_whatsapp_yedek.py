"""
WhatsApp Yedekleme Hızlı Başlatıcı
"""
import sys
import os
from datetime import datetime
from adb_manager import ADBManager
from installer import AutoInstaller

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

print("=" * 60)
print("WhatsApp Yedekleme - Hızlı Başlatıcı")
print("=" * 60)

# ADB ve cihaz kontrolü
installer = AutoInstaller()
is_installed, adb_location = installer.check_adb()

if not is_installed:
    print("[HATA] ADB bulunamadı!")
    sys.exit(1)

if adb_location and adb_location != "system":
    adb = ADBManager(adb_path=adb_location)
else:
    adb = ADBManager()

devices = adb.get_devices()
available_devices = [d for d in devices if d['status'] == 'device']
if not available_devices:
    print("[HATA] Cihaz bulunamadı!")
    sys.exit(1)

selected_device = available_devices[0]['serial']
print(f"[OK] Cihaz: {selected_device}")

# WhatsApp kontrolü
print("\n[KONTROL] WhatsApp kontrol ediliyor...")
whatsapp_paths = adb.find_whatsapp_paths(selected_device)

if not whatsapp_paths.get("databases_sdcard") and not whatsapp_paths.get("media"):
    print("[UYARI] WhatsApp klasörleri bulunamadı!")
    print("[BILGI] WhatsApp'ı açıp birkaç mesaj gönderin, böylece klasörler oluşur.")
    sys.exit(1)

print("[OK] WhatsApp klasörleri bulundu!")

# Çıktı klasörü
output_dir = "output"
os.makedirs(output_dir, exist_ok=True)

print("\n" + "=" * 60)
print("WhatsApp Yedekleme Başlatılıyor...")
print("=" * 60)
print("\n[BILGI] Tam yedekleme yapılıyor (Veritabanları + Medya)")
print("[BILGI] Bu işlem birkaç dakika sürebilir...\n")

result = adb.backup_whatsapp_complete(
    output_dir,
    include_databases=True,
    include_media=True,
    device_serial=selected_device
)

if result["success"]:
    print("\n" + "=" * 60)
    print("[OK] WhatsApp yedeklemesi tamamlandı!")
    print("=" * 60)
    
    if result.get("databases"):
        print(f"\n[OK] Veritabanları: {result['databases']['output_dir']}")
        print(f"[OK] İndirilen dosya sayısı: {len(result['databases']['downloaded_files'])}")
        if result['databases']['downloaded_files']:
            print("[OK] İndirilen dosyalar:")
            for file in result['databases']['downloaded_files']:
                print(f"  - {os.path.basename(file)}")
        if result['databases']['errors']:
            print(f"[UYARI] {len(result['databases']['errors'])} dosya indirilemedi")
    
    if result.get("media"):
        print(f"\n[OK] Medya dosyaları: {result['media']['output_dir']}")
        print(f"[OK] İndirilen dosya sayısı: {result['media']['downloaded_count']}")
        if result['media']['errors']:
            print(f"[UYARI] {len(result['media']['errors'])} klasör indirilemedi")
    
    backup_path = os.path.join(output_dir, "whatsapp_backup")
    print(f"\n[OK] Tüm yedekler: {backup_path}")
    print("[OK] Yedekleme başarıyla tamamlandı!")
else:
    print("\n[HATA] WhatsApp yedeklemesi başarısız!")
    print("[BILGI] WhatsApp klasörlerinin mevcut olduğundan emin olun.")
    if result.get("databases") and result["databases"]["errors"]:
        print("\n[HATA] Veritabanı hataları:")
        for error in result["databases"]["errors"]:
            print(f"  - {error}")

print("\n" + "=" * 60)
