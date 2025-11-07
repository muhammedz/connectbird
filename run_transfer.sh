#!/bin/bash

# IMAP Mail Transfer - Çalıştırma Scripti
# Bu dosyayı düzenleyerek kendi bilgilerinizi girin

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
FOLDER="INBOX"                             # Transfer edilecek klasör (INBOX, Sent, Drafts, vb.)
PORT=993                                   # IMAP port (SSL için 993)
TIMEOUT=60                                 # Bağlantı timeout (saniye)
RETRY_COUNT=3                              # Hata durumunda tekrar deneme sayısı

# ============================================
# TRANSFER BAŞLAT
# ============================================
echo "=========================================="
echo "IMAP Mail Transfer Tool"
echo "=========================================="
echo "Kaynak: $SOURCE_HOST ($SOURCE_USER)"
echo "Hedef: $DEST_HOST ($DEST_USER)"
echo "Klasör: $FOLDER"
echo "=========================================="
echo ""

# Şifreleri environment variable olarak ayarla (güvenlik için)
export SOURCE_PASS
export DEST_PASS

# Transfer'i başlat
python3 -m imap_sync.main \
  --source-host "$SOURCE_HOST" \
  --source-user "$SOURCE_USER" \
  --dest-host "$DEST_HOST" \
  --dest-user "$DEST_USER" \
  --folder "$FOLDER" \
  --port "$PORT" \
  --timeout "$TIMEOUT" \
  --retry-count "$RETRY_COUNT"

# Çıkış kodu kontrolü
if [ $? -eq 0 ]; then
    echo ""
    echo "✓ Transfer başarıyla tamamlandı!"
else
    echo ""
    echo "✗ Transfer sırasında hata oluştu. Lütfen transfer.log dosyasını kontrol edin."
fi
