# %%
# install necessary libraries, import pandas
# pip install pandas
# !pip install SQLAlchemy
# !pip install psycopg2
import pandas as pd

# %%
# read in ny_yellow_taxi data from 2021, adjust datatypes for pandas to detect proper DLL format
df = pd.read_csv("yellow_tripdata_2021-01.csv.gz")

df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)
df.passenger_count = (df.passenger_count).fillna(0).astype(int)

# %%
# Create connection to postgres so pandas knows to put it in a DDL format that'll work for postgres
from sqlalchemy import create_engine
engine = create_engine('postgresql://root:root@localhost:5432/ny_taxi')

# %%
# print the postgres table layout
print(pd.io.sql.get_schema(df,name="yellow_taxi_data", con=engine))

# %%
# setting up file to read file into dataframe one chunk at a time
df_iter = pd.read_csv('yellow_tripdata_2021-01.csv.gz', iterator=True, chunksize=100000)

# %%
# take first batch and correct datatypes
df = next(df_iter)

df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)
df.passenger_count = (df.passenger_count).fillna(0).astype(int)

# create table using just the dataFrame headers
df.head(n=0).to_sql(name='yellow_taxi_data', con=engine, if_exists='replace')

# %%
# read in the first 100000 rows
df.to_sql(name='yellow_taxi_data', con=engine, if_exists='append')

# %%
# read in the rest of the dataFrame, ending after df reads in less than 100000 rows
from time import time
while len(df) == 100000:
    t_start = time()
    
    df = next(df_iter)
    
    df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
    df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)
    df.passenger_count = (df.passenger_count).fillna(0).astype(int)

    df.to_sql(name='yellow_taxi_data', con=engine, if_exists='append')

    t_end = time()

    print('inserted another chunk..., took %.3f second(s)' % (t_end - t_start))


