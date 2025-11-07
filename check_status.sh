#!/bin/bash

# Transfer durumunu ve RAM kullanımını kontrol et

PID_FILE="transfer.pid"

echo "=========================================="
echo "TRANSFER DURUM KONTROLÜ"
echo "=========================================="
echo ""

# PID dosyası var mı?
if [ ! -f "$PID_FILE" ]; then
    echo "❌ Transfer çalışmıyor (PID dosyası bulunamadı)"
    echo ""
    echo "Başlatmak için:"
    echo "  ./run_background.sh"
    exit 1
fi

# PID'yi oku
PID=$(cat $PID_FILE)

# Process çalışıyor mu?
if ! ps -p $PID > /dev/null 2>&1; then
    echo "❌ Transfer durmuş (Process ID: $PID)"
    echo ""
    echo "Yeniden başlatmak için:"
    echo "  ./run_background.sh"
    exit 1
fi

echo "✅ Transfer çalışıyor!"
echo ""
echo "Process ID: $PID"
echo ""

# RAM kullanımı
echo "=========================================="
echo "RAM KULLANIMI:"
echo "=========================================="
ps aux | grep $PID | grep -v grep | awk '{printf "  CPU: %s%%\n  RAM: %s MB\n  Çalışma süresi: %s\n", $3, $6/1024, $10}'
echo ""

# Son mesajlar
echo "=========================================="
echo "SON TRANSFER MESAJLARI:"
echo "=========================================="
tail -10 transfer.log | grep -E "transferred|Complete|Processing"
echo ""

# İstatistikler
echo "=========================================="
echo "TRANSFER İSTATİSTİKLERİ:"
echo "=========================================="

# Cache'den istatistik
if [ -f "transfer_cache.db" ]; then
    TOTAL_TRANSFERRED=$(sqlite3 transfer_cache.db "SELECT COUNT(*) FROM transferred_messages;" 2>/dev/null || echo "0")
    echo "  Toplam transfer edilen: $TOTAL_TRANSFERRED mesaj"
    echo ""
    
    # Klasör bazında
    echo "  Klasör bazında:"
    sqlite3 transfer_cache.db "SELECT folder, COUNT(*) as count FROM transferred_messages GROUP BY folder ORDER BY count DESC LIMIT 10;" 2>/dev/null | while IFS='|' read folder count; do
        echo "    - $folder: $count mesaj"
    done
fi

echo ""
echo "=========================================="
echo "KOMUTLAR:"
echo "=========================================="
echo "  İlerlemeyi izle:  tail -f transfer.log"
echo "  Durdur:           kill $PID"
echo "  Yeniden kontrol:  ./check_status.sh"
echo "=========================================="
