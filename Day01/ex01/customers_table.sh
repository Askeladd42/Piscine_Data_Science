#!/bin/bash

# Load environment variables from test.env, to modify if necessary
set -o allexport
source ../../test.env
set +o allexport

# Directory containing the CSV files
CSV_DIR="../../ressources/Piscine_DataScience/subject_D01/customer"

# Database connection details, to be deleted when using the .env later on
# DB_NAME="postgres_db"
# DB_USER="plam"
# DB_HOST="piscineds"
# DB_PORT="5432"