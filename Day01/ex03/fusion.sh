#!/bin/bash

set -o allexport
source /home/plam/sgoinfre/test.env     # Adjust the path as necessary
set +o allexport

table_name="customers"

# Add columns to the customers table if they do not exist
DB_CONTAINER="postgres_db"

echo "Adding columns to the $table_name table if they do not exist"
for col in "category_id BIGINT" "category_code VARCHAR(255)" "brand VARCHAR(255)"; do
    name=$(echo $col | cut -d' ' -f1)
    type=$(echo $col | cut -d' ' -f2-)
    docker exec -i "$DB_CONTAINER" psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "
    DO \$\$
    BEGIN
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_name = '$table_name' AND column_name = '$name'
        ) THEN
            ALTER TABLE \"$table_name\" ADD COLUMN $name $type;
        END IF;
    END
    \$\$;"
done

echo "Verifying if the rows in the items table are unique based on product_id"
duplicates=$(docker exec -i "$DB_CONTAINER" psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -t -A -c "
SELECT product_id FROM items GROUP BY product_id HAVING COUNT(*) > 1;
")

if [ -n "$duplicates" ]; then
    echo "WARNING: duplicates product_id found in the items table:"
    echo "$duplicates"
else
    echo "All product_id in the items table are unique."
fi

echo "Verifying if the duplicates in the items table have different values for category_id, category_code, and brand"
diff_duplicates=$(docker exec -i "$DB_CONTAINER" psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -t -A -c "
SELECT product_id
FROM items
GROUP BY product_id
HAVING COUNT(*) > 1
   AND COUNT(DISTINCT (category_id, category_code, brand)) > 1;
")

if [ -n "$diff_duplicates" ]; then
    echo "WARNING: Some duplicates in the items table have different values for category_id, category_code, and brand !"
else
    echo "All duplicates in the items table have the same values for category_id, category_code, and brand."
fi

# Create a "temporary" table items_nodup to hold unique product_id entries
echo "Creating a temporary table items_nodup to hold unique product_id entries"
docker exec -i "$DB_CONTAINER" psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "
DROP TABLE IF EXISTS items_nodup;
CREATE TABLE items_nodup AS
SELECT DISTINCT ON (product_id) *
FROM items
ORDER BY product_id;
"

# Update with items_nodup table
echo "Updating the $table_name table with data from the items table (no duplicates)"
docker exec -i "$DB_CONTAINER" psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "
UPDATE \"$table_name\" AS c
SET
    category_id = i.category_id,
    category_code = i.category_code,
    brand = i.brand
FROM items_nodup i
WHERE c.product_id = i.product_id;
"

# Cleaning up the temporary items_nodup table
echo "Cleaning up the temporary items_nodup table"
docker exec -i "$DB_CONTAINER" psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "DROP TABLE IF EXISTS items_nodup;"

echo "Fusion of the $table_name table with the items table completed"