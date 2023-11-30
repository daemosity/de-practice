FROM python:3.9.1

# Installing wget to download parquet file
RUN apt-get install wget

# installing psycopg2, as it is a postgres db adapter for python: SQLalchemy needs it
# installing pyarrow to ingest parquet files
RUN pip install pandas SQLAlchemy psycopg2 pyarrow fastparquet

WORKDIR /app
COPY ingest_data.py ingest_data.py

ENTRYPOINT [ "python", "ingest_data.py" ]