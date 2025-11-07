# IMAP Mail Transfer Tool

IMAP Mail Transfer Tool, iki IMAP sunucu arasında e-posta mesajlarını düşük RAM kullanımıyla transfer eden bir Python uygulamasıdır. Thunderbird'ün kullandığı streaming yaklaşımını benimseyerek, her seferinde yalnızca bir mesajı belleğe alır ve büyük miktarda e-posta transferinde bile sabit RAM tüketimi (~100-200MB) sağlar.

## Özellikler

- **Düşük RAM Kullanımı**: Streaming transfer ile sabit bellek kullanımı
- **Duplicate Kontrolü**: SQLite cache ile tekrar eden transferleri önleme
- **Resume Desteği**: Kesintiden sonra kaldığı yerden devam etme
- **İlerleme Takibi**: Gerçek zamanlı transfer durumu gösterimi
- **Hata Yönetimi**: Otomatik retry mekanizması ve detaylı loglama
- **Metadata Koruması**: Mesaj tarihi ve flags'lerinin korunması
- **Güvenli Bağlantı**: SSL/TLS şifreli IMAP bağlantıları

## Gereksinimler

- Python 3.8 veya üzeri
- İki IMAP sunucuya erişim (kaynak ve hedef)
- SSL/TLS desteği (port 993)

## Kurulum

```bash
# Repository'yi klonlayın
git clone <repo-url>
cd imap-mail-transfer

# Bağımlılıkları yükleyin
pip install -r requirements.txt
```

## Kullanım

### Temel Kullanım

```bash
python3 -m imap_sync.main \
  --source-host imap.source.com \
  --source-user user@source.com \
  --source-pass SOURCE_PASSWORD \
  --dest-host imap.destination.com \
  --dest-user user@destination.com \
  --dest-pass DEST_PASSWORD \
  --folder INBOX
```

### Environment Variables ile Şifre Kullanımı

Güvenlik için şifreleri environment variable olarak kullanabilirsiniz:

```bash
export SOURCE_PASS="your_source_password"
export DEST_PASS="your_destination_password"

python3 -m imap_sync.main \
  --source-host imap.source.com \
  --source-user user@source.com \
  --dest-host imap.destination.com \
  --dest-user user@destination.com \
  --folder INBOX
```

### Tüm Parametreler

```bash
python3 -m imap_sync.main \
  --source-host imap.source.com \
  --source-user user@source.com \
  --source-pass SOURCE_PASSWORD \
  --dest-host imap.destination.com \
  --dest-user user@destination.com \
  --dest-pass DEST_PASSWORD \
  --folder INBOX \
  --port 993 \
  --timeout 60 \
  --retry-count 3 \
  --log-file transfer.log \
  --cache-db transfer_cache.db
```

### Parametreler

| Parametre | Açıklama | Varsayılan |
|-----------|----------|------------|
| `--source-host` | Kaynak IMAP sunucu adresi | (zorunlu) |
| `--source-user` | Kaynak sunucu kullanıcı adı | (zorunlu) |
| `--source-pass` | Kaynak sunucu şifresi | $SOURCE_PASS |
| `--dest-host` | Hedef IMAP sunucu adresi | (zorunlu) |
| `--dest-user` | Hedef sunucu kullanıcı adı | (zorunlu) |
| `--dest-pass` | Hedef sunucu şifresi | $DEST_PASS |
| `--folder` | Transfer edilecek klasör adı | (zorunlu) |
| `--port` | IMAP port numarası | 993 |
| `--timeout` | Bağlantı timeout süresi (saniye) | 60 |
| `--retry-count` | Hata durumunda retry sayısı | 3 |
| `--log-file` | Log dosyası yolu | transfer.log |
| `--cache-db` | Cache veritabanı yolu | transfer_cache.db |

## Örnekler

### Yandex'ten Connect365'e Transfer

```bash
python3 -m imap_sync.main \
  --source-host imap.yandex.com.tr \
  --source-user user@yandex.com.tr \
  --dest-host imap.connect365.com.tr \
  --dest-user user@connect365.com.tr \
  --folder INBOX
```

### Gmail'den Başka Sunucuya Transfer

```bash
# Gmail için uygulama şifresi kullanmanız gerekir
export SOURCE_PASS="your-app-password"
export DEST_PASS="destination-password"

python3 -m imap_sync.main \
  --source-host imap.gmail.com \
  --source-user your-email@gmail.com \
  --dest-host imap.destination.com \
  --dest-user your-email@destination.com \
  --folder INBOX
```

### Sent Klasörünü Transfer Etme

```bash
python3 -m imap_sync.main \
  --source-host imap.source.com \
  --source-user user@source.com \
  --dest-host imap.destination.com \
  --dest-user user@destination.com \
  --folder Sent
```

### Drafts (Taslaklar) Klasörünü Transfer Etme

```bash
python3 -m imap_sync.main \
  --source-host imap.source.com \
  --source-user user@source.com \
  --dest-host imap.destination.com \
  --dest-user user@destination.com \
  --folder Drafts
```

### Özel Klasör Transfer Etme

```bash
# Alt klasörler için nokta notasyonu kullanın
python3 -m imap_sync.main \
  --source-host imap.source.com \
  --source-user user@source.com \
  --dest-host imap.destination.com \
  --dest-user user@destination.com \
  --folder "Work.Projects"
```

### Kesintiden Sonra Devam Etme

Aynı komutu tekrar çalıştırın. Cache sistemi sayesinde daha önce transfer edilen mesajlar atlanır:

```bash
# İlk çalıştırma (kesintiye uğradı)
python3 -m imap_sync.main --source-host ... --folder INBOX

# Aynı komutu tekrar çalıştırın - kaldığı yerden devam eder
python3 -m imap_sync.main --source-host ... --folder INBOX
```

### Farklı Port Kullanma

```bash
# Standart olmayan port kullanımı
python3 -m imap_sync.main \
  --source-host imap.source.com \
  --source-user user@source.com \
  --dest-host imap.destination.com \
  --dest-user user@destination.com \
  --folder INBOX \
  --port 143  # Dikkat: SSL olmayan bağlantı
```

### Yavaş Bağlantılar İçin Timeout Artırma

```bash
python3 -m imap_sync.main \
  --source-host imap.source.com \
  --source-user user@source.com \
  --dest-host imap.destination.com \
  --dest-user user@destination.com \
  --folder INBOX \
  --timeout 120 \
  --retry-count 5 \
  --retry-delay 10
```

### Büyük Mesajları Sınırlama

```bash
# 25MB'dan büyük mesajları atla
python3 -m imap_sync.main \
  --source-host imap.source.com \
  --source-user user@source.com \
  --dest-host imap.destination.com \
  --dest-user user@destination.com \
  --folder INBOX \
  --max-message-size 26214400
```

### Özel Log ve Cache Dosyaları

```bash
python3 -m imap_sync.main \
  --source-host imap.source.com \
  --source-user user@source.com \
  --dest-host imap.destination.com \
  --dest-user user@destination.com \
  --folder INBOX \
  --log-file /var/log/imap-transfer.log \
  --cache-db /var/cache/imap-transfer.db
```

## Nasıl Çalışır?

1. **Bağlantı**: Her iki IMAP sunucuya SSL bağlantısı kurulur
2. **UID Listesi**: Kaynak klasördeki tüm mesaj UID'leri alınır
3. **Cache Kontrolü**: Daha önce transfer edilmiş mesajlar cache'den kontrol edilir
4. **Streaming Transfer**: Her mesaj tek tek:
   - Kaynak sunucudan fetch edilir
   - Hedef sunucuya append edilir
   - Cache'e kaydedilir
   - Bellekten temizlenir
5. **İlerleme**: Transfer durumu gerçek zamanlı gösterilir
6. **Özet**: Transfer tamamlandığında istatistikler gösterilir

## Bellek Yönetimi

Araç, Thunderbird'ün kullandığı streaming yaklaşımını benimser:

- Her seferinde yalnızca **bir mesaj** belleğe alınır
- Mesaj işlendikten sonra **hemen bellekten temizlenir**
- 10,000+ mesaj transferinde bile **~100-200MB** RAM kullanımı
- Büyük mesajlar (50MB'a kadar) güvenle işlenebilir

## Hata Yönetimi

- **Network Hataları**: 3 kez otomatik retry (exponential backoff)
- **Büyük Mesajlar**: 50MB üzeri mesajlar atlanır ve loglanır
- **Bağlantı Hataları**: Detaylı hata mesajı ile sonlanır
- **Klasör Bulunamadı**: Hedef klasör otomatik oluşturulur

## Log Dosyası

Transfer sırasında tüm işlemler `transfer.log` dosyasına kaydedilir:

```
[2025-11-05 10:30:45] [INFO] [Main] Starting transfer from imap.source.com to imap.dest.com
[2025-11-05 10:30:46] [INFO] [IMAPClient] Connected to source server
[2025-11-05 10:30:47] [INFO] [IMAPClient] Connected to destination server
[2025-11-05 10:30:48] [INFO] [TransferEngine] Found 1500 messages in INBOX
[2025-11-05 10:30:49] [INFO] [TransferEngine] 450 messages already transferred
[2025-11-05 10:30:50] [INFO] [TransferEngine] Starting transfer of 1050 messages
[2025-11-05 10:35:20] [INFO] [TransferEngine] Transfer complete: 1050 transferred, 0 failed
```

## Cache Veritabanı

SQLite veritabanı (`transfer_cache.db`) şu bilgileri saklar:

- Kaynak mesaj UID
- Hedef mesaj UID
- Klasör adı
- Transfer zamanı
- Mesaj boyutu

Bu sayede:
- Duplicate transferler önlenir
- Kesintiden sonra devam edilebilir
- Transfer istatistikleri tutulur

## Güvenlik

- **SSL/TLS**: Tüm bağlantılar şifreli (port 993)
- **Şifre Güvenliği**: Environment variable kullanımı önerilir
- **Log Güvenliği**: Şifreler log dosyasına yazılmaz
- **Dosya İzinleri**: Cache ve log dosyaları sadece owner tarafından okunabilir

## Sorun Giderme

### Bağlantı Hatası

**Hata:**
```
IMAPConnectionError: Failed to connect to imap.server.com
```

**Çözüm**: 
- Sunucu adresini kontrol edin (örn: `imap.gmail.com`, `imap.yandex.com.tr`)
- Port numarasını kontrol edin (varsayılan: 993 SSL için)
- Firewall ayarlarını kontrol edin
- SSL/TLS desteğini kontrol edin
- İnternet bağlantınızı kontrol edin
- Sunucunun çalışır durumda olduğunu doğrulayın

**Test:**
```bash
# Sunucuya bağlantıyı test edin
telnet imap.server.com 993
# veya
openssl s_client -connect imap.server.com:993
```

### Kimlik Doğrulama Hatası

**Hata:**
```
IMAPConnectionError: Authentication failed
```

**Çözüm**:
- Kullanıcı adı ve şifreyi kontrol edin
- IMAP erişiminin aktif olduğunu kontrol edin
- 2FA (İki Faktörlü Doğrulama) kullanıyorsanız, uygulama şifresi oluşturun

**Gmail için:**
1. Google Hesap Ayarları > Güvenlik
2. "2 Adımlı Doğrulama"yı etkinleştirin
3. "Uygulama şifreleri" oluşturun
4. Oluşturulan şifreyi kullanın

**Yandex için:**
1. Yandex Mail Ayarları > Posta İstemcileri
2. "IMAP erişimi"ni etkinleştirin
3. Gerekirse uygulama şifresi oluşturun

### Klasör Bulunamadı

**Hata:**
```
IMAPFolderError: Folder 'INBOX' not found
```

**Çözüm**:
- Klasör adını kontrol edin (büyük/küçük harf duyarlı)
- Kaynak sunucuda klasörün var olduğunu kontrol edin
- Standart klasör adlarını kullanın (INBOX, Sent, Drafts, Trash)
- Bazı sunucularda klasör adları farklı olabilir (örn: "Sent Items" vs "Sent")

**Klasör listesini görüntüleme:**
```python
# Python ile klasörleri listeleyin
import imaplib
conn = imaplib.IMAP4_SSL('imap.server.com')
conn.login('user@server.com', 'password')
print(conn.list())
```

### Timeout Hatası

**Hata:**
```
socket.timeout: timed out
```

**Çözüm**:
- Timeout değerini artırın: `--timeout 120`
- İnternet bağlantınızı kontrol edin
- Sunucu yükünü kontrol edin
- Retry sayısını artırın: `--retry-count 5`

### Bellek Sorunu

**Hata:**
```
MemoryError: Unable to allocate memory
```

**Çözüm**:
- Çok büyük mesajlar varsa `--max-message-size` parametresini düşürün
- Sistem RAM'ini kontrol edin (minimum 512MB önerilir)
- Başka uygulamaları kapatın
- Swap alanını artırın

**Örnek:**
```bash
# 25MB'dan büyük mesajları atla
python3 -m imap_sync.main ... --max-message-size 26214400
```

### SSL Sertifika Hatası

**Hata:**
```
ssl.SSLError: certificate verify failed
```

**Çözüm**:
- Sistem tarih ve saatini kontrol edin
- SSL sertifikalarını güncelleyin
- Sunucu sertifikasının geçerli olduğunu doğrulayın

**macOS için:**
```bash
# Sertifikaları güncelle
/Applications/Python\ 3.x/Install\ Certificates.command
```

**Linux için:**
```bash
# Sertifikaları güncelle
sudo update-ca-certificates
```

### Şifre Environment Variable Hatası

**Hata:**
```
ConfigValidationError: Required field 'source_pass' is missing or empty
```

**Çözüm**:
- Environment variable'ın doğru ayarlandığını kontrol edin
- Şifreyi doğrudan parametre olarak verin veya environment variable kullanın

**Doğru kullanım:**
```bash
# Seçenek 1: Environment variable
export SOURCE_PASS="your-password"
export DEST_PASS="your-password"
python3 -m imap_sync.main ...

# Seçenek 2: Doğrudan parametre
python3 -m imap_sync.main --source-pass "your-password" --dest-pass "your-password" ...
```

### Transfer Çok Yavaş

**Sorun:** Transfer hızı çok düşük

**Çözüm**:
- İnternet bağlantı hızınızı kontrol edin
- Sunucu yanıt sürelerini kontrol edin
- Timeout değerini optimize edin
- Büyük mesajları atlayın

**Performans optimizasyonu:**
```bash
python3 -m imap_sync.main \
  --timeout 30 \
  --retry-count 2 \
  --max-message-size 10485760 \
  ...
```

### Cache Veritabanı Bozuldu

**Hata:**
```
sqlite3.DatabaseError: database disk image is malformed
```

**Çözüm**:
- Cache veritabanını silin ve yeniden başlatın
- Disk alanını kontrol edin

```bash
# Cache'i sil ve yeniden başlat
rm transfer_cache.db
python3 -m imap_sync.main ...
```

**Not:** Cache'i silmek, tüm mesajların yeniden transfer edilmesine neden olur. Duplicate kontrolü yapılmaz.

### Çok Fazla Hata

**Sorun:** Transfer sırasında çok sayıda hata oluşuyor

**Çözüm**:
1. Log dosyasını inceleyin: `cat transfer.log`
2. Hata türlerini belirleyin
3. Retry ayarlarını optimize edin
4. Sunucu durumunu kontrol edin

**Detaylı log inceleme:**
```bash
# Son 50 hatayı görüntüle
grep ERROR transfer.log | tail -50

# Hata türlerini say
grep ERROR transfer.log | cut -d']' -f4 | sort | uniq -c

# Belirli bir UID için hataları bul
grep "UID 12345" transfer.log
```

### Duplicate Mesajlar

**Sorun:** Bazı mesajlar tekrar transfer ediliyor

**Çözüm**:
- Cache veritabanının bozulmadığını kontrol edin
- Aynı cache dosyasını kullandığınızdan emin olun
- Cache'i manuel olarak kontrol edin

**Cache kontrolü:**
```bash
# SQLite ile cache'i incele
sqlite3 transfer_cache.db "SELECT COUNT(*) FROM transferred_messages;"
sqlite3 transfer_cache.db "SELECT * FROM transferred_messages WHERE folder='INBOX' LIMIT 10;"
```

### Özel Karakter Sorunları

**Sorun:** Türkçe karakterler veya özel karakterler hatalı görünüyor

**Çözüm**:
- UTF-8 encoding kullanıldığından emin olun
- Terminal encoding'ini kontrol edin
- Log dosyasının UTF-8 olarak kaydedildiğini doğrulayın

```bash
# Terminal encoding'i ayarla
export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8
```

## Sık Kullanım Senaryoları

### Senaryo 1: Tüm E-posta Hesabını Taşıma

Birden fazla klasörü transfer etmek için her klasör için ayrı komut çalıştırın:

```bash
#!/bin/bash
# transfer_all.sh

FOLDERS=("INBOX" "Sent" "Drafts" "Trash" "Archive")

for folder in "${FOLDERS[@]}"; do
    echo "Transferring folder: $folder"
    python3 -m imap_sync.main \
        --source-host imap.source.com \
        --source-user user@source.com \
        --dest-host imap.destination.com \
        --dest-user user@destination.com \
        --folder "$folder" \
        --log-file "transfer_${folder}.log" \
        --cache-db "cache_${folder}.db"
    
    if [ $? -eq 0 ]; then
        echo "✓ $folder transfer completed"
    else
        echo "✗ $folder transfer failed"
    fi
done
```

### Senaryo 2: Periyodik Senkronizasyon

Cron job ile otomatik senkronizasyon:

```bash
# crontab -e
# Her gün saat 02:00'de çalıştır
0 2 * * * /usr/bin/python3 -m imap_sync.main --source-host ... --folder INBOX >> /var/log/imap-sync.log 2>&1
```

### Senaryo 3: Test Transfer (İlk 100 Mesaj)

Önce küçük bir test yapın:

```bash
# 1. Kaynak sunucuda mesaj sayısını kontrol edin
# 2. İlk transferi yapın
python3 -m imap_sync.main ... --folder INBOX

# 3. Hedef sunucuda mesajları kontrol edin
# 4. Sorun yoksa devam edin
```

### Senaryo 4: Büyük Hesaplar (10,000+ Mesaj)

Büyük hesaplar için öneriler:

```bash
# Timeout ve retry ayarlarını optimize edin
python3 -m imap_sync.main \
    --source-host imap.source.com \
    --source-user user@source.com \
    --dest-host imap.destination.com \
    --dest-user user@destination.com \
    --folder INBOX \
    --timeout 120 \
    --retry-count 5 \
    --retry-delay 10 \
    --max-message-size 26214400
```

## En İyi Uygulamalar

### Güvenlik

1. **Şifreleri Güvenli Saklayın**
   ```bash
   # Environment variable kullanın
   export SOURCE_PASS="password"
   export DEST_PASS="password"
   
   # Veya şifre yöneticisi kullanın
   export SOURCE_PASS=$(pass show email/source)
   export DEST_PASS=$(pass show email/dest)
   ```

2. **Uygulama Şifreleri Kullanın**
   - Gmail, Yandex gibi servislerde ana şifre yerine uygulama şifresi kullanın
   - 2FA etkinleştirin

3. **Log Dosyalarını Koruyun**
   ```bash
   # Log dosyası izinlerini kısıtlayın
   chmod 600 transfer.log
   chmod 600 transfer_cache.db
   ```

### Performans

1. **Timeout Değerlerini Optimize Edin**
   - Hızlı bağlantılar için: `--timeout 30`
   - Yavaş bağlantılar için: `--timeout 120`

2. **Büyük Mesajları Yönetin**
   - Çok büyük mesajları atlayın: `--max-message-size 26214400`
   - Veya ayrı bir transfer ile işleyin

3. **Retry Stratejisi**
   - Kararlı bağlantılar için: `--retry-count 2`
   - Kararsız bağlantılar için: `--retry-count 5`

### Veri Bütünlüğü

1. **Cache'i Koruyun**
   ```bash
   # Cache'in yedeğini alın
   cp transfer_cache.db transfer_cache.db.backup
   ```

2. **Log Dosyalarını Saklayın**
   ```bash
   # Log dosyalarını arşivleyin
   gzip transfer.log
   mv transfer.log.gz logs/transfer_$(date +%Y%m%d).log.gz
   ```

3. **Transfer Sonrası Doğrulama**
   - Hedef sunucuda mesaj sayısını kontrol edin
   - Rastgele mesajları açıp kontrol edin
   - Log dosyasında hata olup olmadığını kontrol edin

### Hata Yönetimi

1. **Hataları İzleyin**
   ```bash
   # Transfer sırasında hataları izleyin
   tail -f transfer.log | grep ERROR
   ```

2. **Başarısız Transferleri Tekrarlayın**
   ```bash
   # Cache'i silmeden aynı komutu tekrar çalıştırın
   # Sadece başarısız mesajlar yeniden denenecektir
   python3 -m imap_sync.main ... --folder INBOX
   ```

3. **Kritik Hatalar İçin Bildirim**
   ```bash
   #!/bin/bash
   python3 -m imap_sync.main ... --folder INBOX
   if [ $? -ne 0 ]; then
       echo "Transfer failed!" | mail -s "IMAP Transfer Error" admin@example.com
   fi
   ```

## Sınırlamalar

- **Tek Yönlü Transfer**: Araç sadece tek yönlü transfer yapar (kaynak → hedef)
- **Klasör Yapısı**: Alt klasörler otomatik olarak transfer edilmez, her klasör için ayrı komut gerekir
- **Mesaj Boyutu**: Varsayılan olarak 50MB'dan büyük mesajlar atlanır
- **Bağlantı Sayısı**: Her seferinde bir kaynak ve bir hedef bağlantısı kullanılır
- **Paralel Transfer**: Mesajlar sırayla transfer edilir, paralel transfer desteklenmez

## Sistem Gereksinimleri

### Minimum Gereksinimler
- **CPU**: 1 core
- **RAM**: 512 MB
- **Disk**: 100 MB (uygulama + cache)
- **Python**: 3.8+
- **İnternet**: Kararlı bağlantı

### Önerilen Gereksinimler
- **CPU**: 2+ cores
- **RAM**: 1 GB
- **Disk**: 1 GB (büyük cache için)
- **Python**: 3.10+
- **İnternet**: Yüksek hızlı bağlantı

## SSS (Sık Sorulan Sorular)

**S: Transfer sırasında mesajlar silinir mi?**
C: Hayır, araç sadece kopyalama yapar. Kaynak sunucudaki mesajlar silinmez.

**S: Aynı mesajı birden fazla kez transfer edebilir miyim?**
C: Cache sistemi duplicate transferleri önler. Ancak cache'i silerseniz, mesajlar tekrar transfer edilir.

**S: Transfer sırasında yeni gelen mesajlar ne olur?**
C: Transfer başladıktan sonra gelen yeni mesajlar bu transfere dahil edilmez. Yeni mesajları transfer etmek için komutu tekrar çalıştırın.

**S: Klasör yapısı korunur mu?**
C: Evet, klasör adları korunur. Ancak alt klasörler için her klasörü ayrı ayrı transfer etmeniz gerekir.

**S: Mesaj flags'leri (okundu, önemli, vb.) korunur mu?**
C: Evet, tüm IMAP flags'leri korunur.

**S: Transfer ne kadar sürer?**
C: Bağlantı hızına, mesaj sayısına ve boyutuna bağlıdır. Ortalama 10-50 mesaj/saniye hızında transfer yapılır.

**S: Birden fazla klasörü aynı anda transfer edebilir miyim?**
C: Evet, her klasör için ayrı terminal penceresi açıp paralel olarak çalıştırabilirsiniz. Ancak her klasör için farklı cache dosyası kullanın.

**S: Gmail'den transfer yaparken "Authentication failed" hatası alıyorum?**
C: Gmail için "Daha az güvenli uygulamalara izin ver" ayarını açmanız veya uygulama şifresi oluşturmanız gerekir.

## Katkıda Bulunma

Katkılarınızı bekliyoruz! Lütfen:

1. Fork yapın
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Değişikliklerinizi commit edin (`git commit -m 'Add amazing feature'`)
4. Branch'inizi push edin (`git push origin feature/amazing-feature`)
5. Pull Request açın

## Lisans

[Lisans bilgisi eklenecek]

## İletişim

[İletişim bilgisi eklenecek]

## Desteklenen IMAP Sunucuları

Araç, standart IMAP4rev1 protokolünü destekleyen tüm sunucularla çalışır:

### Test Edilmiş Sunucular

| Sunucu | Host | Port | Notlar |
|--------|------|------|--------|
| Gmail | imap.gmail.com | 993 | Uygulama şifresi gerekli |
| Yandex | imap.yandex.com.tr | 993 | IMAP erişimi aktif olmalı |
| Outlook/Office365 | outlook.office365.com | 993 | Modern auth destekli |
| Yahoo | imap.mail.yahoo.com | 993 | Uygulama şifresi önerilir |
| iCloud | imap.mail.me.com | 993 | Uygulama şifresi gerekli |
| Zoho | imap.zoho.com | 993 | IMAP erişimi aktif olmalı |
| ProtonMail Bridge | 127.0.0.1 | 1143 | Bridge gerekli |

### Diğer Sunucular

Aşağıdaki sunucu türleri de desteklenir:
- **Dovecot**: Popüler açık kaynak IMAP sunucusu
- **Courier**: Hafif IMAP sunucusu
- **Cyrus**: Kurumsal IMAP sunucusu
- **Exchange Server**: Microsoft Exchange (IMAP etkin)
- **Zimbra**: Kurumsal e-posta platformu
- **cPanel Mail**: Hosting sağlayıcıları

## Teknik Detaylar

### Mimari

```
┌─────────────────┐
│   CLI Interface │
└────────┬────────┘
         │
    ┌────▼────┐
    │  Main   │
    │Controller│
    └────┬────┘
         │
    ┌────┴────────────────────────┐
    │                             │
┌───▼────┐                   ┌────▼────┐
│ Source │                   │  Dest   │
│ IMAP   │                   │  IMAP   │
│ Client │                   │ Client  │
└───┬────┘                   └────┬────┘
    │                             │
    └──────────┬──────────────────┘
               │
        ┌──────▼──────┐
        │  Transfer   │
        │   Engine    │
        └──────┬──────┘
               │
        ┌──────┴──────┐
        │    Cache    │
        │   Manager   │
        └──────┬──────┘
               │
        ┌──────▼──────┐
        │   SQLite    │
        │  Database   │
        └─────────────┘
```

### Transfer Akışı

1. **Başlatma**
   - Konfigürasyon yükleme ve validasyon
   - Log sistemi kurulumu
   - Cache veritabanı başlatma

2. **Bağlantı**
   - SSL/TLS bağlantıları kurma
   - Kimlik doğrulama
   - Klasör seçimi

3. **UID Toplama**
   - Kaynak klasördeki tüm UID'leri alma
   - Cache'den transfer edilmiş UID'leri alma
   - Fark hesaplama (transfer edilecek UID'ler)

4. **Streaming Transfer**
   ```
   For each UID:
     1. Fetch message from source (RFC822 + metadata)
     2. Append message to destination
     3. Mark as transferred in cache
     4. Release memory (del + gc.collect())
     5. Update progress bar
   ```

5. **Sonlandırma**
   - İstatistikleri gösterme
   - Bağlantıları kapatma
   - Cache'i kapatma

### Bellek Yönetimi Stratejisi

```python
# Pseudo-code
def transfer_message(uid):
    # 1. Fetch (sadece bu mesaj)
    message_data = source.fetch(uid)  # ~1-50MB
    
    # 2. Append (hemen işle)
    dest.append(message_data)
    
    # 3. Cache (kaydet)
    cache.mark_transferred(uid)
    
    # 4. Cleanup (bellekten temizle)
    del message_data
    gc.collect()
    
    # Toplam bellek kullanımı: ~100-200MB (sabit)
```

### Hata Yönetimi ve Retry Mekanizması

```python
# Exponential backoff stratejisi
retry_delays = [5, 10, 20]  # saniye

for attempt in range(retry_count):
    try:
        transfer_message(uid)
        break
    except NetworkError:
        if attempt < retry_count - 1:
            time.sleep(retry_delays[attempt])
            continue
        else:
            log_error(uid)
            skip_message(uid)
```

### Cache Veritabanı Şeması

```sql
CREATE TABLE transferred_messages (
    source_uid TEXT NOT NULL,
    dest_uid TEXT NOT NULL,
    folder TEXT NOT NULL,
    transferred_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    message_size INTEGER,
    PRIMARY KEY (source_uid, folder)
);

CREATE INDEX idx_folder ON transferred_messages(folder);
CREATE INDEX idx_transferred_at ON transferred_messages(transferred_at);
```

### Performans Metrikleri

Tipik performans değerleri (1000 mesaj, ortalama 100KB):

| Metrik | Değer |
|--------|-------|
| Transfer hızı | 10-50 mesaj/saniye |
| RAM kullanımı | 100-200 MB (sabit) |
| CPU kullanımı | %5-15 (tek core) |
| Disk I/O | Minimal (sadece cache) |
| Network | Bağlantı hızına bağlı |

### Güvenlik Özellikleri

1. **Şifreleme**
   - TLS 1.2+ zorunlu
   - SSL sertifika doğrulama
   - Şifreli bağlantı (port 993)

2. **Kimlik Bilgileri**
   - Şifreler log'a yazılmaz
   - Environment variable desteği
   - Bellek temizleme

3. **Dosya İzinleri**
   ```bash
   # Otomatik olarak ayarlanan izinler
   transfer.log: 600 (rw-------)
   transfer_cache.db: 600 (rw-------)
   ```

## Gelecek Özellikler

Planlanan geliştirmeler:

- [ ] **Paralel Transfer**: 3-5 mesaj paralel transfer
- [ ] **Web UI**: Transfer durumunu web üzerinden izleme
- [ ] **Folder Sync**: Tüm klasörleri otomatik senkronizasyon
- [ ] **Incremental Sync**: Periyodik senkronizasyon modu
- [ ] **Compression**: Büyük mesajlar için sıkıştırma
- [ ] **Bandwidth Throttling**: Network kullanımını sınırlama
- [ ] **Email Notification**: Transfer tamamlandığında bildirim
- [ ] **Docker Support**: Containerized deployment
- [ ] **API Mode**: REST API ile kontrol

## Teşekkürler

Bu proje, Thunderbird'ün IMAP transfer yaklaşımından ilham almıştır.
