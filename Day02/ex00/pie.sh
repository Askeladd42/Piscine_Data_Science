#!/bin/bash

# Load environment file
set -o allexport
source ../../test.env
set +o allexport

# Table name
table_name="customers"

# create a pie chart of the customers table
echo "Creating a pie chart of the $table_name table"
psql -h "$POSTGRES_DB" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" -d "$POSTGRES_NAME" -c "
SELECT items, COUNT(*) as count
FROM \"$table_name\"
GROUP BY items
ORDER BY count DESC
LIMIT 10
\gplot 'pie_chart.png' using 2:1 with pie title 'Top 10 items in $table_name'
echo "Pie chart of the $table_name table created"