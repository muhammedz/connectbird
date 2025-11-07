#!/usr/bin/env python3
"""
Yandex'teki TÜM klasörleri göster (filtresiz)
"""
import sys
import os

# Şifreleri environment'dan al
SOURCE_HOST = "imap.yandex.com.tr"
SOURCE_USER = os.environ.get('SOURCE_USER', 'kullanici@yandex.com.tr')
SOURCE_PASS = os.environ.get('SOURCE_PASS', '')

if not SOURCE_PASS:
    print("Hata: SOURCE_PASS environment variable ayarlanmamış!")
    print("Kullanım: SOURCE_PASS='sifreniz' python3 tum_klasorleri_goster.py")
    sys.exit(1)

# IMAP client'ı import et
from imap_sync.imap_client import IMAPClient

print("=" * 60)
print("YANDEX - TÜM KLASÖRLER (FİLTRESİZ)")
print("=" * 60)
print()

try:
    # Bağlan
    client = IMAPClient(SOURCE_HOST, SOURCE_USER, SOURCE_PASS, 993)
    client.connect()
    print("✓ Bağlantı başarılı!")
    print()
    
    # Ham klasör listesini al
    import imaplib
    status, folders = client._connection.list()
    
    if status == 'OK':
        print(f"Toplam {len(folders)} klasör bulundu:")
        print("-" * 60)
        
        for idx, folder in enumerate(folders, 1):
            folder_str = folder.decode('utf-7') if isinstance(folder, bytes) else str(folder)
            print(f"{idx:3}. {folder_str}")
        
        print("-" * 60)
        print()
        print("INBOX, Sent, Drafts gibi ana klasörleri yukarıda bulun.")
        print("Bunlar transfer edilmedi çünkü farklı isimde olabilirler.")
    
    client.disconnect()
    
except Exception as e:
    print(f"✗ Hata: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
