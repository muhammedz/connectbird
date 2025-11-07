#!/usr/bin/env python3
"""
Debug: Ham klasör listesini göster
"""
import sys
import os
import imaplib

# run_auto_transfer.sh'den bilgileri al
SOURCE_HOST = "imap.yandex.com.tr"
SOURCE_USER = input("Yandex e-posta: ").strip()
SOURCE_PASS = input("Yandex şifre: ").strip()

print("\n" + "=" * 70)
print("HAM KLASÖR LİSTESİ (Yandex)")
print("=" * 70)

try:
    # Bağlan
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
            
            print(f"{idx:3}. RAW: {raw}")
            print(f"     DEC: {decoded}")
            print()
        
        print("-" * 70)
        print("\nYukarıda INBOX, Sent, Drafts gibi klasörleri görüyor musunuz?")
        print("Eğer görmüyorsanız, Yandex hesabınızda bu klasörler olmayabilir.")
    
    conn.logout()
    
except Exception as e:
    print(f"\n✗ Hata: {e}")
    import traceback
    traceback.print_exc()
