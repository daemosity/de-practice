# install necessary libraries, import pandas
# pip install pandas
# !pip install SQLAlchemy
# !pip install psycopg2
# !pip install pyarrow
# !pip install fastparquet

import os
from time import time
import pandas as pd
import pyarrow.parquet as pq
from sqlalchemy import create_engine
from prefect import flow, task
from prefect.tasks import task_input_hash
from datetime import timedelta
from prefect_sqlalchemy import SqlAlchemyConnector

@task(log_prints = True, retries=3, cache_key_fn=task_input_hash, cache_expiration=timedelta(days = 1), timeout_seconds = 60)
def extract_data(url: str) -> None:
    # the backup files are gzipped, and it's important to keep the correct extension
    # for pandas to be able to open the file
    if url.endswith('.csv.gz'):
        outfile_name = 'yellow_tripdata_2019-01.csv.gz'
    elif url.endswith('.parquet'):
        outfile_name = 'output.parquet'
    else:
        outfile_name = 'output.csv'
    
    # download the csv
    os.system(f"wget {url} -O {outfile_name}")
    return outfile_name

@task(log_prints=True)
def transform_data(df):
    """ 
    changes datatype of pickup and dropoffs to datetime
    logs all rides that were logged as having no passengers, then removes them (though this might be worth looking at later)
    """
    print(f"pre: missing passenger count: {df['passenger_count'].isin([0]).sum()}")
    df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
    df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)
    new_df = df[~df['passenger_count'].isin([0])]
    print(f"post: missing passenger count: {new_df['passenger_count'].isin([0]).sum()}")

    return new_df

@flow(log_prints=True)
def ingest_data(outfile_name, table_name):
    """
    Read in the dataFrame
    """
    # read in csv in batches   
    batch_iter = pd.read_csv(outfile_name, iterator=True, chunksize = 100000, compression='gzip')
    df = next(batch_iter)
    cleaned_df = transform_data(df)

    connection_block = SqlAlchemyConnector.load("sqlalch-connect")
    with connection_block.get_connection(begin=False) as engine:
        cleaned_df.head(n=0).to_sql(name=table_name, con=engine, if_exists='replace')
        cleaned_df.to_sql(name=table_name, con=engine, if_exists='append') 
        print('table [{table_name}] primed')

        while len(df) == 100000:
            t_start = time()
            df = next(batch_iter)
            cleaned_df = transform_data(df) 
            cleaned_df.to_sql(name=table_name, con=engine, if_exists='append')
            t_end = time()
            print('inserted another chunk..., took %.3f second(s)' % (t_end - t_start))

        print('upload finished')

@flow(name='Ingest Flow')
def main_flow():
    table_name = "yellow_taxi_trips"
    csv_url = "https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/yellow_tripdata_2019-01.csv.gz"

    outfile_name = extract_data(url = csv_url)
    ingest_data(outfile_name, table_name)
    

if __name__ == '__main__':
    main_flow()