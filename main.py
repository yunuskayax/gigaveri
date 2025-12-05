"""
ADB Telefon Veri Alma Uygulaması
Ana uygulama dosyası
"""
import os
import sys
import json
from datetime import datetime
from adb_manager import ADBManager
from installer import AutoInstaller

# Windows konsolu için UTF-8 encoding ayarla
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass


def print_separator():
    """Ekrana ayırıcı çizgi yazdırır"""
    print("=" * 60)


def print_menu():
    """Ana menüyü gösterir"""
    print_separator()
    print("ADB Telefon Veri Alma Uygulaması")
    print_separator()
    print("1. Bağlı cihazları listele")
    print("2. Cihaz bilgilerini göster")
    print("3. Yüklü uygulamaları listele")
    print("4. Uygulama bilgilerini göster")
    print("5. Dosya/Dizin çek (pull)")
    print("6. Dosya listesi göster")
    print("7. Logcat al ve kaydet")
    print("8. Shell komutu çalıştır")
    print("9. Telefon yedeklemesi oluştur (ADB Backup)")
    print("10. Yedekleme geri yükle (ADB Restore)")
    print("11. Çıkış")
    print_separator()


def save_json(data: dict, filename: str):
    """Veriyi JSON dosyasına kaydeder"""
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"[OK] Veri kaydedildi: {filename}")
        return True
    except Exception as e:
        print(f"[HATA] Kaydetme hatası: {str(e)}")
        return False


def main():
    """Ana uygulama fonksiyonu"""
    print("ADB Manager başlatılıyor...")
    
    # Otomatik kurulum kontrolü
    installer = AutoInstaller()
    is_installed, adb_location = installer.check_adb()
    
    if not is_installed:
        print("\n[UYARI] ADB bulunamadı!")
        response = input("Otomatik kurulum yapılsın mı? (E/h): ").strip().lower()
        
        if response in ['e', 'evet', 'y', 'yes', '']:
            print("\nOtomatik kurulum başlatılıyor...")
            installer.setup_all()
            # Kurulumdan sonra tekrar kontrol et
            is_installed, adb_location = installer.check_adb()
            if not is_installed:
                print("\n[HATA] ADB kurulumu başarısız!")
                print("[BILGI] Lütfen manuel olarak kurun: ADB_KURULUM.md dosyasına bakın")
                return
        else:
            print("\n[HATA] ADB bulunamadı! Lütfen manuel olarak kurun.")
            print("[BILGI] Detaylar için ADB_KURULUM.md dosyasına bakın")
            return
    
    # ADB Manager'ı başlat
    try:
        # Eğer proje klasöründeki ADB kullanılıyorsa, yolunu belirt
        if adb_location and adb_location != "system":
            adb = ADBManager(adb_path=adb_location)
        else:
            adb = ADBManager()
    except Exception as e:
        print(f"[HATA] Hata: {str(e)}")
        return
    
    # Çıktı klasörü oluştur
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    
    selected_device = None
    
    # Otomatik cihaz kontrolü ve bağlantı
    print("\n[OTOMATIK] Cihaz kontrolü yapılıyor...")
    devices = adb.get_devices()
    
    if devices:
        # Sadece 'device' durumundaki cihazları filtrele (unauthorized değil)
        available_devices = [d for d in devices if d['status'] == 'device']
        
        if available_devices:
            # İlk uygun cihazı otomatik seç
            selected_device = available_devices[0]['serial']
            print(f"[OK] Cihaz otomatik olarak bağlandı: {selected_device}")
            
            # Cihaz bilgilerini göster
            device_info = adb.get_device_info(selected_device)
            if device_info:
                model = device_info.get('ro.product.model', 'Bilinmiyor')
                brand = device_info.get('ro.product.brand', 'Bilinmiyor')
                android_version = device_info.get('ro.build.version.release', 'Bilinmiyor')
                print(f"[BILGI] Model: {brand} {model}")
                print(f"[BILGI] Android: {android_version}")
            
            print("[OK] Hazır! Menüden işlem seçebilirsiniz.\n")
        else:
            print("[UYARI] Cihaz bulundu ancak yetkilendirilmemiş!")
            print("[BILGI] Telefonunuzda 'USB hata ayıklamaya izin ver' bildirimini onaylayın.")
            print("[BILGI] Menüden '1' seçerek tekrar deneyebilirsiniz.\n")
    else:
        print("[UYARI] Hiçbir cihaz bulunamadı!")
        print("[BILGI] Lütfen:")
        print("   1. Telefonunuzu USB ile bağlayın")
        print("   2. USB hata ayıklama modunun açık olduğundan emin olun")
        print("   3. Telefonda 'USB hata ayıklamaya izin ver' bildirimini onaylayın")
        print("[BILGI] Menüden '1' seçerek cihazları tekrar kontrol edebilirsiniz.\n")
    
    while True:
        print_menu()
        choice = input("Seçiminiz (1-11): ").strip()
        
        if choice == "1":
            print("\nBağlı cihazlar kontrol ediliyor...")
            devices = adb.get_devices()
            
            if not devices:
                print("[HATA] Hiçbir cihaz bulunamadı!")
                print("[BILGI] Lütfen telefonunuzun USB hata ayıklama modunun açık olduğundan emin olun.")
                selected_device = None
            else:
                print(f"\n[OK] {len(devices)} cihaz bulundu:\n")
                for i, device in enumerate(devices, 1):
                    status_icon = "✓" if device['status'] == 'device' else "⚠"
                    print(f"{i}. {status_icon} Seri: {device['serial']}")
                    print(f"   Durum: {device['status']}")
                    if device['details']:
                        print(f"   Detay: {device['details']}")
                    print()
                
                # Sadece 'device' durumundaki cihazları filtrele
                available_devices = [d for d in devices if d['status'] == 'device']
                
                if not available_devices:
                    print("[UYARI] Hiçbir cihaz yetkilendirilmemiş!")
                    print("[BILGI] Telefonunuzda 'USB hata ayıklamaya izin ver' bildirimini onaylayın.")
                    selected_device = None
                elif len(available_devices) == 1:
                    selected_device = available_devices[0]['serial']
                    print(f"[OK] Cihaz otomatik seçildi: {selected_device}")
                elif len(available_devices) > 1:
                    try:
                        device_choice = input(
                            f"Cihaz seçin (1-{len(available_devices)}, Enter=ilk cihaz): "
                        ).strip()
                        if device_choice:
                            idx = int(device_choice) - 1
                            if 0 <= idx < len(available_devices):
                                selected_device = available_devices[idx]['serial']
                                print(f"[OK] Seçilen cihaz: {selected_device}")
                            else:
                                print("[HATA] Geçersiz seçim!")
                                selected_device = None
                        else:
                            selected_device = available_devices[0]['serial']
                            print(f"[OK] İlk cihaz seçildi: {selected_device}")
                    except ValueError:
                        print("[HATA] Geçersiz giriş!")
                        selected_device = None
                
                # İlk cihazı varsayılan olarak seç
                if len(devices) == 1:
                    selected_device = devices[0]['serial']
                    print(f"[OK] Cihaz otomatik seçildi: {selected_device}")
                elif len(devices) > 1:
                    try:
                        device_choice = input(
                            f"Cihaz seçin (1-{len(devices)}, Enter=ilk cihaz): "
                        ).strip()
                        if device_choice:
                            idx = int(device_choice) - 1
                            if 0 <= idx < len(devices):
                                selected_device = devices[idx]['serial']
                                print(f"[OK] Seçilen cihaz: {selected_device}")
                            else:
                                print("[HATA] Geçersiz seçim!")
                        else:
                            selected_device = devices[0]['serial']
                            print(f"[OK] İlk cihaz seçildi: {selected_device}")
                    except ValueError:
                        print("[HATA] Geçersiz giriş!")
        
        elif choice == "2":
            if not selected_device:
                print("[HATA] Önce bir cihaz seçin! (Seçenek 1)")
                print("[BILGI] Menüden '1' seçerek cihazları kontrol edin.")
                continue
            
            print(f"\nCihaz bilgileri alınıyor ({selected_device})...")
            device_info = adb.get_device_info(selected_device)
            
            if device_info:
                print("\n[OK] Cihaz Bilgileri:")
                print("-" * 40)
                for key, value in device_info.items():
                    print(f"{key}: {value}")
                
                # JSON'a kaydet
                filename = os.path.join(
                    output_dir,
                    f"device_info_{selected_device}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                )
                save_json(device_info, filename)
            else:
                print("[HATA] Cihaz bilgileri alınamadı!")
        
        elif choice == "3":
            if not selected_device:
                print("[HATA] Önce bir cihaz seçin! (Seçenek 1)")
                print("[BILGI] Menüden '1' seçerek cihazları kontrol edin.")
                continue
            
            print(f"\nYüklü uygulamalar alınıyor ({selected_device})...")
            apps = adb.get_installed_apps(selected_device)
            
            if apps:
                print(f"\n[OK] {len(apps)} uygulama bulundu:\n")
                for i, app in enumerate(apps[:50], 1):  # İlk 50'yi göster
                    print(f"{i}. {app}")
                
                if len(apps) > 50:
                    print(f"\n... ve {len(apps) - 50} uygulama daha")
                
                # JSON'a kaydet
                filename = os.path.join(
                    output_dir,
                    f"installed_apps_{selected_device}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                )
                save_json({"apps": apps, "count": len(apps)}, filename)
            else:
                print("[HATA] Uygulama listesi alınamadı!")
        
        elif choice == "4":
            if not selected_device:
                print("[HATA] Önce bir cihaz seçin! (Seçenek 1)")
                print("[BILGI] Menüden '1' seçerek cihazları kontrol edin.")
                continue
            
            package_name = input("Uygulama paket adını girin: ").strip()
            if not package_name:
                print("[HATA] Paket adı boş olamaz!")
                continue
            
            print(f"\nUygulama bilgileri alınıyor ({package_name})...")
            app_info = adb.get_app_info(package_name, selected_device)
            
            if app_info:
                print("\n[OK] Uygulama Bilgileri:")
                print("-" * 40)
                for key, value in app_info.items():
                    print(f"{key}: {value}")
                
                # JSON'a kaydet
                filename = os.path.join(
                    output_dir,
                    f"app_info_{package_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                )
                save_json(app_info, filename)
            else:
                print("[HATA] Uygulama bilgileri alınamadı!")
        
        elif choice == "5":
            if not selected_device:
                print("[HATA] Önce bir cihaz seçin! (Seçenek 1)")
                print("[BILGI] Menüden '1' seçerek cihazları kontrol edin.")
                continue
            
            remote_path = input("Telefondaki dosya/dizin yolu: ").strip()
            if not remote_path:
                print("[HATA] Yol boş olamaz!")
                continue
            
            local_path = input(
                f"Kaydedilecek yerel yol (Enter=output/{os.path.basename(remote_path)}): "
            ).strip()
            
            if not local_path:
                local_path = os.path.join(output_dir, os.path.basename(remote_path))
            
            print(f"\nDosya çekiliyor...")
            print(f"Kaynak: {remote_path}")
            print(f"Hedef: {local_path}")
            
            result = adb.pull_file(remote_path, local_path, selected_device)
            
            if result["success"]:
                print(f"[OK] {result.get('message', 'Dosya başarıyla çekildi')}")
                if "file_size" in result:
                    print(f"  Dosya boyutu: {result['file_size']} bytes")
            else:
                print(f"[HATA] Hata: {result.get('stderr', 'Bilinmeyen hata')}")
        
        elif choice == "6":
            if not selected_device:
                print("[HATA] Önce bir cihaz seçin! (Seçenek 1)")
                print("[BILGI] Menüden '1' seçerek cihazları kontrol edin.")
                continue
            
            remote_path = input(
                "Listelenecek dizin yolu (Enter=/sdcard): "
            ).strip() or "/sdcard"
            
            print(f"\nDosyalar listeleniyor ({remote_path})...")
            files = adb.list_files(remote_path, selected_device)
            
            if files:
                print(f"\n[OK] {len(files)} öğe bulundu:\n")
                for file in files[:30]:  # İlk 30'u göster
                    print(file)
                
                if len(files) > 30:
                    print(f"\n... ve {len(files) - 30} öğe daha")
            else:
                print("[HATA] Dosya listesi alınamadı veya dizin boş!")
        
        elif choice == "7":
            if not selected_device:
                print("[HATA] Önce bir cihaz seçin! (Seçenek 1)")
                print("[BILGI] Menüden '1' seçerek cihazları kontrol edin.")
                continue
            
            lines = input("Alınacak satır sayısı (Enter=1000): ").strip()
            lines = int(lines) if lines.isdigit() else 1000
            
            print(f"\nLogcat alınıyor ({lines} satır)...")
            filename = os.path.join(
                output_dir,
                f"logcat_{selected_device}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            )
            
            success = adb.save_logcat(filename, lines, selected_device)
            
            if success:
                file_size = os.path.getsize(filename)
                print(f"[OK] Logcat kaydedildi: {filename}")
                print(f"  Dosya boyutu: {file_size} bytes")
            else:
                print("[HATA] Logcat kaydedilemedi!")
        
        elif choice == "8":
            if not selected_device:
                print("[HATA] Önce bir cihaz seçin! (Seçenek 1)")
                print("[BILGI] Menüden '1' seçerek cihazları kontrol edin.")
                continue
            
            command = input("Shell komutu: ").strip()
            if not command:
                print("[HATA] Komut boş olamaz!")
                continue
            
            print(f"\nKomut çalıştırılıyor: {command}")
            result = adb.execute_shell_command(command, selected_device)
            
            if result["success"]:
                print("\n[OK] Komut çıktısı:")
                print("-" * 40)
                print(result["stdout"])
            else:
                print(f"\n[HATA] Hata: {result.get('stderr', 'Bilinmeyen hata')}")
        
        elif choice == "9":
            if not selected_device:
                print("[HATA] Önce bir cihaz seçin! (Seçenek 1)")
                print("[BILGI] Menüden '1' seçerek cihazları kontrol edin.")
                continue
            
            print("\n=== ADB Yedekleme Oluşturma ===")
            print("[BILGI] Yedekleme seçenekleri:")
            print("1. Tam yedekleme (Tüm uygulamalar + APK + Paylaşılan depolama)")
            print("2. Sadece uygulamalar (APK dahil)")
            print("3. Sadece uygulamalar (APK hariç)")
            print("4. Paylaşılan depolama (/sdcard)")
            print("5. Özel yedekleme (seçenekleri belirleyin)")
            
            backup_choice = input("\nSeçiminiz (1-5): ").strip()
            
            include_apk = True
            include_shared = True
            include_system = False
            include_all = True
            
            if backup_choice == "1":
                include_apk = True
                include_shared = True
                include_system = False
                include_all = True
            elif backup_choice == "2":
                include_apk = True
                include_shared = False
                include_system = False
                include_all = True
            elif backup_choice == "3":
                include_apk = False
                include_shared = False
                include_system = False
                include_all = True
            elif backup_choice == "4":
                include_apk = False
                include_shared = True
                include_system = False
                include_all = False
            elif backup_choice == "5":
                print("\nÖzel seçenekler:")
                apk_choice = input("APK dosyalarını dahil et? (E/h): ").strip().lower()
                include_apk = apk_choice in ['e', 'evet', 'y', 'yes', '']
                
                shared_choice = input("Paylaşılan depolamayı dahil et? (E/h): ").strip().lower()
                include_shared = shared_choice in ['e', 'evet', 'y', 'yes', '']
                
                system_choice = input("Sistem uygulamalarını dahil et? (E/h): ").strip().lower()
                include_system = system_choice in ['e', 'evet', 'y', 'yes']
                
                all_choice = input("Tüm uygulamaları dahil et? (E/h): ").strip().lower()
                include_all = all_choice in ['e', 'evet', 'y', 'yes', '']
            else:
                print("[HATA] Geçersiz seçim!")
                input("\nDevam etmek için Enter'a basın...")
                continue
            
            backup_filename = input(
                f"\nYedek dosyası adı (Enter=backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.ab): "
            ).strip()
            
            if not backup_filename:
                backup_filename = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.ab"
            
            if not backup_filename.endswith('.ab'):
                backup_filename += '.ab'
            
            backup_path = os.path.join(output_dir, backup_filename)
            
            print(f"\n[KURULUM] Yedekleme başlatılıyor...")
            print(f"[BILGI] Dosya: {backup_path}")
            print(f"[BILGI] APK: {'Evet' if include_apk else 'Hayır'}")
            print(f"[BILGI] Paylaşılan depolama: {'Evet' if include_shared else 'Hayır'}")
            print(f"[BILGI] Sistem uygulamaları: {'Evet' if include_system else 'Hayır'}")
            print(f"[BILGI] Tüm uygulamalar: {'Evet' if include_all else 'Hayır'}")
            
            result = adb.create_backup(
                backup_path,
                include_apk=include_apk,
                include_shared=include_shared,
                include_system=include_system,
                include_all=include_all,
                device_serial=selected_device
            )
            
            if result["success"]:
                print(f"\n[OK] {result.get('message', 'Yedekleme tamamlandı')}")
                if "file_size" in result:
                    size_mb = result["file_size"] / (1024 * 1024)
                    print(f"[OK] Dosya boyutu: {result['file_size']} bytes ({size_mb:.2f} MB)")
                print(f"[OK] Yedek dosyası: {backup_path}")
            else:
                print(f"\n[HATA] {result.get('message', 'Yedekleme başarısız')}")
                if result.get('stderr'):
                    print(f"[HATA] Detay: {result['stderr']}")
        
        elif choice == "10":
            if not selected_device:
                print("[HATA] Önce bir cihaz seçin! (Seçenek 1)")
                print("[BILGI] Menüden '1' seçerek cihazları kontrol edin.")
                continue
            
            print("\n=== ADB Yedekleme Geri Yükleme ===")
            print("[UYARI] Bu işlem telefon verilerini değiştirebilir!")
            print("[UYARI] Mevcut veriler silinebilir!")
            
            confirm = input("\nDevam etmek istediğinizden emin misiniz? (EVET yazın): ").strip()
            if confirm != "EVET":
                print("[BILGI] İşlem iptal edildi")
                input("\nDevam etmek için Enter'a basın...")
                continue
            
            # Yedek dosyalarını listele
            backup_files = []
            if os.path.exists(output_dir):
                for file in os.listdir(output_dir):
                    if file.endswith('.ab'):
                        backup_files.append(file)
            
            if not backup_files:
                print("\n[HATA] Yedek dosyası bulunamadı!")
                backup_path = input("Yedek dosyasının tam yolunu girin: ").strip()
            else:
                print(f"\nMevcut yedek dosyaları:")
                for i, file in enumerate(backup_files, 1):
                    file_path = os.path.join(output_dir, file)
                    file_size = os.path.getsize(file_path) / (1024 * 1024)
                    print(f"{i}. {file} ({file_size:.2f} MB)")
                
                file_choice = input("\nYedek dosyası seçin (numara veya tam yol): ").strip()
                
                if file_choice.isdigit():
                    idx = int(file_choice) - 1
                    if 0 <= idx < len(backup_files):
                        backup_path = os.path.join(output_dir, backup_files[idx])
                    else:
                        print("[HATA] Geçersiz seçim!")
                        input("\nDevam etmek için Enter'a basın...")
                        continue
                else:
                    backup_path = file_choice
            
            if not os.path.exists(backup_path):
                print(f"[HATA] Dosya bulunamadı: {backup_path}")
                input("\nDevam etmek için Enter'a basın...")
                continue
            
            print(f"\n[KURULUM] Geri yükleme başlatılıyor...")
            print(f"[BILGI] Dosya: {backup_path}")
            
            result = adb.restore_backup(backup_path, selected_device)
            
            if result["success"]:
                print(f"\n[OK] {result.get('message', 'Geri yükleme tamamlandı')}")
            else:
                print(f"\n[HATA] {result.get('message', 'Geri yükleme başarısız')}")
                if result.get('stderr'):
                    print(f"[HATA] Detay: {result['stderr']}")
        
        elif choice == "11":
            print("\nÇıkılıyor...")
            break
        
        else:
            print("\n[HATA] Geçersiz seçim! Lütfen 1-11 arası bir sayı girin.")
        
        input("\nDevam etmek için Enter'a basın...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nProgram kullanıcı tarafından sonlandırıldı.")
    except Exception as e:
        print(f"\n[HATA] Beklenmeyen hata: {str(e)}")

