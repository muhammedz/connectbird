# 🚀 IMAP Mail Transfer - Kullanım Kılavuzu

## 📋 İÇİNDEKİLER
1. [Hızlı Başlangıç](#hızlı-başlangıç)
2. [Dış Terminalden Çalıştırma](#dış-terminalden-çalıştırma)
3. [İlerleme Takibi](#ilerleme-takibi)
4. [Cache Sistemi](#cache-sistemi)

---

## 🎯 HIZLI BAŞLANGIÇ

### Yöntem 1: Script ile (ÖNERİLEN)

1. **`run_transfer.sh` dosyasını düzenleyin:**
```bash
nano run_transfer.sh
# veya
open -e run_transfer.sh
```

2. **Bilgilerinizi girin:**
```bash
SOURCE_HOST="imap.yandex.com.tr"
SOURCE_USER="sizin@email.com"
SOURCE_PASS="sifreniz"

DEST_HOST="imap.connect365.com.tr"
DEST_USER="hedef@email.com"
DEST_PASS="hedef_sifreniz"

FOLDER="INBOX"
```

3. **Çalıştırın:**
```bash
./run_transfer.sh
```

---

### Yöntem 2: Doğrudan Komut ile

Terminal'de şu komutu çalıştırın (bilgilerinizi değiştirin):

```bash
python3 -m imap_sync.main \
  --source-host imap.yandex.com.tr \
  --source-user sizin@email.com \
  --source-pass "sifreniz" \
  --dest-host imap.connect365.com.tr \
  --dest-user hedef@email.com \
  --dest-pass "hedef_sifreniz" \
  --folder INBOX
```

---

### Yöntem 3: Environment Variable ile (EN GÜVENLİ)

```bash
# Şifreleri environment variable olarak ayarlayın
export SOURCE_PASS="kaynak_sifreniz"
export DEST_PASS="hedef_sifreniz"

# Şifresiz çalıştırın
python3 -m imap_sync.main \
  --source-host imap.yandex.com.tr \
  --source-user sizin@email.com \
  --dest-host imap.connect365.com.tr \
  --dest-user hedef@email.com \
  --folder INBOX
```

---

## 📊 İLERLEME TAKİBİ

Transfer sırasında **ekranda şunları göreceksiniz:**

```
[INFO] Starting transfer for folder 'INBOX'
[INFO] Found 5000 messages in source folder
[INFO] Found 3500 untransferred messages (1500 already transferred)
[INFO] Transferring 3500 messages...

Transferring |████████░░░░░░░░░░| 1250/3500 [05:30<10:15]
UID 12345: transferring
```

**Gösterilen Bilgiler:**
- ✅ Toplam mesaj sayısı
- ✅ Kaç tanesi zaten transfer edilmiş (cache'den)
- ✅ Kaç tanesi transfer edilecek
- ✅ Anlık ilerleme çubuğu
- ✅ Geçen süre ve tahmini kalan süre
- ✅ Hangi UID'de olduğunuz

---

## 💾 CACHE SİSTEMİ (Kaldığı Yerden Devam)

### Cache Nasıl Çalışır?

1. **İlk Transfer:**
```bash
./run_transfer.sh
# 1000 mesaj transfer edildi, sonra internet kesildi
```

2. **Aynı Komutu Tekrar Çalıştırın:**
```bash
./run_transfer.sh
# Cache sayesinde sadece kalan mesajları transfer eder!
```

**Örnek Çıktı:**
```
[INFO] Found 5000 messages in source folder
[INFO] Found 4000 untransferred messages (1000 already transferred)
[INFO] Transferring 4000 messages...
```

### Cache Dosyaları

- **`transfer_cache.db`** - SQLite veritabanı (transfer edilen mesajlar)
- **`transfer.log`** - Detaylı log dosyası

### Cache'i Sıfırlama (Yeniden Baştan Transfer)

```bash
# Cache'i silin
rm transfer_cache.db

# Tekrar çalıştırın - tüm mesajlar yeniden transfer edilir
./run_transfer.sh
```

---

## 🔍 TRANSFER DURUMUNU İZLEME

### 1. Canlı Log İzleme

Başka bir terminal penceresinde:
```bash
tail -f transfer.log
```

### 2. Hata Kontrolü

```bash
# Hataları görüntüle
grep ERROR transfer.log

# Son 20 hatayı göster
grep ERROR transfer.log | tail -20
```

### 3. İstatistikleri Görüntüleme

Transfer bittiğinde otomatik olarak gösterilir:
```
========================================
Transfer Complete!
========================================
Total messages:      5000
Transferred:         3500
Skipped (cached):    1500
Failed:              0
Total size:          2.5 GB
Duration:            450.2 seconds
Transfer rate:       7.8 messages/second
========================================
```

---

## 📁 FARKLI KLASÖRLER

### INBOX Transfer
```bash
python3 -m imap_sync.main ... --folder INBOX
```

### Sent (Gönderilmiş) Transfer
```bash
python3 -m imap_sync.main ... --folder Sent
```

### Drafts (Taslaklar) Transfer
```bash
python3 -m imap_sync.main ... --folder Drafts
```

### Tüm Klasörleri Transfer (Script)
```bash
#!/bin/bash
FOLDERS=("INBOX" "Sent" "Drafts" "Trash")

for folder in "${FOLDERS[@]}"; do
    echo "Transferring $folder..."
    python3 -m imap_sync.main \
        --source-host imap.source.com \
        --source-user user@source.com \
        --dest-host imap.dest.com \
        --dest-user user@dest.com \
        --folder "$folder"
done
```

---

## ⚙️ GELİŞMİŞ AYARLAR

### Timeout Artırma (Yavaş Bağlantı)
```bash
python3 -m imap_sync.main ... --timeout 120 --retry-count 5
```

### Büyük Mesajları Atlama
```bash
# 25MB'dan büyük mesajları atla
python3 -m imap_sync.main ... --max-message-size 26214400
```

### Özel Log ve Cache Dosyaları
```bash
python3 -m imap_sync.main ... \
  --log-file my_transfer.log \
  --cache-db my_cache.db
```

---

## 🛑 TRANSFER'İ DURDURMA

### Güvenli Durdurma
```
Ctrl + C tuşuna basın
```

**Ne olur?**
- ✅ Mevcut mesaj transfer edilir
- ✅ Cache güncellenir
- ✅ Bağlantılar düzgün kapatılır
- ✅ Kaldığı yer kaydedilir

### Tekrar Başlatma
```bash
# Aynı komutu tekrar çalıştırın
./run_transfer.sh
# Kaldığı yerden devam eder!
```

---

## 🔐 GÜVENLİK İPUÇLARI

### 1. Şifreleri Güvenli Saklama
```bash
# Environment variable kullanın
export SOURCE_PASS="sifre"
export DEST_PASS="sifre"

# Veya macOS Keychain kullanın
export SOURCE_PASS=$(security find-generic-password -s "email-source" -w)
```

### 2. Gmail için Uygulama Şifresi
1. Google Hesap → Güvenlik
2. 2 Adımlı Doğrulama'yı aç
3. Uygulama şifreleri → Yeni şifre oluştur
4. Oluşturulan şifreyi kullanın

### 3. Log Dosyalarını Koruma
```bash
chmod 600 transfer.log
chmod 600 transfer_cache.db
```

---

## 🐛 SORUN GİDERME

### "Authentication failed" Hatası
- ✅ Kullanıcı adı ve şifreyi kontrol edin
- ✅ IMAP erişiminin aktif olduğunu kontrol edin
- ✅ 2FA varsa uygulama şifresi kullanın

### "Connection timeout" Hatası
```bash
# Timeout'u artırın
python3 -m imap_sync.main ... --timeout 120 --retry-count 5
```

### "Folder not found" Hatası
```bash
# Klasör adını kontrol edin (büyük/küçük harf önemli)
# Doğru: INBOX, Sent, Drafts
# Yanlış: inbox, sent, drafts
```

### Transfer Çok Yavaş
```bash
# İnternet hızınızı kontrol edin
# Büyük mesajları atlayın
python3 -m imap_sync.main ... --max-message-size 10485760
```

---

## 📞 YARDIM

Daha fazla bilgi için:
```bash
python3 -m imap_sync.main --help
```

veya `README.md` dosyasına bakın.
