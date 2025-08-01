#!/bin/bash

# Load environment variables from test.env
set -o allexport
source /home/plam/sgoinfre/test.env     # Adjust the path as necessary
set +o allexport

table_name="customers"
batch_size=10000    # batch treatment size because of the size of the table

# Get columns except event_time (quoted, comma-separated)
echo "Fetching columns for table: $table_name"
columns=$(docker exec -i "$DB_CONTAINER" psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -t -A -c \
    "SELECT string_agg(quote_ident(column_name), ', ') FROM information_schema.columns WHERE table_name = '$table_name' AND column_name <> 'event_time';")

if [ -z "$columns" ]; then
    echo "No columns found for table $table_name. Aborting."
    exit 1
fi

# Build index columns (unquoted, comma-separated)
echo "Building index columns for table: $table_name"
index_columns=$(docker exec -i "$DB_CONTAINER" psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -t -A -c \
    "SELECT string_agg(column_name, ', ') FROM information_schema.columns WHERE table_name = '$table_name' AND column_name <> 'event_time';")

# Create functional index for deduplication
docker exec -i "$DB_CONTAINER" psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c \
    "CREATE INDEX IF NOT EXISTS idx_customers_dedup ON \"$table_name\" ($index_columns, date_trunc('second', event_time));"

# Remove near-duplicate rows based on all columns except event_time
# ctid is used to uniquely identify rows in PostgreSQL

echo "Counting rows with near-duplicates (identical except event_time <= 1s apart) in table: $table_name"
docker exec -i "$DB_CONTAINER" psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "
SELECT COUNT(*) FROM (
    SELECT
        *,
        LAG(event_time) OVER (
            PARTITION BY $columns
            ORDER BY event_time
        ) AS prev_event_time
    FROM \"$table_name\"
) t
WHERE prev_event_time IS NOT NULL
  AND abs(EXTRACT(EPOCH FROM (event_time - prev_event_time))) <= 1;"

# Prepare the COALESCE statement for handling ANY NULL-type values for patitioning
echo "Preparing COALESCE statement for NULL handling in table: $table_name"
coalesce_columns=$(docker exec -i "$DB_CONTAINER" psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -t -A -c "
SELECT string_agg(
    CASE data_type
        WHEN 'integer' THEN 'COALESCE(' || quote_ident(column_name) || ', -1)'
        WHEN 'bigint' THEN 'COALESCE(' || quote_ident(column_name) || ', -1)'
        WHEN 'double precision' THEN 'COALESCE(' || quote_ident(column_name) || ', -1)'
        WHEN 'numeric' THEN 'COALESCE(' || quote_ident(column_name) || ', -1)'
        WHEN 'real' THEN 'COALESCE(' || quote_ident(column_name) || ', -1)'
        WHEN 'uuid' THEN 'COALESCE(' || quote_ident(column_name) || ',''00000000-0000-0000-0000-000000000000'')'
        WHEN 'character varying' THEN 'COALESCE(' || quote_ident(column_name) || ',''__NULL__'')'
        WHEN 'text' THEN 'COALESCE(' || quote_ident(column_name) || ',''__NULL__'')'
        WHEN 'date' THEN 'COALESCE(' || quote_ident(column_name) || ',''1900-01-01'')'
        WHEN 'timestamp without time zone' THEN 'COALESCE(' || quote_ident(column_name) || ',''1900-01-01 00:00:00'')'
        ELSE 'COALESCE(' || quote_ident(column_name) || ',''__NULL__'')'
    END, ', '
)
FROM information_schema.columns
WHERE table_name = '$table_name' AND column_name <> 'event_time';
")

echo "Removing strict duplicates (all columns including event_time)..."
while :; do
    deleted=$(docker exec -i "$DB_CONTAINER" psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -t -A -c "
        WITH to_delete AS (
            SELECT ctid FROM (
                SELECT
                    ctid,
                    ROW_NUMBER() OVER (
                        PARTITION BY $coalesce_columns, event_time
                        ORDER BY event_time
                    ) AS rn
                FROM \"$table_name\"
            ) t
            WHERE t.rn > 1
            LIMIT $batch_size
        )
        DELETE FROM \"$table_name\" WHERE ctid IN (SELECT ctid FROM to_delete)
        RETURNING 1;
    " | grep '^1$' | wc -l)
    if [ "$deleted" -eq 0 ]; then break; fi
    echo "Deleted $deleted strict duplicate rows in this batch..."
done

echo "Removing near-duplicates (identical except event_time < 1s apart)..."
while :; do
    deleted=$(docker exec -i "$DB_CONTAINER" psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -t -A -c "
        WITH to_delete AS (
            SELECT ctid FROM (
                SELECT
                    ctid,
                    ROW_NUMBER() OVER (
                        PARTITION BY $coalesce_columns
                        ORDER BY event_time
                    ) AS rn,
                    event_time,
                    LAG(event_time) OVER (
                        PARTITION BY $coalesce_columns
                        ORDER BY event_time
                    ) AS prev_event_time
                FROM \"$table_name\"
            ) t
            WHERE t.rn > 1 AND abs(EXTRACT(EPOCH FROM (event_time - prev_event_time))) <= 1
            LIMIT $batch_size
        )
        DELETE FROM \"$table_name\" WHERE ctid IN (SELECT ctid FROM to_delete)
        RETURNING 1;
    " | grep '^1$' | wc -l)
    if [ "$deleted" -eq 0 ]; then break; fi
    echo "Deleted $deleted near-duplicate rows in this batch..."
done

# Final count of rows after deduplication
echo "Counting rows with near-duplicates (identical except event_time <= 1s apart) in table: $table_name"
docker exec -i "$DB_CONTAINER" psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "
SELECT COUNT(*) FROM (
    SELECT
        *,
        LAG(event_time) OVER (
            PARTITION BY $columns
            ORDER BY event_time
        ) AS prev_event_time
    FROM \"$table_name\"
) t
WHERE prev_event_time IS NOT NULL
  AND abs(EXTRACT(EPOCH FROM (event_time - prev_event_time))) <= 1;"

echo "All near-duplicate rows removed from table: $table_name"

# delete the index created for deduplication
echo "Dropping index idx_customers_dedup from table: $table_name"
docker exec -i "$DB_CONTAINER" psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c \
    "DROP INDEX IF EXISTS idx_customers_dedup;"