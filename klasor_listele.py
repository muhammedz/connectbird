#!/usr/bin/env python3
"""
Yandex sunucusundaki klasörleri listele
"""
import imaplib
import sys

print("=" * 60)
print("YANDEX KLASÖR LİSTESİ")
print("=" * 60)
print()

# Bilgilerinizi buraya girin
SOURCE_HOST = input("Yandex sunucu (örn: imap.yandex.com.tr): ").strip() or "imap.yandex.com.tr"
SOURCE_USER = input("Yandex e-posta adresiniz: ").strip()
SOURCE_PASS = input("Yandex şifreniz: ").strip()

print()
print("Bağlanıyor...")

try:
    # Bağlan
    conn = imaplib.IMAP4_SSL(SOURCE_HOST, 993)
    conn.login(SOURCE_USER, SOURCE_PASS)
    
    print("✓ Bağlantı başarılı!")
    print()
    print("=" * 60)
    print("MEVCUT KLASÖRLER:")
    print("=" * 60)
    
    # Klasörleri listele
    status, folders = conn.list()
    
    if status == 'OK':
        print()
        for folder in folders:
            # Klasör adını parse et
            folder_str = folder.decode() if isinstance(folder, bytes) else str(folder)
            print(f"  {folder_str}")
        
        print()
        print("=" * 60)
        print("ÖNEMLİ:")
        print("=" * 60)
        print("Yukarıdaki listeden doğru klasör adını bulun.")
        print("Örneğin:")
        print("  - INBOX")
        print("  - Inbox")
        print("  - Sent")
        print("  - Отправленные (Rusça)")
        print()
        print("run_transfer.sh dosyasındaki FOLDER değerini")
        print("yukarıdaki listeden birine değiştirin.")
        print("=" * 60)
    
    conn.logout()
    
except imaplib.IMAP4.error as e:
    print(f"✗ IMAP Hatası: {e}")
    print()
    print("Kontrol edin:")
    print("  - E-posta adresi doğru mu?")
    print("  - Şifre doğru mu?")
    print("  - IMAP erişimi aktif mi?")
    sys.exit(1)
except Exception as e:
    print(f"✗ Hata: {e}")
    sys.exit(1)
