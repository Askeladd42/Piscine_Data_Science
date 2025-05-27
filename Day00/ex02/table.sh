#!/bin/bash
# this is not a real script, just a list of command that will be done
# in the terminal for the creation of the table in the Postgres database

### table creation in the Postgres database
CREATE TABLE IF NOT EXISTS data_2022_oct (
    event_time TIMESTAMP,
    event_type VARCHAR(255),
    product_id INT,
    price FLOAT,
    user_id BIGINT,
    user_session UUID
);

### Copy data from the CSV file to the table
\copy data_2022_oct FROM '/data/data_2022_oct.csv' DELIMITER ',' CSV HEADER;