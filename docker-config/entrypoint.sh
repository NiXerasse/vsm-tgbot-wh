#!/bin/bash

if [ ! -f "/docker-entrypoint-initdb.d/init.sql" ]; then
  echo "Подставляем значения из переменных окружения в init.sql.template..."
  envsubst < /docker-entrypoint-initdb.d/init.sql.template > /docker-entrypoint-initdb.d/init.sql
  echo "init.sql создан:"
  cat /docker-entrypoint-initdb.d/init.sql
fi

exec docker-entrypoint.sh "$@"
