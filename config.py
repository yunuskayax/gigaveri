"""
Yapılandırma dosyası
ADB ve uygulama ayarları
"""

# ADB yolu (sistem PATH'inde ise "adb" yeterli)
ADB_PATH = "adb"

# Varsayılan çıktı dizini
OUTPUT_DIR = "output"

# Varsayılan logcat satır sayısı
DEFAULT_LOG_LINES = 1000

# Varsayılan cihaz dizinleri
DEFAULT_REMOTE_PATHS = {
    "sdcard": "/sdcard",
    "downloads": "/sdcard/Download",
    "pictures": "/sdcard/Pictures",
    "dcim": "/sdcard/DCIM",
    "documents": "/sdcard/Documents"
}

# Timeout süreleri (saniye)
TIMEOUTS = {
    "command": 30,
    "pull": 300,
    "shell": 60
}

