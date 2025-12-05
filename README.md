# 📱 ADB Telefon Veri Alma Uygulaması

> Android Debug Bridge (ADB) kullanarak Android telefonlardan veri almak için geliştirilmiş Python uygulaması.

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey.svg)](https://www.microsoft.com/windows)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![ADB](https://img.shields.io/badge/ADB-Auto--Install-orange.svg)](https://developer.android.com/studio/command-line/adb)

## 📋 İçindekiler

- [Özellikler](#-özellikler)
- [Gereksinimler](#-gereksinimler)
- [Kurulum](#-kurulum)
- [Kullanım](#-kullanım)
- [Örnekler](#-örnek-kullanım-senaryoları)
- [Sorun Giderme](#-sorun-giderme)
- [Katkıda Bulunma](#-katkıda-bulunma)
- [Lisans](#-lisans)

## ✨ Özellikler

- 🔍 **Cihaz Yönetimi**
  - Bağlı cihazları listeleme
  - Detaylı cihaz bilgilerini alma (model, marka, Android sürümü)
  
- 📦 **Uygulama Yönetimi**
  - Yüklü uygulamaları listeleme
  - Uygulama bilgilerini görüntüleme
  
- 📁 **Dosya İşlemleri**
  - Dosya ve dizin çekme (pull)
  - Dosya listesi görüntüleme
  
- 📊 **Sistem Bilgileri**
  - Logcat alma ve kaydetme
  - Shell komutları çalıştırma
  
- 💾 **Yedekleme**
  - **Telefon yedeklemesi oluşturma (ADB Backup)**
  - **Yedekleme geri yükleme (ADB Restore)**

## 🔧 Gereksinimler

| Gereksinim | Minimum Versiyon |
|------------|------------------|
| Python | 3.7+ |
| İşletim Sistemi | Windows 10+ |
| İnternet | İlk kurulum için gerekli |

> **Not:** ADB ve diğer paketler otomatik olarak kurulur! Manuel kurulum gerekmez.

## 🚀 Hızlı Başlangıç

### ⚡ Tek Tıkla Çalıştırma

Windows kullanıcıları için hazır başlatıcı dosyalar:

| Dosya | Açıklama |
|-------|----------|
| `BASLAT.bat` | Konsol versiyonu (çift tıkla) |
| `BASLAT_GUI.bat` | Grafik arayüz (çift tıkla) |
| `BASLAT.vbs` | Gizli konsol penceresi |

**Kullanım:** İstediğiniz dosyaya çift tıklayın! 🎉

## 🚀 Kurulum

### Otomatik Kurulum (Önerilen)

Uygulama ilk çalıştırıldığında eksik paketleri otomatik olarak kontrol eder ve kurar:

1. **Python paketlerini kontrol eder** (şu anda ek paket gerekmez)
2. **ADB'yi kontrol eder:**
   - Önce sistem PATH'inde arar
   - Bulamazsa proje klasöründe arar
   - Bulamazsa otomatik olarak indirip kurar

### Manuel Kurulum

Eğer otomatik kurulum çalışmazsa:

```bash
python installer.py
```

Bu komut tüm eksik paketleri kurar.

### Projeyi İndirme

```bash
git clone https://github.com/kullaniciadi/gigaveri.git
cd gigaveri
```

## 📖 Kullanım

### 1. Telefonunuzu Hazırlayın

1. **Geliştirici Seçeneklerini Aktifleştirin:**
   - Ayarlar > Telefon Hakkında > Yapı Numarası'na 7 kez dokunun

2. **USB Hata Ayıklamayı Açın:**
   - Ayarlar > Geliştirici Seçenekleri > USB Hata Ayıklama'yı açın

### 2. Telefonu Bağlayın

- USB kablosu ile bilgisayara bağlayın
- "USB hata ayıklamaya izin ver" bildirimini onaylayın

### 3. Uygulamayı Çalıştırın

**🎯 Tek Tıkla Başlatma (Önerilen):**

Windows'ta `BASLAT.bat` dosyasına çift tıklayın veya `BASLAT_GUI.bat` ile grafik arayüzü kullanın.

**Alternatif Yöntemler:**

```bash
# Konsol versiyonu
python main.py

# GUI başlatıcı
python baslat_gui.py
```

### 4. İlk Çalıştırma

- ADB bulunamazsa otomatik kurulum teklif edilir
- `E` tuşuna basarak otomatik kurulumu başlatın
- Kurulum tamamlandıktan sonra uygulama başlar

### Menü Seçenekleri

Uygulama çalıştırıldığında interaktif bir menü gösterilir:

| Seçenek | Açıklama |
|---------|----------|
| 1 | Bağlı cihazları listele |
| 2 | Cihaz bilgilerini göster |
| 3 | Yüklü uygulamaları listele |
| 4 | Uygulama bilgilerini göster |
| 5 | Dosya/Dizin çek (pull) |
| 6 | Dosya listesi göster |
| 7 | Logcat al ve kaydet |
| 8 | Shell komutu çalıştır |
| 9 | Telefon yedeklemesi oluştur (ADB Backup) |
| 10 | Yedekleme geri yükle (ADB Restore) |
| 11 | Çıkış |

## 📂 Çıktı Dosyaları

Tüm çıktılar `output/` klasörüne kaydedilir:

| Dosya Tipi | Format | Açıklama |
|------------|--------|----------|
| Cihaz Bilgileri | `device_info_*.json` | Cihaz modeli, marka, Android sürümü |
| Uygulama Listesi | `installed_apps_*.json` | Tüm yüklü uygulamalar |
| Uygulama Bilgileri | `app_info_*.json` | Belirli uygulama detayları |
| Logcat | `logcat_*.txt` | Sistem logları |
| Yedek Dosyaları | `backup_*.ab` | ADB backup dosyaları |
| Çekilen Dosyalar | `output/` | Telefondan çekilen dosyalar |

## 💡 Örnek Kullanım Senaryoları

### 📸 Telefondan Fotoğraf Çekme

```bash
# Menüden "5" seçin (Dosya/Dizin çek)
# Telefondaki yol: /sdcard/DCIM/Camera/
# Yerel yol: output/photos/
```

### 📱 Uygulama Listesi Alma

```bash
# Menüden "3" seçin (Yüklü uygulamaları listele)
# Liste output/installed_apps_*.json dosyasına kaydedilir
```

### 📊 Sistem Loglarını Alma

```bash
# Menüden "7" seçin (Logcat al ve kaydet)
# İstediğiniz satır sayısını girin
# Loglar output/logcat_*.txt dosyasına kaydedilir
```

### 💾 Telefon Yedeklemesi Oluşturma

```bash
# Menüden "9" seçin (Telefon yedeklemesi oluştur)
# Yedekleme tipini seçin:
#   1. Tam yedekleme: Tüm uygulamalar + APK + Paylaşılan depolama
#   2. Sadece uygulamalar: APK dahil
#   3. Sadece uygulamalar: APK hariç
#   4. Paylaşılan depolama: Sadece /sdcard içeriği
#   5. Özel yedekleme: Seçenekleri belirleyin
# Telefon ekranında "Yedekleme başlat" butonuna basın
# Yedek dosyası output/backup_*.ab olarak kaydedilir
```

### 🔄 Yedekleme Geri Yükleme

```bash
# Menüden "10" seçin (Yedekleme geri yükle)
# ⚠️ UYARI: Bu işlem telefon verilerini değiştirebilir!
# "EVET" yazarak onaylayın
# Yedek dosyasını seçin
# Telefon ekranında geri yüklemeyi onaylayın
```

## 🔍 Sorun Giderme

### ❌ "ADB bulunamadı" Hatası

**Çözüm:**
- Uygulama otomatik kurulum teklif edecektir, `E` tuşuna basın
- İnternet bağlantınızı kontrol edin (indirme için gerekli)
- Manuel kurulum için: `python installer.py`
- Detaylı bilgi için: `ADB_KURULUM.md` dosyasına bakın

### ❌ "Hiçbir cihaz bulunamadı" Hatası

**Çözüm:**
- ✅ Telefonun USB ile bağlı olduğundan emin olun
- ✅ USB hata ayıklama modunun açık olduğunu kontrol edin
- ✅ Telefonda "USB hata ayıklamaya izin ver" bildirimini onaylayın
- ✅ USB kablosunu değiştirmeyi deneyin
- ✅ `adb devices` komutunu terminalde çalıştırarak kontrol edin

### ❌ İzin Hatası

**Çözüm:**
- Bazı dosyalar root erişimi gerektirebilir
- `/sdcard/` klasörü genellikle erişilebilir
- Sistem dosyaları için root erişimi gerekebilir

## 📝 Notlar

- ⚠️ Bu uygulama yalnızca USB hata ayıklama modu açık Android cihazlarla çalışır
- ⚠️ Bazı işlemler root erişimi gerektirebilir
- ⏱️ Büyük dosyaların çekilmesi zaman alabilir
- 📁 Tüm işlemler loglanır ve `output/` klasörüne kaydedilir
- 💾 **Yedekleme:** ADB backup komutu telefon ekranında onay gerektirir
- 🔄 **Geri yükleme:** Dikkatli kullanın! Mevcut veriler silinebilir
- 🔐 Yedek dosyaları `.ab` formatındadır ve şifrelenmiş olabilir

## 🤝 Katkıda Bulunma

Katkılarınızı bekliyoruz! Lütfen şu adımları izleyin:

1. Bu projeyi fork edin
2. Feature branch oluşturun (`git checkout -b feature/AmazingFeature`)
3. Değişikliklerinizi commit edin (`git commit -m 'Add some AmazingFeature'`)
4. Branch'inizi push edin (`git push origin feature/AmazingFeature`)
5. Pull Request açın

## 📄 Lisans

Bu proje eğitim amaçlıdır. Kendi sorumluluğunuzda kullanın.

## 🙏 Teşekkürler

- [Android Debug Bridge (ADB)](https://developer.android.com/studio/command-line/adb) - Google
- [Python](https://www.python.org/) - Python Software Foundation

---

<div align="center">

**⭐ Bu projeyi beğendiyseniz yıldız vermeyi unutmayın! ⭐**

Made with ❤️ for Android developers

</div>
