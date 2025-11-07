#!/bin/bash

# ============================================
# ÖRNEK KULLANIM - Dış Terminalden Çalıştırma
# ============================================

echo "╔════════════════════════════════════════════════════════════╗"
echo "║         IMAP Mail Transfer - Örnek Kullanım               ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# ============================================
# YÖNTEM 1: Şifreleri Doğrudan Girerek
# ============================================
echo "📝 YÖNTEM 1: Şifreleri doğrudan komutta"
echo "─────────────────────────────────────────────────────────────"
echo ""
echo "python3 -m imap_sync.main \\"
echo "  --source-host imap.yandex.com.tr \\"
echo "  --source-user kullanici@yandex.com.tr \\"
echo "  --source-pass \"KAYNAK_SİFRENİZ\" \\"
echo "  --dest-host imap.connect365.com.tr \\"
echo "  --dest-user kullanici@connect365.com.tr \\"
echo "  --dest-pass \"HEDEF_SİFRENİZ\" \\"
echo "  --folder INBOX"
echo ""
echo ""

# ============================================
# YÖNTEM 2: Environment Variable ile (Önerilen)
# ============================================
echo "🔐 YÖNTEM 2: Environment Variable ile (GÜVENLİ)"
echo "─────────────────────────────────────────────────────────────"
echo ""
echo "# Önce şifreleri ayarlayın:"
echo "export SOURCE_PASS=\"kaynak_sifreniz\""
echo "export DEST_PASS=\"hedef_sifreniz\""
echo ""
echo "# Sonra çalıştırın:"
echo "python3 -m imap_sync.main \\"
echo "  --source-host imap.yandex.com.tr \\"
echo "  --source-user kullanici@yandex.com.tr \\"
echo "  --dest-host imap.connect365.com.tr \\"
echo "  --dest-user kullanici@connect365.com.tr \\"
echo "  --folder INBOX"
echo ""
echo ""

# ============================================
# EKRANDA GÖRECEKLER
# ============================================
echo "📊 EKRANDA GÖRECEKLER:"
echo "─────────────────────────────────────────────────────────────"
echo ""
echo "[INFO] Starting transfer for folder 'INBOX'"
echo "[INFO] Found 5000 messages in source folder"
echo "[INFO] Found 3500 untransferred messages (1500 already transferred)"
echo "[INFO] Transferring 3500 messages..."
echo ""
echo "Transferring |████████░░░░░░░░░░| 1250/3500 [05:30<10:15]"
echo "UID 12345: transferring"
echo ""
echo "=========================================="
echo "Transfer Complete!"
echo "=========================================="
echo "Total messages:      5000"
echo "Transferred:         3500"
echo "Skipped (cached):    1500"
echo "Failed:              0"
echo "Total size:          2.5 GB"
echo "Duration:            450.2 seconds"
echo "Transfer rate:       7.8 messages/second"
echo "=========================================="
echo ""
echo ""

# ============================================
# CACHE SİSTEMİ
# ============================================
echo "💾 CACHE SİSTEMİ (Kaldığı Yerden Devam):"
echo "─────────────────────────────────────────────────────────────"
echo ""
echo "✅ Transfer sırasında internet kesilirse:"
echo "   → Aynı komutu tekrar çalıştırın"
echo "   → Sadece kalan mesajları transfer eder"
echo "   → Duplicate transfer yapmaz"
echo ""
echo "✅ Cache dosyaları:"
echo "   → transfer_cache.db  (SQLite veritabanı)"
echo "   → transfer.log       (Detaylı log)"
echo ""
echo "✅ Cache'i sıfırlamak için:"
echo "   rm transfer_cache.db"
echo ""
echo ""

# ============================================
# FARKLI KLASÖRLER
# ============================================
echo "📁 FARKLI KLASÖRLER:"
echo "─────────────────────────────────────────────────────────────"
echo ""
echo "INBOX:    --folder INBOX"
echo "Sent:     --folder Sent"
echo "Drafts:   --folder Drafts"
echo "Trash:    --folder Trash"
echo ""
echo ""

# ============================================
# POPÜLER SUNUCULAR
# ============================================
echo "🌐 POPÜLER SUNUCU ADRESLERİ:"
echo "─────────────────────────────────────────────────────────────"
echo ""
echo "Gmail:        imap.gmail.com"
echo "Yandex:       imap.yandex.com.tr"
echo "Outlook:      outlook.office365.com"
echo "Yahoo:        imap.mail.yahoo.com"
echo "Connect365:   imap.connect365.com.tr"
echo ""
echo ""

# ============================================
# HIZLI BAŞLATMA
# ============================================
echo "🚀 HIZLI BAŞLATMA:"
echo "─────────────────────────────────────────────────────────────"
echo ""
echo "1. run_transfer.sh dosyasını düzenleyin"
echo "2. Bilgilerinizi girin"
echo "3. Çalıştırın: ./run_transfer.sh"
echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║  Hazır! Yukarıdaki yöntemlerden birini kullanabilirsiniz  ║"
echo "╚════════════════════════════════════════════════════════════╝"
