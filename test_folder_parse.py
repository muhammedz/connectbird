#!/usr/bin/env python3
"""
Test: Yeni klasör parse mantığını test et
"""
from imap_sync.imap_client import IMAPClient

SOURCE_HOST = "imap.yandex.com.tr"
SOURCE_USER = "info@muhammedozdemir.com.tr"
SOURCE_PASS = "Muhamm3d1xx"

print("=" * 70)
print("KLASÖR PARSE TESTİ")
print("=" * 70)

try:
    client = IMAPClient(SOURCE_HOST, SOURCE_USER, SOURCE_PASS, 993)
    client.connect()
    print("✓ Bağlantı başarılı!\n")
    
    folders = client.list_folders()
    
    print(f"Bulunan klasörler ({len(folders)} tane):\n")
    print("-" * 70)
    
    for idx, folder in enumerate(folders, 1):
        print(f"{idx:3}. {folder}")
    
    print("-" * 70)
    print(f"\nToplam: {len(folders)} klasör")
    print("\n✓ INBOX, Sent, Drafts görünüyor mu? Kontrol edin!")
    
    client.disconnect()
    
except Exception as e:
    print(f"\n✗ Hata: {e}")
    import traceback
    traceback.print_exc()
