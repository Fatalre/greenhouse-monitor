#!/usr/bin/env sh
set -eu
FILE=${1:?Usage: restore.sh backups/file.sql.gz}
gzip -dc "$FILE" | docker compose -f docker-compose.production.yml exec -T postgres   psql -U "$POSTGRES_USER" "$POSTGRES_DB"
