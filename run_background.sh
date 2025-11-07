#!/bin/bash

# IMAP Mail Transfer - ARKA PLANDA ÇALIŞTIRMA
# RAM tüketimi düşük, arka planda güvenle çalışır

# ============================================
# KAYNAK SUNUCU BİLGİLERİ
# ============================================
SOURCE_HOST="imap.yandex.com.tr"
SOURCE_USER="info@muhammedozdemir.com.tr"
SOURCE_PASS="Muhamm3d1xx"

# ============================================
# HEDEF SUNUCU BİLGİLERİ
# ============================================
DEST_HOST="imap.connect365.com.tr"
DEST_USER="test1@lexend.com.tr"
DEST_PASS="Ankara312***"

# ============================================
# AYARLAR
# ============================================
PORT=993
TIMEOUT=60
RETRY_COUNT=3

# Log dosyası
LOG_FILE="transfer.log"
PID_FILE="transfer.pid"

echo "=========================================="
echo "IMAP Mail Transfer - ARKA PLAN MODU"
echo "=========================================="
echo ""

# Şifreleri environment variable olarak ayarla
export SOURCE_PASS
export DEST_PASS

# Arka planda çalıştır
nohup python3 -m imap_sync.main \
  --source-host "$SOURCE_HOST" \
  --source-user "$SOURCE_USER" \
  --dest-host "$DEST_HOST" \
  --dest-user "$DEST_USER" \
  --port "$PORT" \
  --timeout "$TIMEOUT" \
  --retry-count "$RETRY_COUNT" \
  --auto-mode \
  > transfer_output.log 2>&1 &

# Process ID'yi kaydet
TRANSFER_PID=$!
echo $TRANSFER_PID > $PID_FILE

echo "✓ Transfer arka planda başlatıldı!"
echo ""
echo "Process ID: $TRANSFER_PID"
echo "PID dosyası: $PID_FILE"
echo "Log dosyası: $LOG_FILE"
echo "Output dosyası: transfer_output.log"
echo ""
echo "=========================================="
echo "KULLANIM:"
echo "=========================================="
echo ""
echo "📊 İlerlemeyi izlemek için:"
echo "   tail -f $LOG_FILE"
echo ""
echo "📈 RAM kullanımını görmek için:"
echo "   ps aux | grep $TRANSFER_PID"
echo ""
echo "🛑 Durdurmak için:"
echo "   kill $TRANSFER_PID"
echo "   # veya"
echo "   kill \$(cat $PID_FILE)"
echo ""
echo "✅ Çalışıyor mu kontrol:"
echo "   ps -p $TRANSFER_PID"
echo ""
echo "=========================================="
echo ""
echo "💡 Terminal'i kapatabilirsiniz!"
echo "   Transfer arka planda devam edecek."
echo "=========================================="
