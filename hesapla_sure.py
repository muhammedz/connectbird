#!/usr/bin/env python3
"""
Transfer süresi hesaplama
"""
from datetime import datetime

# Başlangıç ve bitiş zamanları
start_time = datetime.strptime("2025-11-06 14:19:50", "%Y-%m-%d %H:%M:%S")
msg_1500_time = datetime.strptime("2025-11-06 14:32:19", "%Y-%m-%d %H:%M:%S")

# 1500 mesaj için geçen süre
elapsed = (msg_1500_time - start_time).total_seconds()
elapsed_minutes = elapsed / 60

# Hız hesaplama
messages_transferred = 1500
speed_per_second = messages_transferred / elapsed
speed_per_minute = speed_per_second * 60

# Kalan mesajlar
total_messages = 123334
remaining_messages = total_messages - messages_transferred

# Tahmini kalan süre
remaining_seconds = remaining_messages / speed_per_second
remaining_minutes = remaining_seconds / 60
remaining_hours = remaining_minutes / 60

print("=" * 70)
print("INBOX TRANSFER SÜRE TAHMİNİ")
print("=" * 70)
print()
print(f"📊 İLK 1500 MESAJ İSTATİSTİKLERİ:")
print(f"   Başlangıç:     {start_time.strftime('%H:%M:%S')}")
print(f"   1500. mesaj:   {msg_1500_time.strftime('%H:%M:%S')}")
print(f"   Geçen süre:    {elapsed_minutes:.1f} dakika ({elapsed:.0f} saniye)")
print()
print(f"⚡ TRANSFER HIZI:")
print(f"   {speed_per_second:.2f} mesaj/saniye")
print(f"   {speed_per_minute:.1f} mesaj/dakika")
print(f"   {speed_per_minute * 60:.0f} mesaj/saat")
print()
print(f"📧 MESAJ DURUMU:")
print(f"   Toplam:        {total_messages:,} mesaj")
print(f"   Transfer edilen: {messages_transferred:,} mesaj")
print(f"   Kalan:         {remaining_messages:,} mesaj")
print()
print(f"⏱️  TAHMİNİ KALAN SÜRE:")
print(f"   {remaining_hours:.1f} saat")
print(f"   {remaining_minutes:.0f} dakika")
print()

# Tahmini bitiş zamanı
from datetime import timedelta
estimated_finish = msg_1500_time + timedelta(seconds=remaining_seconds)
print(f"🏁 TAHMİNİ BİTİŞ ZAMANI:")
print(f"   {estimated_finish.strftime('%Y-%m-%d %H:%M:%S')}")
print(f"   ({estimated_finish.strftime('%d %B %Y, %H:%M')})")
print()
print("=" * 70)
print()
print("💡 NOT:")
print("   - Bu tahmini bir hesaplamadır")
print("   - Büyük dosyalar yavaşlatabilir")
print("   - Ağ hızı değişebilir")
print("   - Ctrl+C ile durdurup sonra devam edebilirsiniz")
print("=" * 70)
