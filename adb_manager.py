"""
ADB Yönetim Modülü
Android Debug Bridge ile telefon verilerini almak için yardımcı fonksiyonlar
"""
import subprocess
import os
import json
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime


class ADBManager:
    """ADB komutlarını yöneten sınıf"""
    
    def __init__(self, adb_path: Optional[str] = None):
        """
        Args:
            adb_path: ADB komutunun yolu (None ise otomatik bulunur)
        """
        if adb_path is None:
            self.adb_path = self._find_adb()
        else:
            self.adb_path = adb_path
        self._check_adb_available()
    
    def _find_adb(self) -> str:
        """ADB'yi otomatik olarak bulur (önce proje klasörü, sonra sistem PATH)"""
        # Önce proje klasöründeki platform-tools'u kontrol et
        project_root = Path(__file__).parent
        local_adb = project_root / "platform-tools" / "adb.exe"
        
        if local_adb.exists():
            return str(local_adb)
        
        # Sistem PATH'inde kontrol et
        try:
            result = subprocess.run(
                ["adb", "version"],
                capture_output=True,
                text=True,
                timeout=2
            )
            if result.returncode == 0:
                return "adb"
        except:
            pass
        
        # Varsayılan olarak "adb" döndür (hata kontrolü _check_adb_available'da yapılacak)
        return "adb"
    
    def _check_adb_available(self) -> bool:
        """ADB'nin sistemde mevcut olup olmadığını kontrol eder"""
        try:
            result = subprocess.run(
                [self.adb_path, "version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                print(f"[OK] ADB bulundu: {result.stdout.split()[0]}")
                return True
            else:
                raise Exception("ADB komutu çalıştırılamadı")
        except FileNotFoundError:
            raise Exception(
                "ADB bulunamadı! Lütfen Android SDK Platform Tools'u yükleyin "
                "ve PATH'e ekleyin."
            )
        except Exception as e:
            raise Exception(f"ADB kontrolü başarısız: {str(e)}")
    
    def _run_command(self, command: List[str], timeout: int = 30) -> Dict:
        """
        ADB komutunu çalıştırır ve sonucu döndürür
        
        Args:
            command: Çalıştırılacak komut listesi
            timeout: Komut timeout süresi (saniye)
        
        Returns:
            Komut sonucu ve bilgileri içeren dict
        """
        try:
            result = subprocess.run(
                [self.adb_path] + command,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "stdout": "",
                "stderr": "Komut zaman aşımına uğradı",
                "returncode": -1
            }
        except Exception as e:
            return {
                "success": False,
                "stdout": "",
                "stderr": str(e),
                "returncode": -1
            }
    
    def get_devices(self) -> List[Dict]:
        """
        Bağlı Android cihazların listesini döndürür
        
        Returns:
            Cihaz bilgileri içeren liste
        """
        result = self._run_command(["devices", "-l"])
        devices = []
        
        if result["success"]:
            lines = result["stdout"].strip().split("\n")[1:]  # İlk satırı atla
            for line in lines:
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 2:
                        device_info = {
                            "serial": parts[0],
                            "status": parts[1],
                            "details": " ".join(parts[2:]) if len(parts) > 2 else ""
                        }
                        devices.append(device_info)
        
        return devices
    
    def get_device_info(self, device_serial: Optional[str] = None) -> Dict:
        """
        Cihaz bilgilerini alır
        
        Args:
            device_serial: Cihaz seri numarası (None ise ilk cihaz)
        
        Returns:
            Cihaz bilgileri
        """
        cmd = ["shell", "getprop"]
        if device_serial:
            cmd = ["-s", device_serial] + cmd
        
        result = self._run_command(cmd, timeout=60)
        
        info = {}
        if result["success"]:
            lines = result["stdout"].strip().split("\n")
            for line in lines:
                if ":" in line:
                    key, value = line.split(":", 1)
                    key = key.strip().strip("[]")
                    value = value.strip().strip("[]")
                    info[key] = value
        
        # Önemli bilgileri özel olarak al
        important_props = [
            "ro.product.model",
            "ro.product.brand",
            "ro.product.device",
            "ro.build.version.release",
            "ro.build.version.sdk",
            "ro.serialno"
        ]
        
        device_info = {}
        for prop in important_props:
            cmd = ["shell", "getprop", prop]
            if device_serial:
                cmd = ["-s", device_serial] + cmd
            prop_result = self._run_command(cmd)
            if prop_result["success"]:
                device_info[prop] = prop_result["stdout"].strip()
        
        return device_info
    
    def pull_file(self, remote_path: str, local_path: str, 
                  device_serial: Optional[str] = None) -> Dict:
        """
        Telefondan dosya çeker
        
        Args:
            remote_path: Telefondaki dosya yolu
            local_path: Kaydedilecek yerel yol
            device_serial: Cihaz seri numarası
        
        Returns:
            İşlem sonucu
        """
        cmd = ["pull", remote_path, local_path]
        if device_serial:
            cmd = ["-s", device_serial] + cmd
        
        result = self._run_command(cmd, timeout=300)
        
        if result["success"]:
            # Dosyanın başarıyla indirildiğini kontrol et
            if os.path.exists(local_path):
                file_size = os.path.getsize(local_path)
                result["file_size"] = file_size
                result["message"] = f"Dosya başarıyla indirildi: {file_size} bytes"
            else:
                result["success"] = False
                result["message"] = "Dosya indirildi ancak bulunamadı"
        
        return result
    
    def pull_directory(self, remote_path: str, local_path: str,
                      device_serial: Optional[str] = None) -> Dict:
        """
        Telefondan dizin çeker
        
        Args:
            remote_path: Telefondaki dizin yolu
            local_path: Kaydedilecek yerel yol
            device_serial: Cihaz seri numarası
        
        Returns:
            İşlem sonucu
        """
        return self.pull_file(remote_path, local_path, device_serial)
    
    def execute_shell_command(self, command: str,
                              device_serial: Optional[str] = None) -> Dict:
        """
        Shell komutu çalıştırır
        
        Args:
            command: Çalıştırılacak shell komutu
            device_serial: Cihaz seri numarası
        
        Returns:
            Komut çıktısı
        """
        cmd = ["shell", command]
        if device_serial:
            cmd = ["-s", device_serial] + cmd
        
        return self._run_command(cmd, timeout=60)
    
    def get_installed_apps(self, device_serial: Optional[str] = None) -> List[str]:
        """
        Yüklü uygulamaların listesini alır
        
        Args:
            device_serial: Cihaz seri numarası
        
        Returns:
            Uygulama paket isimleri listesi
        """
        result = self.execute_shell_command(
            "pm list packages",
            device_serial
        )
        
        apps = []
        if result["success"]:
            lines = result["stdout"].strip().split("\n")
            for line in lines:
                if line.startswith("package:"):
                    apps.append(line.replace("package:", "").strip())
        
        return apps
    
    def get_app_info(self, package_name: str,
                    device_serial: Optional[str] = None) -> Dict:
        """
        Uygulama bilgilerini alır
        
        Args:
            package_name: Uygulama paket adı
            device_serial: Cihaz seri numarası
        
        Returns:
            Uygulama bilgileri
        """
        # Uygulama bilgilerini al
        result = self.execute_shell_command(
            f"dumpsys package {package_name}",
            device_serial
        )
        
        info = {
            "package": package_name,
            "installed": result["success"]
        }
        
        if result["success"]:
            output = result["stdout"]
            # Version bilgisi
            if "versionName=" in output:
                try:
                    version_line = [l for l in output.split("\n") 
                                  if "versionName=" in l][0]
                    info["version"] = version_line.split("versionName=")[1].split()[0]
                except:
                    pass
            
            # UID bilgisi
            if "userId=" in output:
                try:
                    uid_line = [l for l in output.split("\n") 
                              if "userId=" in l][0]
                    info["uid"] = uid_line.split("userId=")[1].split()[0]
                except:
                    pass
        
        return info
    
    def get_logcat(self, lines: int = 100,
                  device_serial: Optional[str] = None) -> str:
        """
        Logcat çıktısını alır
        
        Args:
            lines: Alınacak satır sayısı
            device_serial: Cihaz seri numarası
        
        Returns:
            Logcat çıktısı
        """
        result = self.execute_shell_command(
            f"logcat -d -t {lines}",
            device_serial
        )
        
        return result["stdout"] if result["success"] else ""
    
    def save_logcat(self, output_file: str, lines: int = 1000,
                   device_serial: Optional[str] = None) -> bool:
        """
        Logcat'i dosyaya kaydeder
        
        Args:
            output_file: Kaydedilecek dosya yolu
            lines: Alınacak satır sayısı
            device_serial: Cihaz seri numarası
        
        Returns:
            Başarı durumu
        """
        logcat_output = self.get_logcat(lines, device_serial)
        
        try:
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(logcat_output)
            return True
        except Exception as e:
            print(f"Logcat kaydetme hatası: {str(e)}")
            return False
    
    def list_files(self, remote_path: str = "/sdcard",
                  device_serial: Optional[str] = None) -> List[str]:
        """
        Telefondaki dosya listesini alır
        
        Args:
            remote_path: Listelenecek dizin yolu
            device_serial: Cihaz seri numarası
        
        Returns:
            Dosya/dizin listesi
        """
        result = self.execute_shell_command(
            f"ls -la {remote_path}",
            device_serial
        )
        
        files = []
        if result["success"]:
            lines = result["stdout"].strip().split("\n")
            for line in lines:
                if line.strip():
                    files.append(line)
        
        return files
    
    def create_backup(self, output_file: str,
                     include_apk: bool = True,
                     include_shared: bool = True,
                     include_system: bool = False,
                     include_all: bool = True,
                     device_serial: Optional[str] = None) -> Dict:
        """
        Telefonun ADB yedeklemesini oluşturur
        
        Args:
            output_file: Yedek dosyasının kaydedileceği yol (.ab uzantılı)
            include_apk: APK dosyalarını dahil et
            include_shared: Paylaşılan depolamayı dahil et (/sdcard)
            include_system: Sistem uygulamalarını dahil et
            include_all: Tüm uygulamaları dahil et
            device_serial: Cihaz seri numarası
        
        Returns:
            İşlem sonucu
        
        Not: Telefon ekranında yedeklemeyi onaylamanız gerekecek!
        """
        # Yedek dosyası .ab uzantılı olmalı
        if not output_file.endswith('.ab'):
            output_file += '.ab'
        
        # Komut oluştur
        cmd = ["backup"]
        
        if include_all:
            cmd.append("-all")
        if include_apk:
            cmd.append("-apk")
        if include_shared:
            cmd.append("-shared")
        if include_system:
            cmd.append("-system")
        else:
            cmd.append("-nosystem")
        
        cmd.append("-f")
        cmd.append(output_file)
        
        if device_serial:
            cmd = ["-s", device_serial] + cmd
        
        print("\n[UYARI] Telefon ekranında yedeklemeyi onaylamanız gerekecek!")
        print("[BILGI] Telefonda 'Yedekleme başlat' butonuna basın")
        print("[BILGI] Şifre istenirse boş bırakabilirsiniz (şifresiz yedekleme)")
        print(f"[BILGI] Yedekleme başlatılıyor... Bu işlem birkaç dakika sürebilir.\n")
        
        # Backup komutu interaktif olduğu için özel işlem gerekiyor
        try:
            # Output dosyasının dizinini oluştur
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # ADB backup komutunu çalıştır
            # Bu komut telefon ekranında onay bekler
            process = subprocess.Popen(
                [self.adb_path] + cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE
            )
            
            # Kullanıcı telefon ekranında onaylayana kadar bekle
            # Timeout 5 dakika (yedekleme uzun sürebilir)
            try:
                stdout, stderr = process.communicate(timeout=300)
                returncode = process.returncode
            except subprocess.TimeoutExpired:
                process.kill()
                return {
                    "success": False,
                    "message": "Yedekleme zaman aşımına uğradı (5 dakika)",
                    "stderr": "Timeout"
                }
            
            # Dosyanın oluşup oluşmadığını kontrol et
            if os.path.exists(output_file):
                file_size = os.path.getsize(output_file)
                return {
                    "success": True,
                    "message": f"Yedekleme başarıyla oluşturuldu",
                    "file_size": file_size,
                    "file_path": output_file,
                    "stdout": stdout.decode('utf-8', errors='ignore') if stdout else "",
                    "stderr": stderr.decode('utf-8', errors='ignore') if stderr else ""
                }
            else:
                return {
                    "success": False,
                    "message": "Yedekleme dosyası oluşturulamadı",
                    "stderr": stderr.decode('utf-8', errors='ignore') if stderr else "Bilinmeyen hata"
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"Yedekleme hatası: {str(e)}",
                "stderr": str(e)
            }
    
    def restore_backup(self, backup_file: str,
                      device_serial: Optional[str] = None) -> Dict:
        """
        ADB yedeklemesini geri yükler
        
        Args:
            backup_file: Yedek dosyasının yolu (.ab uzantılı)
            device_serial: Cihaz seri numarası
        
        Returns:
            İşlem sonucu
        
        Not: Bu işlem telefon verilerini silebilir! Dikkatli kullanın!
        """
        if not os.path.exists(backup_file):
            return {
                "success": False,
                "message": f"Yedek dosyası bulunamadı: {backup_file}",
                "stderr": "File not found"
            }
        
        cmd = ["restore", backup_file]
        
        if device_serial:
            cmd = ["-s", device_serial] + cmd
        
        print("\n[UYARI] Bu işlem telefon verilerini değiştirebilir!")
        print("[UYARI] Mevcut veriler silinebilir!")
        print("[BILGI] Telefon ekranında geri yüklemeyi onaylamanız gerekecek")
        print(f"[BILGI] Yedek dosyası: {backup_file}")
        print("[BILGI] Geri yükleme başlatılıyor...\n")
        
        try:
            process = subprocess.Popen(
                [self.adb_path] + cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE
            )
            
            # Timeout 10 dakika (geri yükleme uzun sürebilir)
            try:
                stdout, stderr = process.communicate(timeout=600)
                returncode = process.returncode
            except subprocess.TimeoutExpired:
                process.kill()
                return {
                    "success": False,
                    "message": "Geri yükleme zaman aşımına uğradı (10 dakika)",
                    "stderr": "Timeout"
                }
            
            if returncode == 0:
                return {
                    "success": True,
                    "message": "Geri yükleme tamamlandı",
                    "stdout": stdout.decode('utf-8', errors='ignore') if stdout else "",
                    "stderr": stderr.decode('utf-8', errors='ignore') if stderr else ""
                }
            else:
                return {
                    "success": False,
                    "message": "Geri yükleme başarısız",
                    "stderr": stderr.decode('utf-8', errors='ignore') if stderr else "Bilinmeyen hata"
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"Geri yükleme hatası: {str(e)}",
                "stderr": str(e)
            }
    
    def find_whatsapp_paths(self, device_serial: Optional[str] = None) -> Dict:
        """
        WhatsApp klasörlerini ve dosyalarını bulur
        
        Args:
            device_serial: Cihaz seri numarası
        
        Returns:
            WhatsApp yolları ve dosyaları
        """
        paths = {
            "databases_sdcard": None,
            "media": None,
            "backups": None,
            "databases_app": "/data/data/com.whatsapp/databases",
            "found_files": []
        }
        
        # Olası WhatsApp konumları (Android versiyonlarına göre)
        possible_locations = [
            "/sdcard/WhatsApp",
            "/storage/emulated/0/WhatsApp",
            "/sdcard/Android/media/com.whatsapp/WhatsApp",
            "/storage/emulated/0/Android/media/com.whatsapp/WhatsApp"
        ]
        
        whatsapp_base = None
        for location in possible_locations:
            result = self.execute_shell_command(f"test -d {location} && echo 'exists'", device_serial)
            if result["success"] and "exists" in result["stdout"]:
                whatsapp_base = location
                break
        
        if whatsapp_base:
            # Klasik konumlar
            paths["databases_sdcard"] = f"{whatsapp_base}/Databases"
            paths["media"] = f"{whatsapp_base}/Media"
            paths["backups"] = f"{whatsapp_base}/Backups"
            
            # Klasörleri kontrol et ve dosyaları listele
            for key in ["databases_sdcard", "media", "backups"]:
                if paths[key]:
                    result = self.execute_shell_command(f"test -d {paths[key]} && echo 'exists'", device_serial)
                    if result["success"] and "exists" in result["stdout"]:
                        files_result = self.execute_shell_command(f"ls {paths[key]}", device_serial)
                        if files_result["success"]:
                            paths["found_files"].extend([f"{paths[key]}/{f}" for f in files_result["stdout"].strip().split("\n") if f.strip()])
        
        return paths
    
    def backup_whatsapp_databases(self, output_dir: str,
                                  device_serial: Optional[str] = None) -> Dict:
        """
        WhatsApp veritabanı dosyalarını yedekler
        
        Args:
            output_dir: Yedek dosyalarının kaydedileceği klasör
            device_serial: Cihaz seri numarası
        
        Returns:
            İşlem sonucu ve indirilen dosyalar
        """
        whatsapp_dir = os.path.join(output_dir, "whatsapp_backup")
        os.makedirs(whatsapp_dir, exist_ok=True)
        
        databases_dir = os.path.join(whatsapp_dir, "databases")
        os.makedirs(databases_dir, exist_ok=True)
        
        downloaded_files = []
        errors = []
        
        # WhatsApp klasörlerini bul
        whatsapp_paths = self.find_whatsapp_paths(device_serial)
        
        # SDCard'taki otomatik yedekleri çek
        sdcard_db_path = whatsapp_paths.get("databases_sdcard") or "/sdcard/WhatsApp/Databases"
        result = self.execute_shell_command(f"ls {sdcard_db_path} 2>/dev/null", device_serial)
        
        if result["success"] and result["stdout"].strip():
            files = [f.strip() for f in result["stdout"].strip().split("\n") if f.strip()]
            for file in files:
                if file.endswith(('.db', '.db.crypt12', '.db.crypt14', '.db.crypt15')):
                    remote_path = f"{sdcard_db_path}/{file}"
                    local_path = os.path.join(databases_dir, file)
                    
                    pull_result = self.pull_file(remote_path, local_path, device_serial)
                    if pull_result["success"]:
                        downloaded_files.append(local_path)
                    else:
                        errors.append(f"{file}: {pull_result.get('stderr', 'Bilinmeyen hata')}")
        
        # /data/data/com.whatsapp/databases/ klasöründen çekmeyi dene (root gerektirir)
        app_db_path = "/data/data/com.whatsapp/databases"
        result = self.execute_shell_command(f"su -c 'ls {app_db_path}' 2>/dev/null", device_serial)
        
        if result["success"] and result["stdout"].strip():
            files = [f.strip() for f in result["stdout"].strip().split("\n") if f.strip()]
            for file in files:
                if file.endswith('.db') and file not in [os.path.basename(f) for f in downloaded_files]:
                    remote_path = f"{app_db_path}/{file}"
                    local_path = os.path.join(databases_dir, f"root_{file}")
                    
                    # Root ile çek
                    pull_result = self.execute_shell_command(
                        f"su -c 'cat {remote_path}' > /sdcard/temp_{file}",
                        device_serial
                    )
                    
                    if pull_result["success"]:
                        temp_pull = self.pull_file(f"/sdcard/temp_{file}", local_path, device_serial)
                        if temp_pull["success"]:
                            downloaded_files.append(local_path)
                            # Geçici dosyayı sil
                            self.execute_shell_command(f"rm /sdcard/temp_{file}", device_serial)
        
        return {
            "success": len(downloaded_files) > 0,
            "downloaded_files": downloaded_files,
            "errors": errors,
            "output_dir": databases_dir
        }
    
    def backup_whatsapp_media(self, output_dir: str,
                              include_images: bool = True,
                              include_videos: bool = True,
                              include_audio: bool = True,
                              include_documents: bool = True,
                              device_serial: Optional[str] = None) -> Dict:
        """
        WhatsApp medya dosyalarını yedekler
        
        Args:
            output_dir: Yedek dosyalarının kaydedileceği klasör
            include_images: Resimleri dahil et
            include_videos: Videoları dahil et
            include_audio: Ses dosyalarını dahil et
            include_documents: Belgeleri dahil et
            device_serial: Cihaz seri numarası
        
        Returns:
            İşlem sonucu
        """
        whatsapp_dir = os.path.join(output_dir, "whatsapp_backup")
        os.makedirs(whatsapp_dir, exist_ok=True)
        
        media_dir = os.path.join(whatsapp_dir, "media")
        os.makedirs(media_dir, exist_ok=True)
        
        media_folders = []
        if include_images:
            media_folders.append(("WhatsApp Images", "Images"))
        if include_videos:
            media_folders.append(("WhatsApp Video", "Videos"))
        if include_audio:
            media_folders.append(("WhatsApp Audio", "Audio"))
        if include_documents:
            media_folders.append(("WhatsApp Documents", "Documents"))
        
        downloaded_count = 0
        errors = []
        
        # WhatsApp medya klasörünü bul
        whatsapp_paths = self.find_whatsapp_paths(device_serial)
        media_base = whatsapp_paths.get("media") or "/sdcard/WhatsApp/Media"
        
        for remote_folder, local_folder in media_folders:
            remote_path = f"{media_base}/{remote_folder}"
            local_path = os.path.join(media_dir, local_folder)
            
            # Klasörün varlığını kontrol et
            check_result = self.execute_shell_command(f"test -d {remote_path} && echo 'exists'", device_serial)
            if check_result["success"] and "exists" in check_result["stdout"]:
                pull_result = self.pull_directory(remote_path, local_path, device_serial)
                if pull_result["success"]:
                    # İndirilen dosya sayısını say
                    if os.path.exists(local_path):
                        file_count = sum([len(files) for _, _, files in os.walk(local_path)])
                        downloaded_count += file_count
                else:
                    errors.append(f"{remote_folder}: {pull_result.get('stderr', 'Bilinmeyen hata')}")
        
        return {
            "success": downloaded_count > 0,
            "downloaded_count": downloaded_count,
            "errors": errors,
            "output_dir": media_dir
        }
    
    def backup_whatsapp_complete(self, output_dir: str,
                                include_databases: bool = True,
                                include_media: bool = True,
                                device_serial: Optional[str] = None) -> Dict:
        """
        WhatsApp'ın tam yedeğini alır (veritabanları + medya)
        
        Args:
            output_dir: Yedek dosyalarının kaydedileceği klasör
            include_databases: Veritabanlarını dahil et
            include_media: Medya dosyalarını dahil et
            device_serial: Cihaz seri numarası
        
        Returns:
            İşlem sonucu
        """
        whatsapp_dir = os.path.join(output_dir, "whatsapp_backup")
        os.makedirs(whatsapp_dir, exist_ok=True)
        
        results = {
            "databases": None,
            "media": None,
            "success": False
        }
        
        if include_databases:
            print("\n[KURULUM] WhatsApp veritabanları yedekleniyor...")
            results["databases"] = self.backup_whatsapp_databases(output_dir, device_serial)
            if results["databases"]["success"]:
                print(f"[OK] {len(results['databases']['downloaded_files'])} veritabanı dosyası indirildi")
            else:
                print("[UYARI] Veritabanı dosyaları bulunamadı veya erişilemedi")
        
        if include_media:
            print("\n[KURULUM] WhatsApp medya dosyaları yedekleniyor...")
            results["media"] = self.backup_whatsapp_media(output_dir, device_serial=device_serial)
            if results["media"]["success"]:
                print(f"[OK] {results['media']['downloaded_count']} medya dosyası indirildi")
            else:
                print("[UYARI] Medya dosyaları bulunamadı")
        
        results["success"] = (results["databases"] and results["databases"]["success"]) or \
                            (results["media"] and results["media"]["success"])
        
        return results

