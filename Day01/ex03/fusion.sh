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

echo "Verifying if the rows in the $table_name table are unique based on product_id"
duplicates=$(docker exec -i "$DB_CONTAINER" psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -t -A -c "
SELECT product_id FROM items GROUP BY product_id HAVING COUNT(*) > 1;
")

if [ -n "$duplicates" ]; then
    echo "WARNING: duplicates product_id found in the items table:"
    echo "$duplicates"
else
    echo "Aucun doublon de product_id trouvé dans la table items."
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
    echo "ATTENTION : Certains product_id ont des valeurs différentes dans items !"
    echo "$diff_duplicates"
else
    echo "Tous les doublons de product_id sont identiques sur toutes les colonnes."
fi

echo "Creating a temporary table items_nodup to remove duplicates based on product_id and keep the first occurrence"
docker exec -i "$DB_CONTAINER" psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "
DROP TABLE IF EXISTS items_nodup;
CREATE TEMP TABLE items_nodup AS
SELECT DISTINCT ON (product_id) *
FROM items
ORDER BY product_id;
"

# Update the customers table with data from the items_nodup table
echo "Updating the $table_name table with data from the items table (sans doublons)"
docker exec -i "$DB_CONTAINER" psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "
UPDATE \"$table_name\" AS c
SET
    category_id = i.category_id,
    category_code = i.category_code,
    brand = i.brand
FROM items_nodup i
WHERE c.product_id = i.product_id;
"
echo "Fusion of the $table_name table with the items table completed"