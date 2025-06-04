#!/bin/bash

# Load environment variables from test.env
set -o allexport
source /home/plam/sgoinfre/test.env     # Adjust the path as necessary
set +o allexport

table_name="customers"

# Get columns except event_time
columns=$(docker exec -i "$DB_CONTAINER" psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -t -A -c \
    "SELECT string_agg(quote_ident(column_name), ', ') FROM information_schema.columns WHERE table_name = '$table_name' AND column_name <> 'event_time';")

if [ -z "$columns" ]; then
    echo "No columns found for table $table_name. Aborting."
    exit 1
fi

# Remove near-duplicate rows based on all columns except event_time
# ctid is used to uniquely identify rows in PostgreSQL

echo "Removing near-duplicate rows from table: $table_name"
docker exec -i "$DB_CONTAINER" psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "
DELETE FROM \"$table_name\"
WHERE ctid IN (
    SELECT ctid FROM (
        SELECT
            ctid,
            ROW_NUMBER() OVER (
                PARTITION BY $columns, date_trunc('second', event_time)
                ORDER BY event_time
            ) AS rn
        FROM \"$table_name\"
    ) t
    WHERE t.rn > 1
);"

echo "Near-duplicate rows removed from table: $table_name"