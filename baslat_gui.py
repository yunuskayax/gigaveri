"""
GUI Başlatıcı - Tek tıkla çalıştırma
Windows için basit grafik arayüz
"""
import os
import sys
import subprocess
import tkinter as tk
from tkinter import messagebox, scrolledtext
from threading import Thread


class AppLauncher:
    """GUI Başlatıcı sınıfı"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("ADB Telefon Veri Alma Uygulaması")
        self.root.geometry("600x400")
        self.root.resizable(False, False)
        
        # Pencereyi ortala
        self.center_window()
        
        # Stil
        bg_color = "#2b2b2b"
        fg_color = "#ffffff"
        button_color = "#4CAF50"
        
        self.root.configure(bg=bg_color)
        
        # Başlık
        title_label = tk.Label(
            root,
            text="📱 ADB Telefon Veri Alma",
            font=("Arial", 18, "bold"),
            bg=bg_color,
            fg=fg_color
        )
        title_label.pack(pady=20)
        
        # Alt başlık
        subtitle_label = tk.Label(
            root,
            text="Android telefonunuzdan veri almak için başlatın",
            font=("Arial", 10),
            bg=bg_color,
            fg="#cccccc"
        )
        subtitle_label.pack(pady=5)
        
        # Durum alanı
        self.status_text = scrolledtext.ScrolledText(
            root,
            height=12,
            width=65,
            bg="#1e1e1e",
            fg="#00ff00",
            font=("Consolas", 9),
            wrap=tk.WORD
        )
        self.status_text.pack(pady=20, padx=20)
        self.status_text.insert("1.0", "[BILGI] Hazır! Başlat butonuna tıklayın.\n")
        self.status_text.config(state=tk.DISABLED)
        
        # Butonlar
        button_frame = tk.Frame(root, bg=bg_color)
        button_frame.pack(pady=10)
        
        self.start_button = tk.Button(
            button_frame,
            text="🚀 Uygulamayı Başlat",
            command=self.start_app,
            bg=button_color,
            fg="white",
            font=("Arial", 12, "bold"),
            width=20,
            height=2,
            cursor="hand2"
        )
        self.start_button.pack(side=tk.LEFT, padx=10)
        
        self.exit_button = tk.Button(
            button_frame,
            text="❌ Çıkış",
            command=self.exit_app,
            bg="#f44336",
            fg="white",
            font=("Arial", 12, "bold"),
            width=15,
            height=2,
            cursor="hand2"
        )
        self.exit_button.pack(side=tk.LEFT, padx=10)
        
        # Bilgi etiketi
        info_label = tk.Label(
            root,
            text="💡 İpucu: Telefonunuzu USB ile bağlamayı unutmayın!",
            font=("Arial", 9),
            bg=bg_color,
            fg="#ffa500"
        )
        info_label.pack(pady=10)
        
        self.process = None
    
    def center_window(self):
        """Pencereyi ekranın ortasına yerleştir"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def log(self, message):
        """Durum alanına mesaj yaz"""
        self.status_text.config(state=tk.NORMAL)
        self.status_text.insert(tk.END, f"{message}\n")
        self.status_text.see(tk.END)
        self.status_text.config(state=tk.DISABLED)
        self.root.update()
    
    def check_python(self):
        """Python'un yüklü olup olmadığını kontrol et"""
        try:
            result = subprocess.run(
                ["python", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                version = result.stdout.strip()
                self.log(f"[OK] Python bulundu: {version}")
                return True
        except:
            pass
        
        self.log("[HATA] Python bulunamadı!")
        return False
    
    def start_app(self):
        """Ana uygulamayı başlat"""
        self.start_button.config(state=tk.DISABLED)
        self.log("=" * 50)
        self.log("[BILGI] Uygulama başlatılıyor...")
        
        # Python kontrolü
        if not self.check_python():
            messagebox.showerror(
                "Hata",
                "Python bulunamadı!\n\n"
                "Lütfen Python'u yükleyin:\n"
                "https://www.python.org/downloads/"
            )
            self.start_button.config(state=tk.NORMAL)
            return
        
        # Ana uygulamayı başlat
        self.log("[BILGI] Ana uygulama başlatılıyor...")
        self.log("[BILGI] Konsol penceresi açılacak...")
        
        try:
            # Yeni konsol penceresinde çalıştır
            if sys.platform == "win32":
                # Windows'ta yeni konsol penceresi aç
                subprocess.Popen(
                    ["python", "main.py"],
                    creationflags=subprocess.CREATE_NEW_CONSOLE
                )
            else:
                # Diğer platformlarda normal çalıştır
                subprocess.Popen(["python", "main.py"])
            
            self.log("[OK] Uygulama başlatıldı!")
            self.log("[BILGI] Konsol penceresinde devam edin.")
            self.log("[BILGI] Bu pencereyi kapatabilirsiniz.")
            
            # 3 saniye sonra pencereyi kapat
            self.root.after(3000, self.minimize_window)
            
        except Exception as e:
            self.log(f"[HATA] Başlatma hatası: {str(e)}")
            messagebox.showerror("Hata", f"Uygulama başlatılamadı:\n{str(e)}")
            self.start_button.config(state=tk.NORMAL)
    
    def minimize_window(self):
        """Pencereyi simge durumuna küçült"""
        self.root.iconify()
    
    def exit_app(self):
        """Uygulamadan çık"""
        if messagebox.askyesno("Çıkış", "Çıkmak istediğinizden emin misiniz?"):
            self.root.destroy()


def main():
    """Ana fonksiyon"""
    root = tk.Tk()
    app = AppLauncher(root)
    root.mainloop()


if __name__ == "__main__":
    main()

