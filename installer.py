"""
Otomatik Kurulum Modülü
Eksik paketleri ve ADB'yi otomatik olarak kurar
"""
import os
import sys
import subprocess
import zipfile
import shutil
from pathlib import Path
from urllib.request import urlretrieve
from urllib.error import URLError


class AutoInstaller:
    """Otomatik kurulum sınıfı"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.platform_tools_dir = self.project_root / "platform-tools"
        self.adb_path = self.platform_tools_dir / "adb.exe"
        
    def check_python_packages(self):
        """Gerekli Python paketlerini kontrol eder"""
        # Bu proje standart kütüphaneler kullanıyor, ek paket gerekmez
        # Ancak gelecekte eklenebilir paketler için hazır
        required_packages = []
        missing_packages = []
        
        for package in required_packages:
            try:
                __import__(package)
            except ImportError:
                missing_packages.append(package)
        
        return missing_packages
    
    def install_python_packages(self, packages=None):
        """Python paketlerini kurar"""
        if packages is None:
            packages = self.check_python_packages()
        
        if not packages:
            print("[OK] Tüm Python paketleri mevcut")
            return True
        
        print(f"\n[KURULUM] {len(packages)} paket kuruluyor...")
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", "-q"
            ] + packages)
            print("[OK] Python paketleri başarıyla kuruldu")
            return True
        except subprocess.CalledProcessError as e:
            print(f"[HATA] Paket kurulumu başarısız: {str(e)}")
            return False
    
    def check_adb(self):
        """ADB'nin kurulu olup olmadığını kontrol eder"""
        # Önce sistem PATH'inde kontrol et
        try:
            result = subprocess.run(
                ["adb", "version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                print("[OK] ADB sistem PATH'inde bulundu")
                return True, "system"
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass
        
        # Sonra proje klasöründe kontrol et
        if self.adb_path.exists():
            print("[OK] ADB proje klasöründe bulundu")
            return True, str(self.adb_path)
        
        return False, None
    
    def download_platform_tools(self):
        """Android Platform Tools'u indirir"""
        print("\n[KURULUM] Android Platform Tools indiriliyor...")
        
        # Google'ın resmi Platform Tools indirme URL'i
        # Bu URL genellikle stabil kalır
        url = "https://dl.google.com/android/repository/platform-tools-latest-windows.zip"
        
        zip_path = self.project_root / "platform-tools.zip"
        
        # İndirme progress callback
        def show_progress(block_num, block_size, total_size):
            if total_size > 0:
                percent = min(100, (block_num * block_size * 100) // total_size)
                if block_num % 10 == 0:  # Her 10 blokta bir göster
                    print(f"\r[BILGI] İndiriliyor... %{percent}", end='', flush=True)
        
        try:
            print(f"[BILGI] İndirme başlıyor: {url}")
            print("[BILGI] Bu işlem birkaç dakika sürebilir...")
            urlretrieve(url, zip_path, show_progress)
            print("\n[OK] İndirme tamamlandı")
            return str(zip_path)
        except URLError as e:
            print(f"\n[HATA] İndirme hatası: {str(e)}")
            print("[BILGI] İnternet bağlantınızı kontrol edin")
            print("[BILGI] Alternatif: Manuel olarak indirip platform-tools klasörüne koyabilirsiniz")
            return None
        except Exception as e:
            print(f"\n[HATA] Beklenmeyen hata: {str(e)}")
            return None
    
    def extract_platform_tools(self, zip_path):
        """Platform Tools ZIP dosyasını çıkarır"""
        print(f"\n[KURULUM] ZIP dosyası açılıyor: {zip_path}")
        
        try:
            # Geçici bir klasöre çıkar
            temp_extract_dir = self.project_root / "temp_extract"
            temp_extract_dir.mkdir(exist_ok=True)
            
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                # ZIP içindeki tüm dosyaları çıkar
                zip_ref.extractall(temp_extract_dir)
            
            # platform-tools klasörünü bul ve taşı
            extracted_platform_tools = None
            
            # Önce doğrudan platform-tools klasörünü ara
            if (temp_extract_dir / "platform-tools").exists():
                extracted_platform_tools = temp_extract_dir / "platform-tools"
            else:
                # İç içe klasörleri kontrol et
                for item in temp_extract_dir.iterdir():
                    if item.is_dir() and (item / "adb.exe").exists():
                        extracted_platform_tools = item
                        break
            
            if extracted_platform_tools and (extracted_platform_tools / "adb.exe").exists():
                # Eski klasörü sil (varsa)
                if self.platform_tools_dir.exists():
                    shutil.rmtree(self.platform_tools_dir)
                
                # Yeni klasörü taşı
                shutil.move(str(extracted_platform_tools), str(self.platform_tools_dir))
                
                # Geçici klasörü temizle
                try:
                    shutil.rmtree(temp_extract_dir)
                except:
                    pass
                
                print("[OK] ZIP dosyası başarıyla açıldı")
                return True
            else:
                print("[HATA] ZIP içinde platform-tools klasörü bulunamadı")
                return False
                
        except Exception as e:
            print(f"[HATA] ZIP açma hatası: {str(e)}")
            # Geçici klasörü temizle
            try:
                if temp_extract_dir.exists():
                    shutil.rmtree(temp_extract_dir)
            except:
                pass
            return False
    
    def install_adb(self):
        """ADB'yi kurar (indirir ve çıkarır)"""
        # Önce kontrol et
        is_installed, location = self.check_adb()
        if is_installed:
            print(f"[OK] ADB zaten kurulu: {location}")
            return True, location
        
        print("\n[KURULUM] ADB kurulumu başlatılıyor...")
        
        # İndir
        zip_path = self.download_platform_tools()
        if not zip_path:
            return False, None
        
        # Çıkar
        if not self.extract_platform_tools(zip_path):
            return False, None
        
        # ZIP dosyasını sil
        try:
            os.remove(zip_path)
        except:
            pass
        
        # Kontrol et
        if self.adb_path.exists():
            print(f"[OK] ADB başarıyla kuruldu: {self.adb_path}")
            return True, str(self.adb_path)
        else:
            print("[HATA] ADB kurulumu tamamlandı ancak adb.exe bulunamadı")
            return False, None
    
    def setup_all(self):
        """Tüm eksik paketleri kurar"""
        print("=" * 60)
        print("Otomatik Kurulum Başlatılıyor...")
        print("=" * 60)
        
        # Python paketlerini kontrol et ve kur
        missing = self.check_python_packages()
        if missing:
            self.install_python_packages(missing)
        
        # ADB'yi kontrol et ve kur
        is_installed, location = self.check_adb()
        if not is_installed:
            success, adb_location = self.install_adb()
            if success:
                print(f"\n[OK] ADB kuruldu: {adb_location}")
            else:
                print("\n[HATA] ADB kurulumu başarısız!")
                print("[BILGI] Lütfen manuel olarak kurun: ADB_KURULUM.md dosyasına bakın")
                return False
        else:
            print(f"\n[OK] ADB mevcut: {location}")
        
        print("\n" + "=" * 60)
        print("[OK] Kurulum tamamlandı!")
        print("=" * 60)
        return True


def main():
    """Kurulum scripti"""
    installer = AutoInstaller()
    installer.setup_all()


if __name__ == "__main__":
    main()

