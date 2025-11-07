#!/bin/bash

# IMAP Mail Transfer - SMART MODE
# Otomatik cache yönetimi ve iş takibi

# Renkler
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Klasörler
JOBS_DIR=".imap_jobs"
CACHES_DIR="$JOBS_DIR/caches"
LOGS_DIR="$JOBS_DIR/logs"
CONFIGS_DIR="$JOBS_DIR/configs"

# Klasörleri oluştur
mkdir -p "$JOBS_DIR" "$CACHES_DIR" "$LOGS_DIR" "$CONFIGS_DIR"

# Banner
clear
echo -e "${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║         IMAP MAIL TRANSFER - SMART MODE                   ║${NC}"
echo -e "${CYAN}║         Otomatik Cache & İş Yönetimi                      ║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Mevcut işleri listele
list_jobs() {
    local jobs=($(ls -1 "$CONFIGS_DIR"/*.conf 2>/dev/null | xargs -n 1 basename | sed 's/.conf//'))
    echo "${jobs[@]}"
}

# İş detaylarını göster
show_job_details() {
    local job_id=$1
    local config_file="$CONFIGS_DIR/${job_id}.conf"
    
    if [ -f "$config_file" ]; then
        source "$config_file"
        
        local cache_file="$CACHES_DIR/${job_id}.db"
        local log_file="$LOGS_DIR/${job_id}.log"
        
        echo -e "${BLUE}📧 Kaynak:${NC} $SOURCE_USER"
        echo -e "${BLUE}📬 Hedef:${NC}  $DEST_USER"
        
        # Mesaj boyutu limiti
        if [ -n "$MAX_MESSAGE_SIZE" ]; then
            local size_mb=$((MAX_MESSAGE_SIZE / 1024 / 1024))
            echo -e "${BLUE}📏 Max boyut:${NC} ${size_mb} MB"
        fi
        
        if [ -f "$cache_file" ]; then
            local count=$(sqlite3 "$cache_file" "SELECT COUNT(*) FROM transferred_messages;" 2>/dev/null || echo "0")
            echo -e "${GREEN}✓ Transfer edilen:${NC} $count mesaj"
        else
            echo -e "${YELLOW}⚠ Henüz transfer başlamadı${NC}"
        fi
        
        if [ -f "$log_file" ]; then
            local last_line=$(tail -1 "$log_file" 2>/dev/null)
            echo -e "${BLUE}📝 Son durum:${NC} $(echo $last_line | cut -c1-50)..."
        fi
    fi
}

# Ana menü
show_menu() {
    echo -e "${YELLOW}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}1)${NC} Yeni İş Başlat"
    echo -e "${GREEN}2)${NC} Mevcut İşe Devam Et"
    echo -e "${GREEN}3)${NC} İş Listesini Göster"
    echo -e "${GREEN}4)${NC} Çıkış"
    echo -e "${YELLOW}═══════════════════════════════════════════════════════════${NC}"
    echo ""
}

# Yeni iş oluştur
create_new_job() {
    echo ""
    echo -e "${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║                    YENİ İŞ OLUŞTUR                        ║${NC}"
    echo -e "${CYAN}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    
    # Kaynak bilgileri
    echo -e "${BLUE}KAYNAK SUNUCU BİLGİLERİ:${NC}"
    read -p "Kaynak IMAP sunucu (örn: imap.yandex.com.tr): " SOURCE_HOST
    read -p "Kaynak e-posta: " SOURCE_USER
    read -sp "Kaynak şifre: " SOURCE_PASS
    echo ""
    echo ""
    
    # Hedef bilgileri
    echo -e "${BLUE}HEDEF SUNUCU BİLGİLERİ:${NC}"
    read -p "Hedef IMAP sunucu (örn: imap.connect365.com.tr): " DEST_HOST
    read -p "Hedef e-posta: " DEST_USER
    read -sp "Hedef şifre: " DEST_PASS
    echo ""
    echo ""
    
    # Mesaj boyutu ayarı
    echo -e "${BLUE}TRANSFER AYARLARI:${NC}"
    echo -e "${YELLOW}Maksimum mesaj boyutu (büyük dosyaları atlamak için):${NC}"
    echo "  1) 10 MB"
    echo "  2) 25 MB (önerilen)"
    echo "  3) 50 MB (varsayılan)"
    echo "  4) Sınırsız"
    read -p "Seçiminiz (1-4, Enter=3): " size_choice
    size_choice=${size_choice:-3}
    
    case $size_choice in
        1) MAX_MESSAGE_SIZE=$((10 * 1024 * 1024)) ;;
        2) MAX_MESSAGE_SIZE=$((25 * 1024 * 1024)) ;;
        3) MAX_MESSAGE_SIZE=$((50 * 1024 * 1024)) ;;
        4) MAX_MESSAGE_SIZE=$((100 * 1024 * 1024)) ;;
        *) MAX_MESSAGE_SIZE=$((50 * 1024 * 1024)) ;;
    esac
    
    echo -e "${GREEN}✓ Maksimum mesaj boyutu: $((MAX_MESSAGE_SIZE / 1024 / 1024)) MB${NC}"
    echo ""
    
    # İş ID'si oluştur (kaynak_hedef formatında)
    local source_clean=$(echo "$SOURCE_USER" | tr '@.' '_')
    local dest_clean=$(echo "$DEST_USER" | tr '@.' '_')
    local job_id="${source_clean}__${dest_clean}"
    
    # Config dosyasını kaydet
    local config_file="$CONFIGS_DIR/${job_id}.conf"
    cat > "$config_file" << EOF
SOURCE_HOST="$SOURCE_HOST"
SOURCE_USER="$SOURCE_USER"
SOURCE_PASS="$SOURCE_PASS"
DEST_HOST="$DEST_HOST"
DEST_USER="$DEST_USER"
DEST_PASS="$DEST_PASS"
MAX_MESSAGE_SIZE="$MAX_MESSAGE_SIZE"
CREATED_AT="$(date '+%Y-%m-%d %H:%M:%S')"
EOF
    
    echo -e "${GREEN}✓ İş kaydedildi!${NC}"
    echo -e "${BLUE}İş ID:${NC} $job_id"
    echo ""
    
    # Hemen başlat
    read -p "Şimdi başlatmak ister misiniz? (e/h): " start_now
    if [[ "$start_now" == "e" || "$start_now" == "E" ]]; then
        start_job "$job_id"
    fi
}

# Mevcut işleri listele ve seç
select_existing_job() {
    local jobs=($(list_jobs))
    
    if [ ${#jobs[@]} -eq 0 ]; then
        echo -e "${RED}❌ Henüz kayıtlı iş yok!${NC}"
        echo ""
        return 1
    fi
    
    echo ""
    echo -e "${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║                    MEVCUT İŞLER                           ║${NC}"
    echo -e "${CYAN}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    
    local i=1
    for job_id in "${jobs[@]}"; do
        echo -e "${GREEN}$i)${NC} ${YELLOW}$job_id${NC}"
        show_job_details "$job_id"
        echo ""
        ((i++))
    done
    
    echo -e "${YELLOW}═══════════════════════════════════════════════════════════${NC}"
    read -p "Hangi işi başlatmak istersiniz? (1-${#jobs[@]} veya 0=İptal): " choice
    
    if [[ "$choice" -ge 1 && "$choice" -le ${#jobs[@]} ]]; then
        local selected_job="${jobs[$((choice-1))]}"
        start_job "$selected_job"
    elif [ "$choice" != "0" ]; then
        echo -e "${RED}❌ Geçersiz seçim!${NC}"
    fi
}

# İşi başlat
start_job() {
    local job_id=$1
    local config_file="$CONFIGS_DIR/${job_id}.conf"
    
    if [ ! -f "$config_file" ]; then
        echo -e "${RED}❌ İş bulunamadı: $job_id${NC}"
        return 1
    fi
    
    # Config'i yükle
    source "$config_file"
    
    # Dosya yolları
    local cache_file="$CACHES_DIR/${job_id}.db"
    local log_file="$LOGS_DIR/${job_id}.log"
    
    echo ""
    echo -e "${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║                    TRANSFER BAŞLIYOR                      ║${NC}"
    echo -e "${CYAN}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${BLUE}İş ID:${NC}     $job_id"
    echo -e "${BLUE}Kaynak:${NC}    $SOURCE_USER"
    echo -e "${BLUE}Hedef:${NC}     $DEST_USER"
    echo -e "${BLUE}Cache:${NC}     $cache_file"
    echo -e "${BLUE}Log:${NC}       $log_file"
    echo ""
    
    if [ -f "$cache_file" ]; then
        local count=$(sqlite3 "$cache_file" "SELECT COUNT(*) FROM transferred_messages;" 2>/dev/null || echo "0")
        echo -e "${GREEN}✓ Daha önce $count mesaj transfer edilmiş${NC}"
        echo -e "${GREEN}✓ Kaldığı yerden devam edecek!${NC}"
    else
        echo -e "${YELLOW}⚠ Yeni transfer başlıyor${NC}"
    fi
    
    echo ""
    echo -e "${YELLOW}═══════════════════════════════════════════════════════════${NC}"
    read -p "Devam etmek için Enter'a basın (Ctrl+C ile iptal)..."
    echo ""
    
    # Şifreleri environment variable olarak ayarla
    export SOURCE_PASS
    export DEST_PASS
    
    # Varsayılan değerler
    MAX_MESSAGE_SIZE=${MAX_MESSAGE_SIZE:-52428800}  # Varsayılan 50MB
    
    # Transfer'i başlat
    python3 -m imap_sync.main \
        --source-host "$SOURCE_HOST" \
        --source-user "$SOURCE_USER" \
        --dest-host "$DEST_HOST" \
        --dest-user "$DEST_USER" \
        --cache-db "$cache_file" \
        --log-file "$log_file" \
        --max-message-size "$MAX_MESSAGE_SIZE" \
        --auto-mode
    
    local exit_code=$?
    
    echo ""
    if [ $exit_code -eq 0 ]; then
        echo -e "${GREEN}✓ Transfer tamamlandı!${NC}"
    else
        echo -e "${YELLOW}⚠ Transfer durdu (Ctrl+C veya hata)${NC}"
        echo -e "${BLUE}💡 Kaldığı yer cache'de kayıtlı, tekrar çalıştırabilirsiniz.${NC}"
    fi
    echo ""
    read -p "Ana menüye dönmek için Enter'a basın..."
}

# İş listesini göster
show_job_list() {
    local jobs=($(list_jobs))
    
    if [ ${#jobs[@]} -eq 0 ]; then
        echo -e "${RED}❌ Henüz kayıtlı iş yok!${NC}"
        echo ""
        read -p "Ana menüye dönmek için Enter'a basın..."
        return
    fi
    
    echo ""
    echo -e "${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║                    TÜM İŞLER                              ║${NC}"
    echo -e "${CYAN}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    
    for job_id in "${jobs[@]}"; do
        echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo -e "${GREEN}İş ID:${NC} $job_id"
        show_job_details "$job_id"
        echo ""
    done
    
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    read -p "Ana menüye dönmek için Enter'a basın..."
}

# Ana döngü
while true; do
    clear
    echo -e "${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║         IMAP MAIL TRANSFER - SMART MODE                   ║${NC}"
    echo -e "${CYAN}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    
    show_menu
    read -p "Seçiminiz (1-4): " choice
    
    case $choice in
        1)
            create_new_job
            ;;
        2)
            select_existing_job
            ;;
        3)
            show_job_list
            ;;
        4)
            echo ""
            echo -e "${GREEN}Görüşmek üzere! 👋${NC}"
            echo ""
            exit 0
            ;;
        *)
            echo -e "${RED}❌ Geçersiz seçim!${NC}"
            sleep 1
            ;;
    esac
done
