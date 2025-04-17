#!/bin/bash

# Load environment variables from test.env, to modify if necessary
set -o allexport
source ../../test.env
set +o allexport

# Directory containing the CSV files
CSV_DIR="../../../ressources/Piscine_Data_Science"

# Table name for the joined data
joined_table="customers"

# Create the "customers" table
echo "Creating table: $joined_table"        # message to inform the user of the creation of the table
docker exec -it "$DB_CONTAINER" psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "
DROP TABLE IF EXISTS \"$joined_table\";
CREATE TABLE \"$joined_table\" AS
SELECT * FROM data_2022_oct LIMIT 0;"  # Create the structure of the table based on one of the existing tables

# Loop through all tables matching the pattern "data_202*_***"
echo "Joining tables into: $joined_table"
for table in $(psql -h "$POSTGRES_DB" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" -d "$POSTGRES_NAME" -t -c "
SELECT table_name FROM information_schema.tables WHERE table_name LIKE 'data_202%';"); do
    echo "Adding data from table: $table"
    "$DB_CONTAINER" psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "
    INSERT INTO \"$joined_table\" SELECT * FROM \"$table\";"
done

echo "All tables joined into: $joined_table" # message to inform the user of the end of the process