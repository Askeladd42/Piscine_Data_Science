#!/bin/bash


### table creation in the Postgres database
CREATE TABLE data_2022_oct (
    event_time TIMESTAMP,
    event_type VARCHAR(255),
    product_id INT,
    price FLOAT,
    user_id BIGINT,
    user_session UUID
)

### Copy data from the CSV file to the table
COPY data_2022_oct FROM 'data_2022_oct.csv' DELIMITER ',' CSV HEADER