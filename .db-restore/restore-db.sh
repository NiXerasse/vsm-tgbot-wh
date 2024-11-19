#!/bin/bash
set -e

echo "Checking if database restoration is required..."

if [ -n "${DB_RESTORE_FROM_FILE}" ]; then
  if [ -f "/docker-entrypoint-initdb.d/${DB_RESTORE_FROM_FILE}" ]; then
    echo "Restoring database from file: ${DB_RESTORE_FROM_FILE}"
    psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB" < "/docker-entrypoint-initdb.d/${DB_RESTORE_FROM_FILE}"
    echo "Database restored successfully."
  else
    echo "Warning: File specified in DB_RESTORE_FROM_FILE does not exist: /docker-entrypoint-initdb.d/${DB_RESTORE_FROM_FILE}"
    echo "Skipping database restoration. The database will be initialized as empty."
  fi
else
  echo "No restoration file specified. The database will be initialized as empty."
fi
