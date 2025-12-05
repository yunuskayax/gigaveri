"""
WhatsApp Kontrol Scripti
WhatsApp'ın yüklü olup olmadığını ve konumunu kontrol eder
"""
import sys
from adb_manager import ADBManager
from installer import AutoInstaller

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

print("=" * 60)
print("WhatsApp Kontrol")
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
print(f"[OK] Cihaz: {selected_device}\n")

# WhatsApp paketini kontrol et
print("[KONTROL] WhatsApp yüklü mü kontrol ediliyor...")
apps = adb.get_installed_apps(selected_device)
whatsapp_packages = [app for app in apps if 'whatsapp' in app.lower()]

if whatsapp_packages:
    print(f"[OK] WhatsApp bulundu: {', '.join(whatsapp_packages)}")
    
    # WhatsApp veri klasörünü kontrol et
    print("\n[KONTROL] WhatsApp veri klasörleri kontrol ediliyor...")
    
    # Farklı olası konumlar
    possible_paths = [
        "/sdcard/WhatsApp",
        "/storage/emulated/0/WhatsApp",
        "/sdcard/Android/media/com.whatsapp",
        "/storage/emulated/0/Android/media/com.whatsapp"
    ]
    
    found_paths = []
    for path in possible_paths:
        result = adb.execute_shell_command(f"test -d {path} && echo 'exists' || echo 'not found'", selected_device)
        if result["success"] and "exists" in result["stdout"]:
            found_paths.append(path)
            print(f"[OK] Bulundu: {path}")
            
            # İçeriği listele
            list_result = adb.execute_shell_command(f"ls {path}", selected_device)
            if list_result["success"]:
                print(f"   İçerik: {list_result['stdout'].strip()[:100]}")
    
    if not found_paths:
        print("[UYARI] WhatsApp klasörleri bulunamadı!")
        print("[BILGI] WhatsApp'ı açıp birkaç mesaj gönderin, böylece klasörler oluşur.")
    else:
        print(f"\n[OK] {len(found_paths)} WhatsApp klasörü bulundu!")
        print("[BILGI] Ana uygulamada '11' seçerek yedekleme yapabilirsiniz.")
else:
    print("[HATA] WhatsApp yüklü görünmüyor!")
    print("[BILGI] Lütfen WhatsApp'ı yükleyin ve tekrar deneyin.")

print("\n" + "=" * 60)

