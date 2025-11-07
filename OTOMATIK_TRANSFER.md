# 🚀 OTOMATİK TÜM KLASÖR TRANSFER

## ✨ YENİ ÖZELLİK: Otomatik Mod

Artık kaynak sunucudaki **TÜM KLASÖRLER** otomatik olarak bulunup transfer edilebilir!

---

## 🎯 NASIL ÇALIŞIR?

### 1️⃣ Kaynak Sunucudaki Klasörleri Bulur
```
Discovering folders on source server...
Found 8 total folders
Will transfer 7 folders
Skipping 1 system folders

Folders to transfer:
  1. INBOX
  2. Sent
  3. Drafts
  4. Trash
  5. Archive
  6. Work
  7. Personal
```

### 2️⃣ Hedef Sunucuda Klasörleri Oluşturur
```
Creating destination folder: INBOX
✓ Created folder: INBOX
Creating destination folder: Sent
✓ Created folder: Sent
...
```

### 3️⃣ Her Klasörü Sırayla Transfer Eder
```
============================================================
TRANSFERRING FOLDER: INBOX
============================================================
Source folder has 5000 messages
Found 3500 untransferred messages (1500 already transferred)
Transferring 3500 messages...

Transferring |████████░░░░░░░░░░| 1250/3500 [05:30<10:15]
UID 12345: transferring

------------------------------------------------------------
Folder 'INBOX' Complete:
  Transferred: 3500
  Skipped: 1500
  Failed: 0
------------------------------------------------------------

============================================================
TRANSFERRING FOLDER: Sent
============================================================
...
```

### 4️⃣ Özet Gösterir
```
============================================================
FINAL TRANSFER SUMMARY
============================================================
Total folders processed: 7
  Successful: 7
  Failed: 0

Total messages transferred: 12,450
Total messages skipped: 3,200
Total messages failed: 0
Total data transferred: 8.5 GB

Per-folder summary:
------------------------------------------------------------
✓ INBOX: 3500 transferred, 1500 skipped, 0 failed
✓ Sent: 2100 transferred, 800 skipped, 0 failed
✓ Drafts: 45 transferred, 12 skipped, 0 failed
✓ Trash: 1200 transferred, 300 skipped, 0 failed
✓ Archive: 4500 transferred, 500 skipped, 0 failed
✓ Work: 850 transferred, 50 skipped, 0 failed
✓ Personal: 255 transferred, 38 skipped, 0 failed
============================================================
```

---

## 🚀 KULLANIM

### Yöntem 1: Script ile (EN KOLAY)

1. **`run_auto_transfer.sh` dosyasını düzenleyin:**
```bash
nano run_auto_transfer.sh
# veya
open -e run_auto_transfer.sh
```

2. **Bilgilerinizi girin:**
```bash
SOURCE_HOST="imap.yandex.com.tr"
SOURCE_USER="sizin@email.com"
SOURCE_PASS="sifreniz"

DEST_HOST="imap.connect365.com.tr"
DEST_USER="hedef@email.com"
DEST_PASS="hedef_sifreniz"
```

3. **Çalıştırın:**
```bash
cd /Users/m/connectbird
./run_auto_transfer.sh
```

---

### Yöntem 2: Doğrudan Komut

```bash
cd /Users/m/connectbird

python3 -m imap_sync.main \
  --source-host imap.yandex.com.tr \
  --source-user sizin@email.com \
  --source-pass "sifreniz" \
  --dest-host imap.connect365.com.tr \
  --dest-user hedef@email.com \
  --dest-pass "hedef_sifreniz" \
  --auto-mode
```

**DİKKAT:** `--folder` parametresi YOK! Sadece `--auto-mode` var.

---

## 🆚 TEK KLASÖR vs OTOMATİK MOD

### Tek Klasör Modu (Eski)
```bash
./run_transfer.sh
# veya
python3 -m imap_sync.main ... --folder INBOX
```
- ✅ Sadece belirtilen klasörü transfer eder
- ✅ Daha hızlı (tek klasör)
- ❌ Her klasör için ayrı çalıştırmanız gerekir

### Otomatik Mod (Yeni) ⭐
```bash
./run_auto_transfer.sh
# veya
python3 -m imap_sync.main ... --auto-mode
```
- ✅ TÜM klasörleri otomatik bulur
- ✅ Hedef sunucuda klasörleri oluşturur
- ✅ Tüm klasörleri sırayla transfer eder
- ✅ Tek komutla tüm hesabı taşır
- ⚠️ Daha uzun sürer (tüm klasörler)

---

## 💾 CACHE SİSTEMİ

Her iki modda da cache çalışır:

```bash
# İlk çalıştırma - 5000 mesaj transfer edildi, kesildi
./run_auto_transfer.sh

# İkinci çalıştırma - Kaldığı yerden devam eder
./run_auto_transfer.sh
# Sadece kalan mesajları transfer eder!
```

---

## ⚙️ ATLANAN SİSTEM KLASÖRLER

Otomatik mod şu klasörleri ATLAR:
- `[Gmail]` - Gmail sistem klasörü
- `Notes` - Apple Notes
- `Contacts` - Kişiler klasörü

Diğer tüm klasörler transfer edilir.

---

## 🛑 TRANSFER'İ DURDURMA

```
Ctrl + C
```

**Ne olur?**
- ✅ Mevcut mesaj tamamlanır
- ✅ Cache güncellenir
- ✅ Kaldığı klasör kaydedilir
- ✅ Aynı komutu tekrar çalıştırınca devam eder

---

## 📊 KARŞILAŞTIRMA

| Özellik | Tek Klasör | Otomatik Mod |
|---------|------------|--------------|
| Klasör seçimi | Manuel | Otomatik |
| Hedef klasör oluşturma | Manuel | Otomatik |
| Tüm hesabı taşıma | ❌ | ✅ |
| Hız | Hızlı (tek klasör) | Yavaş (tüm klasörler) |
| Kullanım kolaylığı | Orta | Çok Kolay |
| Cache desteği | ✅ | ✅ |
| Resume desteği | ✅ | ✅ |

---

## 🎯 HANGİSİNİ KULLANMALIYIM?

### Otomatik Mod Kullan:
- ✅ Tüm e-posta hesabını taşıyorsunuz
- ✅ Birden fazla klasör var
- ✅ Klasör adlarını bilmiyorsunuz
- ✅ En kolay yolu istiyorsunuz

### Tek Klasör Modu Kullan:
- ✅ Sadece INBOX'ı taşıyorsunuz
- ✅ Belirli bir klasörü test ediyorsunuz
- ✅ Daha hızlı sonuç istiyorsunuz

---

## 📝 TERMINAL KOMUTLARI

### Otomatik Mod:
```bash
# 1. Klasöre girin
cd /Users/m/connectbird

# 2. Çalıştırın
./run_auto_transfer.sh
```

### Tek Klasör Modu:
```bash
# 1. Klasöre girin
cd /Users/m/connectbird

# 2. Çalıştırın
./run_transfer.sh
```

---

## ✅ HAZIR!

Artık iki seçeneğiniz var:

1. **`run_transfer.sh`** - Tek klasör transfer
2. **`run_auto_transfer.sh`** - Tüm klasörler otomatik ⭐

İkisini de kullanabilirsiniz! 🎉
