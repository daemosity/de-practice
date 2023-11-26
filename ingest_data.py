# install necessary libraries, import pandas
# pip install pandas
# !pip install SQLAlchemy
# !pip install psycopg2
# !pip install pyarrow
# !pip install fastparquet

import os
import argparse
from time import time
import pandas as pd
from sqlalchemy import create_engine

def main(params):
    user = params.user
    password = params.password
    host = params.host
    port = params.port
    db = params.db
    table_name = params.table_name
    url = params.url
    parquet_name = 'output.parquet'

    os.system(f"wget {url} -O {parquet_name}")
    # download the csv
    # Create connection to postgres so pandas knows to put it in a DDL format that'll work for postgres
    engine = create_engine(f'postgresql://{user}:{password}@{host}:{port}/{db}')

    # read in ny_yellow_taxi data from 2021, adjust datatypes for pandas to detect proper DLL format
    # setting up file to read file into dataframe one chunk at a time
    df_iter = pd.read_parquet(parquet_name, iterator=True, chunksize=100000)

    # take first batch and correct datatypes
    df = next(df_iter)

    df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
    df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)
    df.passenger_count = (df.passenger_count).fillna(0).astype(int)

    # create table using just the dataFrame headers
    df.head(n=0).to_sql(name=table_name, con=engine, if_exists='replace')

    # read in the first 100000 rows
    df.to_sql(name=table_name, con=engine, if_exists='append')

    # read in the rest of the dataFrame, ending after df reads in less than 100000 rows
    while len(df) == 100000:
        t_start = time()
        
        df = next(df_iter)
        
        df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
        df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)
        df.passenger_count = (df.passenger_count).fillna(0).astype(int)

        df.to_sql(name=table_name, con=engine, if_exists='append')

        t_end = time()

        print('inserted another chunk..., took %.3f second(s)' % (t_end - t_start))


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Ingest CSV data to Postgres')

    # user, password, host, port, database name, table name
    # url of the csv
    parser.add_argument('user', help='username for postgres')
    parser.add_argument('password', help='password for postgres')
    parser.add_argument('host', help='host for postgres')
    parser.add_argument('port', help='port for postgres')
    parser.add_argument('db', help='database name for postgres')
    parser.add_argument('table-name', help='name of the table where we will write the results to')
    parser.add_argument('url', help='url of the csv file')

    args = parser.parse_args()
    main(args)