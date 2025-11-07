@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

REM IMAP Mail Transfer - SMART MODE (Windows)
REM Otomatik cache yönetimi ve iş takibi

REM Klasörler
set "JOBS_DIR=.imap_jobs"
set "CACHES_DIR=%JOBS_DIR%\caches"
set "LOGS_DIR=%JOBS_DIR%\logs"
set "CONFIGS_DIR=%JOBS_DIR%\configs"

REM Klasörleri oluştur
if not exist "%JOBS_DIR%" mkdir "%JOBS_DIR%"
if not exist "%CACHES_DIR%" mkdir "%CACHES_DIR%"
if not exist "%LOGS_DIR%" mkdir "%LOGS_DIR%"
if not exist "%CONFIGS_DIR%" mkdir "%CONFIGS_DIR%"

:MAIN_MENU
cls
echo ╔════════════════════════════════════════════════════════════╗
echo ║         IMAP MAIL TRANSFER - SMART MODE                   ║
echo ║         Otomatik Cache ^& İş Yönetimi                      ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
echo ═══════════════════════════════════════════════════════════
echo 1) Yeni İş Başlat
echo 2) Mevcut İşe Devam Et
echo 3) İş Listesini Göster
echo 4) Çıkış
echo ═══════════════════════════════════════════════════════════
echo.
set /p "choice=Seçiminiz (1-4): "

if "%choice%"=="1" goto CREATE_JOB
if "%choice%"=="2" goto SELECT_JOB
if "%choice%"=="3" goto LIST_JOBS
if "%choice%"=="4" goto EXIT
echo Geçersiz seçim!
timeout /t 2 >nul
goto MAIN_MENU

:CREATE_JOB
cls
echo ╔════════════════════════════════════════════════════════════╗
echo ║                    YENİ İŞ OLUŞTUR                        ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
echo KAYNAK SUNUCU BİLGİLERİ:
set /p "SOURCE_HOST=Kaynak IMAP sunucu (örn: imap.yandex.com.tr): "
set /p "SOURCE_USER=Kaynak e-posta: "
set /p "SOURCE_PASS=Kaynak şifre: "
echo.
echo HEDEF SUNUCU BİLGİLERİ:
set /p "DEST_HOST=Hedef IMAP sunucu (örn: imap.connect365.com.tr): "
set /p "DEST_USER=Hedef e-posta: "
set /p "DEST_PASS=Hedef şifre: "
echo.
echo TRANSFER AYARLARI:
echo Maksimum mesaj boyutu (büyük dosyaları atlamak için):
echo   1) 10 MB
echo   2) 25 MB (önerilen)
echo   3) 50 MB (varsayılan)
echo   4) Sınırsız
set /p "size_choice=Seçiminiz (1-4, Enter=3): "
if "%size_choice%"=="" set "size_choice=3"

if "%size_choice%"=="1" set "MAX_MESSAGE_SIZE=10485760"
if "%size_choice%"=="2" set "MAX_MESSAGE_SIZE=26214400"
if "%size_choice%"=="3" set "MAX_MESSAGE_SIZE=52428800"
if "%size_choice%"=="4" set "MAX_MESSAGE_SIZE=104857600"

set /a "SIZE_MB=%MAX_MESSAGE_SIZE% / 1024 / 1024"
echo ✓ Maksimum mesaj boyutu: %SIZE_MB% MB
echo.

REM İş ID'si oluştur
set "job_id=%SOURCE_USER%__%DEST_USER%"
set "job_id=%job_id:@=_%"
set "job_id=%job_id:.=_%"

REM Config dosyasını kaydet
set "config_file=%CONFIGS_DIR%\%job_id%.conf"
(
echo SOURCE_HOST=%SOURCE_HOST%
echo SOURCE_USER=%SOURCE_USER%
echo SOURCE_PASS=%SOURCE_PASS%
echo DEST_HOST=%DEST_HOST%
echo DEST_USER=%DEST_USER%
echo DEST_PASS=%DEST_PASS%
echo MAX_MESSAGE_SIZE=%MAX_MESSAGE_SIZE%
) > "%config_file%"

echo ✓ İş kaydedildi!
echo İş ID: %job_id%
echo.
set /p "start_now=Şimdi başlatmak ister misiniz? (e/h): "
if /i "%start_now%"=="e" (
    set "SELECTED_JOB=%job_id%"
    goto START_JOB
)
goto MAIN_MENU

:SELECT_JOB
cls
echo ╔════════════════════════════════════════════════════════════╗
echo ║                    MEVCUT İŞLER                           ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

set "job_count=0"
for %%f in ("%CONFIGS_DIR%\*.conf") do (
    set /a "job_count+=1"
    set "job_!job_count!=%%~nf"
    echo !job_count!) %%~nf
    call :SHOW_JOB_DETAILS "%%~nf"
    echo.
)

if %job_count%==0 (
    echo ❌ Henüz kayıtlı iş yok!
    pause
    goto MAIN_MENU
)

echo ═══════════════════════════════════════════════════════════
set /p "choice=Hangi işi başlatmak istersiniz? (1-%job_count% veya 0=İptal): "

if "%choice%"=="0" goto MAIN_MENU
if %choice% geq 1 if %choice% leq %job_count% (
    set "SELECTED_JOB=!job_%choice%!"
    goto START_JOB
)
echo Geçersiz seçim!
timeout /t 2 >nul
goto SELECT_JOB

:SHOW_JOB_DETAILS
set "job_id=%~1"
set "config_file=%CONFIGS_DIR%\%job_id%.conf"
if not exist "%config_file%" exit /b

for /f "tokens=1,* delims==" %%a in ('type "%config_file%"') do set "%%a=%%b"

echo   📧 Kaynak: %SOURCE_USER%
echo   📬 Hedef:  %DEST_USER%

set "cache_file=%CACHES_DIR%\%job_id%.db"
if exist "%cache_file%" (
    echo   ✓ Cache dosyası mevcut
) else (
    echo   ⚠ Henüz transfer başlamadı
)
exit /b

:START_JOB
set "config_file=%CONFIGS_DIR%\%SELECTED_JOB%.conf"
if not exist "%config_file%" (
    echo ❌ İş bulunamadı: %SELECTED_JOB%
    pause
    goto MAIN_MENU
)

REM Config'i yükle
for /f "tokens=1,* delims==" %%a in ('type "%config_file%"') do set "%%a=%%b"

set "cache_file=%CACHES_DIR%\%SELECTED_JOB%.db"
set "log_file=%LOGS_DIR%\%SELECTED_JOB%.log"

cls
echo ╔════════════════════════════════════════════════════════════╗
echo ║                    TRANSFER BAŞLIYOR                      ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
echo İş ID:     %SELECTED_JOB%
echo Kaynak:    %SOURCE_USER%
echo Hedef:     %DEST_USER%
echo Cache:     %cache_file%
echo Log:       %log_file%
echo.

if exist "%cache_file%" (
    echo ✓ Daha önce transfer yapılmış
    echo ✓ Kaldığı yerden devam edecek!
) else (
    echo ⚠ Yeni transfer başlıyor
)

echo.
echo ═══════════════════════════════════════════════════════════
pause

REM Varsayılan değer
if "%MAX_MESSAGE_SIZE%"=="" set "MAX_MESSAGE_SIZE=52428800"

REM Transfer'i başlat
python -m imap_sync.main --source-host "%SOURCE_HOST%" --source-user "%SOURCE_USER%" --source-password "%SOURCE_PASS%" --dest-host "%DEST_HOST%" --dest-user "%DEST_USER%" --dest-password "%DEST_PASS%" --cache-db "%cache_file%" --log-file "%log_file%" --max-message-size "%MAX_MESSAGE_SIZE%" --auto-mode

echo.
if %ERRORLEVEL%==0 (
    echo ✓ Transfer tamamlandı!
) else (
    echo ⚠ Transfer durdu (Ctrl+C veya hata^)
    echo 💡 Kaldığı yer cache'de kayıtlı, tekrar çalıştırabilirsiniz.
)
echo.
pause
goto MAIN_MENU

:LIST_JOBS
cls
echo ╔════════════════════════════════════════════════════════════╗
echo ║                    TÜM İŞLER                              ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

set "found=0"
for %%f in ("%CONFIGS_DIR%\*.conf") do (
    set "found=1"
    echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    echo İş ID: %%~nf
    call :SHOW_JOB_DETAILS "%%~nf"
    echo.
)

if "%found%"=="0" (
    echo ❌ Henüz kayıtlı iş yok!
)

echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
pause
goto MAIN_MENU

:EXIT
cls
echo.
echo Görüşmek üzere! 👋
echo.
timeout /t 2 >nul
exit /b 0
