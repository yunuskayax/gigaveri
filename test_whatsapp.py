"""
WhatsApp Yedekleme Test Scripti
WhatsApp klasörlerini ve dosyalarını kontrol eder
"""
import sys
from adb_manager import ADBManager
from installer import AutoInstaller

# Windows konsolu için UTF-8 encoding
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

print("=" * 60)
print("WhatsApp Yedekleme Test")
print("=" * 60)

# ADB kontrolü
installer = AutoInstaller()
is_installed, adb_location = installer.check_adb()

if not is_installed:
    print("[HATA] ADB bulunamadı!")
    sys.exit(1)

# ADB Manager'ı başlat
if adb_location and adb_location != "system":
    adb = ADBManager(adb_path=adb_location)
else:
    adb = ADBManager()

# Cihaz kontrolü
print("\n[TEST] Cihazlar kontrol ediliyor...")
devices = adb.get_devices()

if not devices:
    print("[HATA] Hiçbir cihaz bulunamadı!")
    sys.exit(1)

available_devices = [d for d in devices if d['status'] == 'device']
if not available_devices:
    print("[HATA] Hiçbir cihaz yetkilendirilmemiş!")
    sys.exit(1)

selected_device = available_devices[0]['serial']
print(f"[OK] Cihaz seçildi: {selected_device}")

# WhatsApp klasörlerini kontrol et
print("\n[TEST] WhatsApp klasörleri kontrol ediliyor...")
whatsapp_paths = adb.find_whatsapp_paths(selected_device)

print("\n[SONUÇ] WhatsApp Klasör Durumu:")
print("-" * 60)

# SDCard klasörlerini kontrol et
sdcard_paths = {
    "Veritabanları": whatsapp_paths["databases_sdcard"],
    "Medya": whatsapp_paths["media"],
    "Yedekler": whatsapp_paths["backups"]
}

for name, path in sdcard_paths.items():
    result = adb.execute_shell_command(f"test -d {path} && echo 'exists' || echo 'not found'", selected_device)
    if result["success"] and "exists" in result["stdout"]:
        # Dosya sayısını say
        count_result = adb.execute_shell_command(f"find {path} -type f 2>/dev/null | wc -l", selected_device)
        file_count = count_result["stdout"].strip() if count_result["success"] else "?"
        print(f"[OK] {name}: {path} ({file_count} dosya)")
    else:
        print(f"[HATA] {name}: {path} (bulunamadı)")

# Veritabanı dosyalarını listele
print("\n[TEST] WhatsApp Veritabanı Dosyaları:")
print("-" * 60)
db_result = adb.execute_shell_command(f"ls -lh {whatsapp_paths['databases_sdcard']} 2>/dev/null | grep -E '\\.db'", selected_device)
if db_result["success"] and db_result["stdout"].strip():
    print(db_result["stdout"])
else:
    print("[BILGI] Veritabanı dosyası bulunamadı (normal olabilir)")

# Medya klasörlerini kontrol et
print("\n[TEST] WhatsApp Medya Klasörleri:")
print("-" * 60)
media_folders = ["WhatsApp Images", "WhatsApp Video", "WhatsApp Audio", "WhatsApp Documents"]
for folder in media_folders:
    path = f"{whatsapp_paths['media']}/{folder}"
    result = adb.execute_shell_command(f"test -d {path} && echo 'exists' || echo 'not found'", selected_device)
    if result["success"] and "exists" in result["stdout"]:
        count_result = adb.execute_shell_command(f"find {path} -type f 2>/dev/null | wc -l", selected_device)
        file_count = count_result["stdout"].strip() if count_result["success"] else "?"
        print(f"[OK] {folder}: {file_count} dosya")
    else:
        print(f"[HATA] {folder}: Bulunamadı")

print("\n" + "=" * 60)
print("[TEST] Test tamamlandı!")
print("=" * 60)
print("\n[BILGI] Ana uygulamada '11' seçerek WhatsApp yedeklemesi yapabilirsiniz.")

