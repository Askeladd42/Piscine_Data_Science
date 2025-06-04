#!/bin/bash

# Load environment variables from test.env
set -o allexport
source /home/plam/sgoinfre/test.env     # Adjust the path as necessary
set +o allexport

table_name="customers"
batch_size=10000    # batch treatment size because of the size of the table

# Get columns except event_time (quoted, comma-separated)
columns=$(docker exec -i "$DB_CONTAINER" psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -t -A -c \
    "SELECT string_agg(quote_ident(column_name), ', ') FROM information_schema.columns WHERE table_name = '$table_name' AND column_name <> 'event_time';")

if [ -z "$columns" ]; then
    echo "No columns found for table $table_name. Aborting."
    exit 1
fi

# Build index columns (unquoted, comma-separated)
index_columns=$(docker exec -i "$DB_CONTAINER" psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -t -A -c \
    "SELECT string_agg(column_name, ', ') FROM information_schema.columns WHERE table_name = '$table_name' AND column_name <> 'event_time';")

# Create functional index for deduplication
docker exec -i "$DB_CONTAINER" psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c \
    "CREATE INDEX IF NOT EXISTS idx_customers_dedup ON \"$table_name\" ($index_columns, date_trunc('second', event_time));"

# Remove near-duplicate rows based on all columns except event_time
# ctid is used to uniquely identify rows in PostgreSQL

echo "Removing near-duplicate rows from table: $table_name"
while :; do
    deleted=$(docker exec -i "$DB_CONTAINER" psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -t -A -c "
        WITH to_delete AS (
            SELECT ctid
            FROM (
                SELECT
                    ctid,
                    ROW_NUMBER() OVER (
                        PARTITION BY $columns, date_trunc('second', event_time)
                        ORDER BY event_time
                    ) AS rn
                FROM \"$table_name\"
            ) t
            WHERE t.rn > 1
            LIMIT $batch_size
        )
        DELETE FROM \"$table_name\" WHERE ctid IN (SELECT ctid FROM to_delete)
        RETURNING 1;
    " | wc -l)

    if [ "$deleted" -eq 0 ]; then
        echo "No more duplicates to delete."
        break
    else
        echo "Deleted $deleted duplicate rows in this batch..."
    fi
done

echo "All near-duplicate rows removed from table: $table_name"

# delete the index created for deduplication
echo "Dropping index idx_customers_dedup from table: $table_name"
docker exec -i "$DB_CONTAINER" psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c \
    "DROP INDEX IF EXISTS idx_customers_dedup;"