#!/bin/bash

# Load environment variables from test.env
set -o allexport
source /home/plam/sgoinfre/test.env
set +o allexport

# Table name for the joined data
joined_table="customers"

# Crée la table "customers" with the first table found structure
first_table=$(docker exec -i "$DB_CONTAINER" psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -t -A -c \
    "SELECT table_name FROM information_schema.tables WHERE table_name LIKE 'data_202%_' ORDER BY table_name LIMIT 1;")

echo "Creating table: $joined_table"
docker exec -i "$DB_CONTAINER" psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "
DROP TABLE IF EXISTS \"$joined_table\";
CREATE TABLE \"$joined_table\" AS SELECT * FROM \"$first_table\" LIMIT 0;"

# Loop through all matching tables and insert data
tables=$(docker exec -i "$DB_CONTAINER" psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -t -A -c \
    "SELECT table_name FROM information_schema.tables WHERE table_name LIKE 'data_202%_';")

for table in $tables; do
    echo "Adding data from table: $table"
    docker exec -i "$DB_CONTAINER" psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c \
        "INSERT INTO \"$joined_table\" SELECT * FROM \"$table\";"
done

echo "All tables joined into: $joined_table"