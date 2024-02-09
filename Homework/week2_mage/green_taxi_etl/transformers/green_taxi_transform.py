from typing import List

from mage_ai.data_cleaner.transformer_actions.base import BaseAction
from mage_ai.data_cleaner.transformer_actions.constants import ActionType, Axis
from mage_ai.data_cleaner.transformer_actions.utils import build_transformer_action
from pandas import DataFrame

if 'transformer' not in globals():
    from mage_ai.data_preparation.decorators import transformer
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test


@transformer
def execute_transformer_action(df: DataFrame, *args, **kwargs) -> List:
    """
    Execute Transformer Action: ActionType.CLEAN_COLUMN_NAME

    Docs: https://docs.mage.ai/guides/transformer-blocks#clean-column-names
    """
    
    df = df.fillna(0)
    
    df = df.loc[(df['passenger_count'] > 0) & (df['trip_distance'] > 0)]
    
    df['lpep_pickup_date'] = df['lpep_pickup_datetime'].dt.date

    df.columns = df.columns.map(lambda x: 
                                    ''.join([ 
                                        f"_{ char.lower() }" 
                                        if all([(idx > 0), (idx < (len(x) - 1)), char.isupper()]) 
                                        else char.lower() 
                                        for idx, char in enumerate(x)
                                        ])
                                )

    return [df]
                                
@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, 'The output is undefined'

@test
def test_snake_case(output, *args) -> None:
    assert 'vendor_id' in output.columns, "VendorID was not properly transformed"

@test
def test_passengers_not_zero(output, *args) -> None:
    assert (output['passenger_count'] <= 0).sum() == 0, "Rides exist without passengers"

@test
def test_trip_distance_not_zero(output, *args) -> None:
    assert (output['trip_distance'] <= 0).sum() == 0, "Rides exist that do not go any distance"