#!/bin/bash

# Load environment file
set -o allexport
source /home/plam/sgoinfre/test.env    # Adjust the path to your .env file
set +o allexport

# Table name
table_name="customers"

# Fusion of the "customers" table with the "items" table in the "customers" table
echo "Fusion of the $table_name table with the items table"
docker exec -it "$DB_CONTAINER" psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "
UPDATE \"$table_name\"
SET items = (
    SELECT items
    FROM items
    WHERE items.id = \"$table_name\".items_id
);

echo "Fusion of the $table_name table with the items table completed"