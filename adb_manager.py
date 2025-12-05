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

