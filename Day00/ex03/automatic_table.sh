#!/bin/bash

# Directory containing the CSV files
CSV_DIR="/path/to/customer"

# Loop through all CSV files in the directory
for csv_file in "$CSV_DIR"/*.csv; do
    # Extract the base name of the file (without the directory and extension)
    table_name=$(basename "$csv_file" .csv)
    
    # Create the table using the extracted name
    echo "Creating table: $table_name"
    
    # Assuming you have a command or script to create the table from the CSV
    # Replace 'create_table_command' with the actual command you use
    create_table_command "$csv_file" "$table_name"
done