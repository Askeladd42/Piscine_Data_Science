#!/bin/bash

# Load environment variables from test.env, to modify if necessary
set -o allexport
source ../../test.env
set +o allexport

# Directory containing the CSV file
CSV_DIR="../../ressources/Piscine_DataScience/D00/items"

# Database connection details, to be deleted when using the .env later on
# DB_NAME="postgres_db"
# DB_USER="plam"
# DB_HOST="piscineds"
# DB_PORT="5432"

# CSV file path
csv_file="$CSV_DIR/items.csv"

# Table name
table_name="items"

# Create the table using the extracted name
echo "Creating table: $table_name"
psql -h "$POSTGRES_DB" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" -d "$POSTGRES_NAME" -c "
CREATE TABLE IF NOT EXISTS \"$table_name\" (
    product_id INT,
    category_id BIGINT,
    category_code VARCHAR(255),
    brand VARCHAR(255)
);"

# Copy data from the CSV file to the table
echo "Copying data to table: $table_name"
psql -h "$POSTGRES_DB" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" -d "$POSTGRES_NAME" -c "
COPY \"$table_name\" FROM '$csv_file' DELIMITER ',' CSV HEADER;"