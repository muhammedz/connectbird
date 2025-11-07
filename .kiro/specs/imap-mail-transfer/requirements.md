# Requirements Document

## Introduction

IMAP Mail Transfer Tool, iki IMAP sunucu arasında e-posta mesajlarını düşük RAM kullanımıyla transfer eden bir araçtır. Thunderbird'ün kullandığı streaming yaklaşımını benimseyerek, her seferinde yalnızca bir mesajı belleğe alır ve büyük miktarda e-posta transferinde bile sabit RAM tüketimi sağlar. Araç, duplicate kontrolü, resume desteği, hata yönetimi ve ilerleme takibi gibi özelliklere sahiptir.

## Glossary

- **Transfer Tool**: IMAP Mail Transfer Tool - İki IMAP sunucu arasında e-posta transferi yapan Python uygulaması
- **Source Server**: Kaynak IMAP Sunucu - E-postaların okunacağı IMAP sunucusu
- **Destination Server**: Hedef IMAP Sunucu - E-postaların yazılacağı IMAP sunucusu
- **Streaming Transfer**: Her seferinde yalnızca bir mesajın belleğe alınarak işlendiği transfer yöntemi
- **UID**: Unique Identifier - IMAP sunucusunda her mesaja atanan benzersiz kimlik numarası
- **Cache Database**: SQLite veritabanı - Transfer edilen mesajların kaydını tutan yerel veritabanı
- **Resume**: Kesintiden sonra kaldığı yerden devam etme özelliği
- **Message Flags**: E-posta durumunu belirten işaretler (okundu, önemli, vb.)
- **RFC822**: E-posta mesaj formatı standardı
- **SSL Connection**: Güvenli şifreli IMAP bağlantısı

## Requirements

### Requirement 1

**User Story:** Kullanıcı olarak, iki IMAP sunucu arasında e-posta transferi yapabilmek istiyorum, böylece e-posta hesabımı başka bir sunucuya taşıyabilirim.

#### Acceptance Criteria

1. WHEN the user provides source and destination IMAP server credentials, THE Transfer Tool SHALL establish SSL connections to both servers
2. WHEN the user specifies a folder name, THE Transfer Tool SHALL retrieve the list of message UIDs from the source folder
3. WHEN the Transfer Tool retrieves message UIDs, THE Transfer Tool SHALL fetch each message individually using streaming transfer
4. WHEN the Transfer Tool fetches a message from Source Server, THE Transfer Tool SHALL append the message to Destination Server before fetching the next message
5. THE Transfer Tool SHALL maintain RAM usage below 200 megabytes during transfer operations

### Requirement 2

**User Story:** Kullanıcı olarak, aynı mesajların tekrar transfer edilmemesini istiyorum, böylece duplicate mesajlardan kaçınabilirim.

#### Acceptance Criteria

1. WHEN the Transfer Tool starts a transfer operation, THE Transfer Tool SHALL check the Cache Database for previously transferred message UIDs
2. WHEN a message UID exists in the Cache Database for the specified folder, THE Transfer Tool SHALL skip that message
3. WHEN the Transfer Tool successfully transfers a message, THE Transfer Tool SHALL record the source UID, destination UID, folder name, and timestamp in the Cache Database
4. THE Transfer Tool SHALL use SQLite as the Cache Database storage mechanism
5. WHEN checking for duplicates, THE Transfer Tool SHALL query the Cache Database using source UID and folder name as the composite key

### Requirement 3

**User Story:** Kullanıcı olarak, transfer işlemi kesintiye uğradığında kaldığı yerden devam edebilmek istiyorum, böylece tüm transferi baştan başlatmak zorunda kalmayayım.

#### Acceptance Criteria

1. WHEN the Transfer Tool encounters a network error, THE Transfer Tool SHALL save the current progress to the Cache Database
2. WHEN the user restarts the Transfer Tool after an interruption, THE Transfer Tool SHALL read the Cache Database to identify already transferred messages
3. WHEN resuming a transfer operation, THE Transfer Tool SHALL skip messages that exist in the Cache Database
4. WHEN resuming a transfer operation, THE Transfer Tool SHALL continue with the next untransferred message UID
5. THE Transfer Tool SHALL persist the Cache Database to disk after each successful message transfer

### Requirement 4

**User Story:** Kullanıcı olarak, transfer işleminin ilerleyişini görebilmek istiyorum, böylece ne kadar süreceğini tahmin edebilirim.

#### Acceptance Criteria

1. WHEN the Transfer Tool begins a transfer operation, THE Transfer Tool SHALL display the total number of messages to be transferred
2. WHILE transferring messages, THE Transfer Tool SHALL display the current message number and total message count
3. WHILE transferring messages, THE Transfer Tool SHALL display the percentage of completion
4. WHEN the Transfer Tool completes each message transfer, THE Transfer Tool SHALL update the progress display
5. WHEN the Transfer Tool completes the transfer operation, THE Transfer Tool SHALL display a completion message with total transferred message count

### Requirement 5

**User Story:** Kullanıcı olarak, transfer sırasında oluşan hataların loglanmasını istiyorum, böylece sorunları tespit edip çözebilirim.

#### Acceptance Criteria

1. WHEN the Transfer Tool encounters any error, THE Transfer Tool SHALL write the error details to a log file
2. WHEN a network error occurs, THE Transfer Tool SHALL retry the operation up to 3 times before logging failure
3. IF a message exceeds the maximum size limit, THEN THE Transfer Tool SHALL skip the message and log the UID with size information
4. WHEN an unrecoverable error occurs for a message, THE Transfer Tool SHALL log the error and continue with the next message
5. THE Transfer Tool SHALL include timestamp, error type, message UID, and error description in each log entry

### Requirement 6

**User Story:** Kullanıcı olarak, mesajların metadata bilgilerinin (tarih, flags) korunmasını istiyorum, böylece hedef sunucuda mesajlar orijinal durumlarıyla görünsün.

#### Acceptance Criteria

1. WHEN the Transfer Tool fetches a message from Source Server, THE Transfer Tool SHALL extract the message date from the message headers
2. WHEN the Transfer Tool fetches a message from Source Server, THE Transfer Tool SHALL extract the Message Flags
3. WHEN the Transfer Tool appends a message to Destination Server, THE Transfer Tool SHALL include the original message date
4. WHEN the Transfer Tool appends a message to Destination Server, THE Transfer Tool SHALL include the original Message Flags
5. THE Transfer Tool SHALL preserve the RFC822 format of the message during transfer

### Requirement 7

**User Story:** Kullanıcı olarak, command-line üzerinden transfer parametrelerini belirtebilmek istiyorum, böylece farklı sunucular ve klasörler için aracı kullanabilirim.

#### Acceptance Criteria

1. THE Transfer Tool SHALL accept source server hostname as a command-line parameter
2. THE Transfer Tool SHALL accept source server username and password as command-line parameters
3. THE Transfer Tool SHALL accept destination server hostname as a command-line parameter
4. THE Transfer Tool SHALL accept destination server username and password as command-line parameters
5. THE Transfer Tool SHALL accept folder name as a command-line parameter

### Requirement 8

**User Story:** Kullanıcı olarak, transfer işleminin bellek sızıntısı olmadan çalışmasını istiyorum, böylece uzun süreli transferlerde sistem kararlılığı sağlansın.

#### Acceptance Criteria

1. WHEN the Transfer Tool completes a message transfer, THE Transfer Tool SHALL release the message data from memory
2. THE Transfer Tool SHALL invoke garbage collection after each message transfer
3. WHILE processing 10,000 messages, THE Transfer Tool SHALL maintain RAM usage below 200 megabytes
4. THE Transfer Tool SHALL handle messages ranging from 1 kilobyte to 50 megabytes without memory overflow
5. WHEN the Transfer Tool runs for extended periods, THE Transfer Tool SHALL maintain stable memory usage without memory leaks

### Requirement 9

**User Story:** Kullanıcı olarak, farklı klasörleri transfer edebilmek istiyorum, böylece tüm e-posta hesabımı taşıyabilirim.

#### Acceptance Criteria

1. WHEN the user specifies a folder name, THE Transfer Tool SHALL verify the folder exists on Source Server
2. WHEN the user specifies a folder name, THE Transfer Tool SHALL create the folder on Destination Server if it does not exist
3. WHEN transferring messages, THE Transfer Tool SHALL maintain folder structure between source and destination
4. THE Transfer Tool SHALL support standard IMAP folder names including INBOX
5. WHEN a folder does not exist on Source Server, THE Transfer Tool SHALL log an error and terminate gracefully

### Requirement 10

**User Story:** Kullanıcı olarak, güvenli bağlantı kullanılmasını istiyorum, böylece e-posta verilerim şifreli olarak iletilsin.

#### Acceptance Criteria

1. WHEN connecting to Source Server, THE Transfer Tool SHALL establish an SSL Connection
2. WHEN connecting to Destination Server, THE Transfer Tool SHALL establish an SSL Connection
3. IF SSL Connection fails, THEN THE Transfer Tool SHALL log the error and terminate
4. THE Transfer Tool SHALL validate SSL certificates during connection establishment
5. THE Transfer Tool SHALL use IMAP over SSL on port 993 by default
