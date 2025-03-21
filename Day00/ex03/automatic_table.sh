#!/bin/bash

# Directory containing the CSV files, to modify with the correct path
CSV_DIR="../../ressources/Piscine_DataScience/subject_D00/customer"

# Loop through all CSV files in the directory
for csv_file in "$CSV_DIR"/*.csv; do
    # Extract the base name of the file (without the directory and extension)
    table_name=$(basename "$csv_file" .csv)
    
    # Create the table using the extracted name
    echo "Creating table: $table_name"
    
    # Assuming you have a command or script to create the table from the CSV
    # Replace 'create_table_command' with the actual command you use
    CREATE TABLE "$table_name" (
        event_time TIMESTAMP,
        event_type VARCHAR(255),
        product_id INT,
        price FLOAT,
        user_id BIGINT,
        user_session UUID
    )

    # Copy data from the CSV file to the table
    echo "Copying data to table: $table_name"
    COPY "$table_name" FROM "$csv_file" DELIMITER ',' CSV HEADER
done