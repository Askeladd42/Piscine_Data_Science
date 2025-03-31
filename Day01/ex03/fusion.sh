#!/bin/bash

# Load environment file
set -o allexport
source ../../test.env
set +o allexport

# Table name
table_name="customers"

# Fusion of the "customers" table with the "items" table in the "customers" table
echo "Fusion of the $table_name table with the items table"
psql -h "$POSTGRES_DB" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" -d "$POSTGRES_NAME" -c "
UPDATE \"$table_name\"
SET items = (
    SELECT items
    FROM items
    WHERE items.id = \"$table_name\".items_id
);

echo "Fusion of the $table_name table with the items table completed"