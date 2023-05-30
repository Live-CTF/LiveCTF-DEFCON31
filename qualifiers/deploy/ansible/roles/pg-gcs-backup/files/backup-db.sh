#!/bin/sh

BACKUP_FILENAME="db-backup-$(date +"%Y%m%d-%H%M%S").gz"

TMPFILE=$(mktemp --suffix ".gz")
pg_dumpall | gzip > "$TMPFILE"
mv "$TMPFILE" "/tmp/$BACKUP_FILENAME"
gsutil -o "Credentials:gs_service_key_file=/etc/gcp/account.json" cp "/tmp/$BACKUP_FILENAME" "gs://livectf-backups"
rm "/tmp/$BACKUP_FILENAME"
