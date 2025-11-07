#!/usr/bin/env python3
"""
Debug: Ham klasör listesini göster (otomatik)
"""
import imaplib

# Bilgiler
SOURCE_HOST = "imap.yandex.com.tr"
SOURCE_USER = "info@muhammedozdemir.com.tr"
SOURCE_PASS = "Muhamm3d1xx"

print("\n" + "=" * 70)
print("HAM KLASÖR LİSTESİ (Yandex)")
print("=" * 70)

try:
    # Bağlan
    print(f"Bağlanılıyor: {SOURCE_HOST}...")
    conn = imaplib.IMAP4_SSL(SOURCE_HOST, 993)
    conn.login(SOURCE_USER, SOURCE_PASS)
    print("✓ Bağlantı başarılı!\n")
    
    # Ham liste
    status, folders = conn.list()
    
    if status == 'OK':
        print(f"Toplam {len(folders)} klasör bulundu:\n")
        print("-" * 70)
        
        for idx, folder in enumerate(folders, 1):
            # Hem bytes hem decoded göster
            if isinstance(folder, bytes):
                raw = folder
                decoded = folder.decode('utf-7', errors='ignore')
            else:
                raw = str(folder).encode()
                decoded = str(folder)
            
            print(f"{idx:3}. {decoded}")
        
        print("-" * 70)
        print(f"\nToplam: {len(folders)} klasör")
    
    conn.logout()
    
except Exception as e:
    print(f"\n✗ Hata: {e}")
    import traceback
    traceback.print_exc()
