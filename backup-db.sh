#!/bin/bash
# Prosty skrypt do backupu bazy danych

DB_NAME="app_database"
BACKUP_DIR="/var/backups/db"
DATE=$(date +%Y%m%d_%H%M%S)
FILENAME="${BACKUP_DIR}/${DB_NAME}_${DATE}.sql.gz"

# Sprawdź czy katalog istnieje
if [ ! -d "$BACKUP_DIR" ]; then
  mkdir -p "$BACKUP_DIR"
  echo "Utworzono katalog $BACKUP_DIR"
fi

# Wykonaj backup
echo "Rozpoczynam backup bazy $DB_NAME..."
mysqldump -u root -p "$DB_NAME" | gzip > "$FILENAME"

if [ $? -eq 0 ]; then
  echo "Backup zakończony sukcesem: $FILENAME"
else
  echo "Błąd podczas wykonywania backupu!"
  exit 1
fi
