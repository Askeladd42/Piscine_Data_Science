#!/bin/bash

# Load environment file
set -o allexport
source /home/plam/sgoinfre/test.env    # Adjust the path to your .env file
set +o allexport

# Table name
table_name="customers"

# Remove duplicate rows from the "customers" table
echo "Removing duplicate rows from table: $table_name"
docker exec -it "$DB_CONTAINER" psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "
DELETE FROM \"$table_name\"
WHERE ctid NOT IN (                                     # ctid is a system column that uniquely identifies rows in a table
    SELECT MIN(ctid)
    FROM \"$table_name\"
    GROUP BY *
);"

echo "Duplicate rows removed from table: $table_name"