from typing import Dict, List

@data_loader
def load_data(*args, **kwargs) -> List[List[Dict]]:
    links = [dict(url=link) for link in [
                                "https://github.com/DataTalksClub/nyc-tlc-data/releases/download/green/green_tripdata_2020-10.csv.gz",
                                "https://github.com/DataTalksClub/nyc-tlc-data/releases/download/green/green_tripdata_2020-11.csv.gz",
                                "https://github.com/DataTalksClub/nyc-tlc-data/releases/download/green/green_tripdata_2020-12.csv.gz"
                                ]
            ]
    metadata = [dict(block_uuid=f"green_taxi_data_2020-{ month }") for month in range(10, 13)]

    return [
        links,
        metadata,
    ]


@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, 'The output is undefined'

@test
def test_dtypes(output, *args) -> None:
    """
    Test to ensure that the output is correct for a dynamic block
    """
    assert isinstance(output, list), "The outer layer is not a list"
    assert all([isinstance(dct, dict) for dct in output]), "The inner layer does not contain dictionaries"