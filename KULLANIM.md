# Hızlı Başlangıç Kılavuzu

## İlk Kullanım

1. **Projeyi çalıştırın:**
   ```bash
   python main.py
   ```

2. **ADB kurulumu:**
   - İlk çalıştırmada ADB bulunamazsa otomatik kurulum teklif edilir
   - "E" tuşuna basarak kurulumu onaylayın
   - İnternet bağlantısı gerekir (yaklaşık 5-10 MB indirme)

3. **Telefonu bağlayın:**
   - USB hata ayıklama modunu açın
   - USB ile bağlayın
   - Bildirimi onaylayın

4. **Menüden seçim yapın:**
   - "1" tuşuna basarak cihazları listele
   - Cihaz otomatik seçilir veya manuel seçim yapabilirsiniz

## Özellikler

### 1. Cihaz Listeleme
- Bağlı tüm Android cihazları gösterir
- Otomatik olarak ilk cihazı seçer

### 2. Cihaz Bilgileri
- Model, marka, Android sürümü
- Seri numarası, SDK versiyonu
- JSON dosyasına kaydedilir

### 3. Uygulama Listesi
- Tüm yüklü uygulamaları listeler
- JSON dosyasına kaydedilir

### 4. Dosya Çekme
- Telefondan dosya veya klasör indirir
- `output/` klasörüne kaydedilir

### 5. Logcat
- Sistem loglarını alır
- Metin dosyasına kaydedilir

## Çıktı Dosyaları

Tüm çıktılar `output/` klasörüne kaydedilir:
- `device_info_*.json` - Cihaz bilgileri
- `installed_apps_*.json` - Uygulama listesi
- `app_info_*.json` - Uygulama detayları
- `logcat_*.txt` - Sistem logları
- Çekilen dosyalar

## İpuçları

- **Hızlı çıkış:** Menüden "9" seçin veya Ctrl+C
- **Dosya yolları:** Android'de `/sdcard/` genellikle erişilebilir
- **Root gerekmez:** Çoğu işlem root gerektirmez
- **Büyük dosyalar:** İndirme işlemi zaman alabilir

## Sorun mu Yaşıyorsunuz?

1. ADB kurulumu için: `python installer.py`
2. Detaylı bilgi için: `ADB_KURULUM.md`
3. Genel bilgi için: `README.md`

