from typing import Dict

if 'data_loader' not in globals():
    from mage_ai.data_preparation.decorators import data_loader
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test
from pandas import DataFrame
import pandas as pd

@data_loader
def load_data_from_api(data: Dict, *args, **kwargs) -> DataFrame:
    """
    Template for loading data from API
    """
    url = data['url']

    taxi_dtypes = {
            'VendorID': pd.Int64Dtype(),
            'passenger_count': pd.Int64Dtype(),
            'trip_distance': float,
            'RatecodeID':pd.Int64Dtype(),
            'store_and_fwd_flag':str,
            'PULocationID':pd.Int64Dtype(),
            'DOLocationID':pd.Int64Dtype(),
            'payment_type': pd.Int64Dtype(),
            'fare_amount': float,
            'extra':float,
            'mta_tax':float,
            'tip_amount':float,
            'tolls_amount':float,
            'ehail_fee':float,
            'improvement_surcharge':float,
            'payment_type':pd.Int64Dtype(),
            'total_amount':float,
            'trip_type':pd.Int64Dtype(),
            'congestion_surcharge':float
            }

    parse_dates = ['lpep_pickup_datetime', 'lpep_dropoff_datetime']
    
    return pd.read_csv(url, sep=',', compression="gzip", dtype=taxi_dtypes, parse_dates=parse_dates)


@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, 'The output is undefined'
