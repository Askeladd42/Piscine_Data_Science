#!/bin/bash

set -o allexport
source /home/plam/sgoinfre/test.env     # Adjust the path as necessary
set +o allexport

table_name="customers"

# Ajoute les colonnes si elles n'existent pas déjà
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

# Met à jour customers avec les infos de items (jointure sur product_id)
docker exec -i "$DB_CONTAINER" psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "
UPDATE \"$table_name\" AS c
SET
    category_id = i.category_id,
    category_code = i.category_code,
    brand = i.brand
FROM items i
WHERE c.product_id = i.product_id;
"

echo "Fusion of the $table_name table with the items table completed"