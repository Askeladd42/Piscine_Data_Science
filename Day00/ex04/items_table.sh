#!/bin/bash

# Load environment variables from test.env, to modify if necessary
set -o allexport
source /home/plam/sgoinfre/test.env    # Adjust the path to your .env file
set +o allexport

# Directory containing the CSV file
CSV_DIR="../../../subject/item"    # Adjust the path to your CSV files

# Database container name
DB_CONTAINER="postgres_db"

# CSV file path
csv_file="$CSV_DIR/item.csv"

# Table name
table_name="items"

# Create the table using the extracted name
echo "Creating table: $table_name"
docker exec -it "$DB_CONTAINER" psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "
CREATE TABLE IF NOT EXISTS \"$table_name\" (
    product_id INT,
    category_id BIGINT,
    category_code VARCHAR(255),
    brand VARCHAR(255)
);"

# Copy data from the CSV file to the table
echo "Copying data to table: $table_name"
docker cp "$csv_file" "$DB_CONTAINER:/tmp/$(basename "$csv_file")"
docker exec -it "$DB_CONTAINER" psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "
COPY \"$table_name\" FROM '/tmp/$(basename "$csv_file")' DELIMITER ',' CSV HEADER;"
