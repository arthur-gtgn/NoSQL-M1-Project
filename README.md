# NoSQL Project - Getting familiar with Cassandra

## Project Overview

The aim of this project is to get familiar with Cassandra, a NoSQL database, by working with a dataset of companies. The dataset contains information about various companies, including their names, categories, descriptions, and acquisition details.
## Part 1: data cleaning and basic querries

I have produced two python scripts that allow to clean the data and generate a script that will automatically create the tables in Cassandra and insert the data.

How to run `clean_dataset.py`:
1. Make sure you have Python installed on your machine.
2. `python clean_dataset.py <path_to_your_data>` (for now please use the `companies2.json` file).

How to run `json_to_cql.py`:
1. Run `python json_to_cql.py` - Make sure you have the `companies2.json` file in the same directory.
2. This will generate a `insert_companies.cql` file that contains the CQL commands to create the tables and insert the data. Add the following lines to the beginning of the file:
   ```
   CREATE KEYSPACE IF NOT EXISTS PROJECT WITH REPLICATION ={'class': 'SimpleStrategy', 'replication_factor':1};
    USE PROJECT;

    CREATE TABLE companies (
        permalink text PRIMARY KEY,
        name text,
        category_code text,
        description text,
        homepage_url text,
        founded_year int,
        founded_month int,
        founded_day int,
        deadpooled_year int,
        deadpooled_month int,
        deadpooled_day int,
        number_of_employees int,
        email_address text,
        phone_number text,
        total_money_raised text,
        overview text,
        twitter_username text,
        acquisition_price_amount decimal,
        acquisition_acquired_year int,
        acquisition_acquired_month int,
        acquisition_acquired_day int,
        acquisition_acquiring_company text
    );
   ```

How to connect to Cassandra and run the CQL commands:
1. Make sure you have a running Cassandra docker container.
2. Transfer the `insert_companies.cql` file to the container using:
   ```
   docker cp insert_companies.cql <container_id>:/
   ```
3. Connect to the Cassandra container:
   ```
   docker exec -it <container_name_or_id> /bin/bash
   ```
4. Run the CQL commands:
   ```
   cqlsh -f /insert_companies.cql
   ```
5. Check that the data has been inserted correctly by running:
   ```
   SELECT * FROM PROJECT.companies LIMIT 10;
   ```


