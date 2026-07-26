#!/usr/bin/env sh
set -eu
mkdir -p backups
STAMP=$(date +%Y%m%d-%H%M%S)
docker compose -f docker-compose.production.yml exec -T postgres   pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB" | gzip > "backups/greenhouse-$STAMP.sql.gz"
echo "Created backups/greenhouse-$STAMP.sql.gz"
