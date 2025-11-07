#!/bin/bash

# IMAP Mail Transfer - OTOMATİK TÜM KLASÖRLER
# Kaynak sunucudaki TÜM klasörleri otomatik bulup transfer eder

# ============================================
# KAYNAK SUNUCU BİLGİLERİ (Transfer edilecek hesap)
# ============================================
SOURCE_HOST="imap.yandex.com.tr"           # Örnek: imap.gmail.com, imap.yandex.com.tr
SOURCE_USER="info@muhammedozdemir.com.tr"      # E-posta adresiniz
SOURCE_PASS="Muhamm3d1xx"              # Şifreniz veya uygulama şifresi

# ============================================
# HEDEF SUNUCU BİLGİLERİ (Transfer edilecek yer)
# ============================================
DEST_HOST="imap.connect365.com.tr"         # Örnek: imap.connect365.com.tr
DEST_USER="test1@lexend.com.tr"    # E-posta adresiniz
DEST_PASS="Ankara312***"                 # Şifreniz veya uygulama şifresi

# ============================================
# TRANSFER AYARLARI
# ============================================
PORT=993                                   # IMAP port (SSL için 993)
TIMEOUT=60                                 # Bağlantı timeout (saniye)
RETRY_COUNT=3                              # Hata durumunda tekrar deneme sayısı

# ============================================
# OTOMATİK TRANSFER BAŞLAT
# ============================================
echo "=========================================="
echo "IMAP Mail Transfer Tool - OTOMATİK MOD"
echo "=========================================="
echo "Kaynak: $SOURCE_HOST ($SOURCE_USER)"
echo "Hedef: $DEST_HOST ($DEST_USER)"
echo "Mod: TÜM KLASÖRLER OTOMATİK"
echo "=========================================="
echo ""
echo "⚠️  Bu mod kaynak sunucudaki TÜM klasörleri"
echo "    otomatik olarak bulup transfer edecek!"
echo ""
echo "Devam etmek için Enter'a basın (Ctrl+C ile iptal)..."
read

# Şifreleri environment variable olarak ayarla (güvenlik için)
export SOURCE_PASS
export DEST_PASS

# Transfer'i başlat
python3 -m imap_sync.main \
  --source-host "$SOURCE_HOST" \
  --source-user "$SOURCE_USER" \
  --dest-host "$DEST_HOST" \
  --dest-user "$DEST_USER" \
  --port "$PORT" \
  --timeout "$TIMEOUT" \
  --retry-count "$RETRY_COUNT" \
  --auto-mode

# Çıkış kodu kontrolü
if [ $? -eq 0 ]; then
    echo ""
    echo "✓ Tüm klasörler başarıyla transfer edildi!"
else
    echo ""
    echo "✗ Transfer sırasında hata oluştu. Lütfen transfer.log dosyasını kontrol edin."
fi
