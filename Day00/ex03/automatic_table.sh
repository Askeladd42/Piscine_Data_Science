#!/bin/bash

# Load environment variables from test.env, to modify if necessary
set -o allexport
source ../../test.env
set +o allexport

# Directory containing the CSV files
CSV_DIR="../../../ressources/Piscine_Data_Science/customer"

# Database container name
DB_CONTAINER="postgres_db"

# Loop through all CSV files in the directory
for csv_file in "$CSV_DIR"/*.csv; do
    # Extract the base name of the file (without the directory and extension)
    table_name=$(basename "$csv_file" .csv)

    # Create the table using the extracted name
    echo "Creating table: $table_name"
    docker exec -it "$DB_CONTAINER" psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "
    CREATE TABLE IF NOT EXISTS \"$table_name\" (
        event_time TIMESTAMP,
        event_type VARCHAR(255),
        product_id INT,
        price FLOAT,
        user_id BIGINT,
        user_session UUID
    );"
    
    # Copy data from the CSV file to the table
    echo "Copying data to table: $table_name"
    docker cp "$csv_file" "$DB_CONTAINER:/tmp/$(basename "$csv_file")"
    docker exec -it "$DB_CONTAINER" psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "
    COPY \"$table_name\" FROM '/tmp/$(basename "$csv_file")' DELIMITER ',' CSV HEADER;"
done