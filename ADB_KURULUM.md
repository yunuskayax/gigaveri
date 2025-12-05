# ADB Kurulum Rehberi (Windows)

## ADB Nedir?
Android Debug Bridge (ADB), Android cihazlarınızla iletişim kurmanızı sağlayan bir komut satırı aracıdır.

## Kurulum Adımları

### 1. Android SDK Platform Tools İndirme

1. **Resmi Android Developer sitesinden indirin:**
   - https://developer.android.com/studio/releases/platform-tools
   - "Download SDK Platform-Tools for Windows" linkine tıklayın
   - ZIP dosyasını indirin

2. **ZIP dosyasını açın:**
   - İndirdiğiniz ZIP dosyasını bir klasöre çıkarın (örn: `C:\platform-tools`)
   - İçinde `adb.exe` dosyası olmalı

### 2. PATH'e Ekleme

#### Yöntem 1: Sistem Değişkenleri Üzerinden (Önerilen)

1. Windows tuşu + R tuşlarına basın
2. `sysdm.cpl` yazın ve Enter'a basın
3. "Gelişmiş" sekmesine gidin
4. "Ortam Değişkenleri" butonuna tıklayın
5. "Sistem değişkenleri" bölümünde "Path" değişkenini seçin
6. "Düzenle" butonuna tıklayın
7. "Yeni" butonuna tıklayın
8. Platform Tools klasörünün yolunu girin (örn: `C:\platform-tools`)
9. Tüm pencereleri "Tamam" ile kapatın

#### Yöntem 2: PowerShell ile (Hızlı)

PowerShell'i **Yönetici olarak** açın ve şu komutu çalıştırın:

```powershell
[Environment]::SetEnvironmentVariable("Path", $env:Path + ";C:\platform-tools", "Machine")
```

**Not:** `C:\platform-tools` yerine kendi klasör yolunuzu yazın.

### 3. Kurulumu Test Etme

1. **Yeni bir PowerShell veya CMD penceresi açın** (eski pencereler PATH değişikliğini görmeyebilir)
2. Şu komutu çalıştırın:
   ```bash
   adb version
   ```
3. ADB versiyon bilgisi görünmeli (örn: `Android Debug Bridge version 1.0.41`)

### 4. Telefonu Hazırlama

1. **USB Hata Ayıklama Modunu Açın:**
   - Ayarlar > Telefon Hakkında
   - "Yapı Numarası"na 7 kez dokunun
   - "Geliştirici seçenekleri" açılacak

2. **Geliştirici Seçeneklerini Aktifleştirin:**
   - Ayarlar > Geliştirici Seçenekleri
   - "USB Hata Ayıklama" seçeneğini açın

3. **Telefonu Bağlayın:**
   - Telefonu USB kablosu ile bilgisayara bağlayın
   - Telefonda "USB hata ayıklamaya izin ver" bildirimini onaylayın
   - "Bu bilgisayara her zaman izin ver" seçeneğini işaretleyebilirsiniz

### 5. Bağlantıyı Test Etme

PowerShell veya CMD'de şu komutu çalıştırın:

```bash
adb devices
```

Çıktı şöyle görünmeli:
```
List of devices attached
ABC123XYZ    device
```

"device" yazısı görünüyorsa bağlantı başarılıdır!

## Sorun Giderme

### "adb komutu bulunamadı" Hatası
- PATH'e ekledikten sonra **yeni bir terminal penceresi** açtığınızdan emin olun
- PATH yolunun doğru olduğunu kontrol edin
- Bilgisayarı yeniden başlatmayı deneyin

### "no devices/emulators found" Hatası
- USB kablosunun veri aktarımı yapabildiğinden emin olun (sadece şarj kablosu olmayabilir)
- USB hata ayıklama modunun açık olduğunu kontrol edin
- Telefonda "USB hata ayıklamaya izin ver" bildirimini onaylayın
- Farklı bir USB portu deneyin
- USB kablosunu değiştirin

### "unauthorized" Hatası
- Telefonda "USB hata ayıklamaya izin ver" bildirimini onaylayın
- Telefonu çıkarıp tekrar takın

## Alternatif: ADB'yi Proje Klasörüne Kopyalama

Eğer PATH'e eklemek istemiyorsanız:

1. `platform-tools` klasöründeki `adb.exe` dosyasını proje klasörüne kopyalayın
2. `config.py` dosyasını açın
3. `ADB_PATH` değerini şu şekilde değiştirin:
   ```python
   ADB_PATH = "./adb.exe"  # veya tam yol: "C:\\platform-tools\\adb.exe"
   ```

## Daha Fazla Bilgi

- Resmi Android Developer Dokümantasyonu: https://developer.android.com/studio/command-line/adb
- Platform Tools İndirme: https://developer.android.com/studio/releases/platform-tools

