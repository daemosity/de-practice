# Data Ingestion With dlt Workshop Notes
## Ingesting data from APIs to Warehouses
Notes directly from: [DataTalks.Club's dlt workshop](https://github.com/DataTalksClub/data-engineering-zoomcamp/blob/main/cohorts/2024/workshops/dlt_resources/data_ingestion_workshop.md), taught by [Adrian Brudaru](https://www.linkedin.com/in/data-team/)

### Workshop focus:
Building robust, scalable, self maintaining pipelines with built in governance *(aka best practices applied)*
1. Extracting data from APIs, or files
2. Normalizing, cleaning and adding metadata (e.g. schema, types)
3. Incremental loading

## Data Loading/Ingestion
Data ingestion is the process of extracting data from a producer, transporting it to a convenient environment, and preparing it for usage by normalizing it, *sometimes cleaning*, and adding metadata

> **Schema**: specifies expected format and structure of data within a document or data store and defines:
> - allowed keys
> - data types
> - any constraints or relationships


The end format can be:
- structured with explicit schema
    - Allows immediate use
    - Example files: parquet, Avro, table in db
- weakly typed, without explicit schema
    -  Some extra normalization or cleaning may be needed before use
    - Example files: csv, json

A data engineer's goal is to ensure data flows from source systems to analytical destinations
- Builds, runs, and fixes pipelines
- Optimizes data storage
- Ensures data quality and integrity
- Implements effective data governance practices
- Continuously refines data architecture to meet the evolving needs of the organization

> Ultimately, a data engineer's role extends beyond mechanical aspects, encompassing strategic management and enhancement of the entire data lifecycle

## Extracting Data

Most data is stored behind an API. Sometimes that API is:
- a RESTful api, returning records of data
- returns a secure file path to a JSON or parquet file in a bucket, enabling bulk export
- a database/application returning records as JSON

> Engineers must build pipelines that "just work".
Therefore, to prevent pipelines from breaking and keep them running smoothly, they must consider:
- Hardware limits
    - Manage memory
- Network limits
    - Networks can fail; while that can't be fixed, can retry until success
    - Ex. dlt library offers a [requests "replacement" with built-in retries](https://dlthub.com/docs/reference/performance#using-the-built-in-requests-client)
- Source api limits
    - Each source may have *rate limits* (e.g. # of requests per second)
        - Look at each source's docs to understand how to navigate these obstacles
        - Examples of how to wait for rate limits:
            - [Zendesk](https://developer.zendesk.com/api-reference/introduction/rate-limits/)
            - [Shopify](https://shopify.dev/docs/api/usage/rate-limits)

### Dealing with hardware limits
On local machine or server, the only limits are memory (RAM or virtual memory) and storage (hard disk/SSD: physical storage)

#### Managing memory
Many pipelines run on serverless functions or on orchestrators that delegate the workloads of clusters of small workers
- These systems have a small memory and/or share it between multiple workers; filling memory is **BAD**
    - May lead to pipeline crashing
    - May crash entire container or virtual machine that might be shared with other worker processes, taking them down too
- Storage is usually enough, but occasionally it isn't. 
    - In the latter instance, mount an external drive mapped to a storage bucket
    - Example: Airflow supports a "data" folder used like a local folder but can be mapped to a bucket for unlimited capacity

##### Obstacles to overcome:
1. We often do not know the volume of data upfront
2. We cannot scale dynamically or infinitely on hardware during runtime

###### **Therefore: Control the max memory used**

#### How do we do this?

##### Streaming Data to Control Memory Use
> **Streaming**: processing the data event by event or chunk by chunk instead of doing bulk operations

Classic examples of streaming:
- Audio broadcaster --> in-browser audio player
- Server --> local video player
- Smart home device or IoT device --> phone
- Google Maps --> navigation app
- Instagram live --> followers

Data Engineers stream the data between buffers:
- API to local file
- Webhooks to event queues
- Event queues (Kafka, SQS) to buckets

To build most data pipelines:
> **python generators**: functions that can return multiple times
- This allows the data to be released as it's produced (as stream) instead of returning it all as a batch\
- Examples:
    - Searching twitter for #catpic
        - The number of pictures is initially unknown; may be from 1 to 1 million
        - The full result may not fit in memory or storage
    - To grab, we use a python generator

###### Transforming a regular returning function into a generator

Regular Returning function[^1]:
- Needs to download **all the data** before it returns the first record.

> ```python
> def search_twitter(query):
> 	data = []
> 	for row in paginated_get(query):
> 		data.append(row)
> 	return data
> 
> # Collect all the cat picture data
> for row in search_twitter("#catpic"):
>   # Once collected, 
>   # print row by row
> 	print(row)
> ```

> [!WARNING] 
> This function will break if more data exists than memory.

Function as a Generator[^1]:
>```py
>def search_twitter(query):
>	for row in paginated_get(query):
>		yield row
>
># Get one row at a time
>for row in extract_data("#catpic"):
>	# print the row
>	print(row)
>  # do something with the row such as cleaning it and writing it to a buffer
>	# continue requesting and printing data
>```

***Memory use is minimized***:
- Data is yielded, item by item, as the data arrives - *without collecting into memory*
    1. The function runs until the first data item in the queue is yielded, then stops
    2. The item is printed
    - Steps 1 & 2 are repeated until all data has been collected
- This still allows us to get all the values at once, if desired:
    - Just cast the generator as a list: ```data = list(extract_data("#catpic"))```
        - The generator runs until exhausted and places the result into a list

Three Extraction Examples:
-

> ### Example 1:
> Grabbing data from an API
> 
> **The bread and butter of data engineers**
><br></br>

The API:
Documentation:
- There are a limited # of records behind it
- Data can be requested page by page
- Each page contains 1,000 records
- Requesting a page with no data still yields a successful response ... with no data
    - i.e. page requests can be stopped when an empty page is yielded
    - This is a common way to paginate (but not the only one)

Details:
- method: ```get```
- url: ```https://us-central1-dlthub-analytics.cloudfunctions.net/data_engineering_zoomcamp_api```
- parameters: ```page: int```
    - Description: page # being requested
    - Default: 1

Requester design:
- Request page by page until all data has been retrieved
    - Remember: data size behind the API is unknown
    - Maybe 1,000 MB, maybe infinite PB

Design Pros/Cons:
- Pros: **Easy memory management** due to api returning events/pages
- Cons: **Low throughput** - data transfer constrained by an API

*Example 1 Code*[^1]

```py
import requests

BASE_API_URL = "https://us-central1-dlthub-analytics.cloudfunctions.net/data_engineering_zoomcamp_api"

# I call this a paginated getter
# as it's a function that gets data
# and also paginates until there is no more data
# by yielding pages, we "microbatch", which speeds up downstream processing

def paginated_getter():
    page_number = 1

    while True:
        # Set the query parameters
        params = {'page': page_number}

        # Make the GET request to the API
        response = requests.get(BASE_API_URL, params=params)
        response.raise_for_status()  # Raise an HTTPError for bad responses
        page_json = response.json()
        print(f'got page number {page_number} with {len(page_json)} records')

        # if the page has no records, stop iterating
        if page_json:
            yield page_json
            page_number += 1
        else:
            # No more data, break the loop
            break

if __name__ == '__main__':
    # Use the generator to iterate over pages
    for page_data in paginated_getter():
        # Process each page as needed
        print(page_data)
```
---
<br></br>
> ### Example 2:
> Grabbing the same data from file (simple download):
> 
> **Best Practice for a Bad Outcome**
> <br></br>

Some APIs deliver files **instead** of pages of data
- Example: Ad impressions data
-  Pros: **High Throughput** and **Low Cost**
    - A restful API must read from storage, process, and return via some logic

    - This costs time, money, and creates a bottleneck if size of data is large
    - Delivering files sidesteps the RESTful API layer
- Cons: **Memory** must hold all the data

***Awful** Example 2 Code*[^1]

```py
import requests
import json

url = "https://storage.googleapis.com/dtc_zoomcamp_api/yellow_tripdata_2009-06.jsonl"

def download_and_read_jsonl(url):
    response = requests.get(url)
    response.raise_for_status()  # Raise an HTTPError for bad responses
    data = response.text.splitlines()
    parsed_data = [json.loads(line) for line in data]
    return parsed_data
   

downloaded_data = download_and_read_jsonl(url)

if downloaded_data:
    # Process or print the downloaded data as needed
    print(downloaded_data[:5])  # Print the first 5 entries as an example
```
---
<br></br>
> ### Example 3:
> Same file, but streaming:
> 
> **More Bread and butter of Data Engineers**
> <br></br>

**We can stream download files**
- This gives us the best of both worlds

The API:
Documentation:
- The API now hides a jsonl file, already split into lines

>**JSONL file**: Each line is a json document >(i.e. "row" of data) 
>- We can yield them as they get downloaded
>- Allows processing of one row before >getting the next



>[!Tip]
> JSON files can also be downloaded this way
>- See: [ijson library](https://github.com/ICRAR/ijson) (*for python*)

Design Pros/Cons:
- Pros: **High throughput** and **Easy Memory Management**
    - We're downloading a file
- Cons: **Difficult for columnar file formats**
    - Must download entire blocks before they can be deserialized to rows
    - Code may be complex

*Example 3 Code*[^1]

```py
import requests
import json

def download_and_yield_rows(url):
    response = requests.get(url, stream=True)
    response.raise_for_status()  # Raise an HTTPError for bad responses

    for line in response.iter_lines():
        if line:
            yield json.loads(line)

# Replace the URL with your actual URL
url = "https://storage.googleapis.com/dtc_zoomcamp_api/yellow_tripdata_2009-06.jsonl"

# Use the generator to iterate over rows with minimal memory usage
for row in download_and_yield_rows(url):
    # Process each row as needed
    print(row)
```

> [!TIP]
> [dlt](https://dlthub.com/docs/intro) (data load tool) respects the streaming concept of the generator and processes it efficiently: keeping memory usage low and using parallelism where possible.

## Normalizing Data

Cleaning data usually has 2 parts:
1. Normalizing data 
    - No change to its meaning
2. Filtering data for use case
    - Changes its meaning

Often, data cleaning is just metadata work:
- Add types
    - Ex. string --> number, timestamp, etc
- Rename columns
    - Ensures column names follow a supported standard downstream
    - Ex. No strange characters in name
- Flatten nested dictionaries
    - Bring nested dictionary values to top dictionary row
- Unnest lists/arrays into child tables
    - Lists/Arrays can't be flattened into parent record
        - Must break them out into separate tables

Why not use JSON as is?
- JSON lacks schema; difficult to know what's inside
- Types aren't enforced between JSON rows
    - Ex. One row may have age as 25, another as twenty-five, and another as 25.00
    - A single record may be a dict, but multiple records may be a list of dicts
- JSON is all strings
    - To do aggregation by time, must convert dtype
- Higher memory and time cost to read a JSON
    - The whole document must be scanned vs a parquet/db, where a single column can be scanned
    - JSON is slow to aggregate, columnar formats are FAST
    - JSON is slow to search

Essentially, JSON is "lowest common denominator format" for "interchange" / data transfer, but is unsuitable for direct analytical usage

## Introducing dlt

> [dlt](https://dlthub.com/docs/intro) is a python library to assist data engineers build simpler, faster and more robust pipelines with minimal effort.
- May be thought of as a loading tool that implements data pipeline best practices to be used in your own pipelines in a declarative way
- Helps efficiently build pipelines by automating the tedious work of a data engineer in a robust way
- Handles:
    - Schema: Inferring and evolving schema, alerting changes, using schemas as data contracts
    - Typing data, flattening structures, renaming columns to fit database standards
    - Processing a stream of events/rows without filling memory
        - Includes extraction from generators
    - Loading to a variety of DBs or file formats
- Is database agnostic; if it runs well on duckDB or SQLite, it will run well on BigQuery or other OLTP databases
- install: `pip install dlt[duckdb]`

### What is DuckDB?
DuckDB is an in-memory database (like SQLite)
- Like SQLite, not a persistent database
    - can be run in process - it can be used in pipelines
    - In pipeline, we create files underneath the data, and duckDB is used to read the data
- Like dlt, can be run almost anywhere
    - Means we can use it in Jupyter Notebooks
    - In theory, can do something with dlt, load the data from duckDB, and export it to a different database
        - Data can be transformed or summarized and put into a new pipeline
- Can be thought of as a database when in development mode
    - Can do pipeline development using duckDB and iterate on it quickly
    - When ready for production, just switch from duckDB to BigQuery
- Can be used to test pipelines for CI/CD (e.g. in GitHub, etc)

## Incremental Loading

> **Incremental loading**: When updating datasets with new data, append only the new data instead of a full replacement
>- Makes pipelines run faster and cheaper
>    - Goes hand in hand with incremental extraction and state
><br></br>


>    - **State**: Information that tracks what was loaded to know what remains to be loaded
>       - dlt stores the state at the destination in a separate table
>       - Learn More: [State](https://dlthub.com/docs/general-usage/state)
><br></br>


>    - **Incremental Extraction**: Request only the increment of data needed, no more
>       - Tightly connected to state to determine exact chunk necessary to extract and load
>       - Learn More: 
>           - [Incremental loading](https://dlthub.com/docs/general-usage/incremental-loading)
>           - [Load Zendesk tickets incrementally](https://dlthub.com/docs/examples/incremental_loading/)
><br></br>

### How is **Incremental Loading** different from **Change Data Capture** (*CDC*)?
- Incremental Loading and CDC are similar but different.
    - In CDC: 
        - You receive a stream of data updates from a source database
        - There must be a system by which the updates are parsed out of the data stream
        - They can then be applied to the tables
    - In Incremental Loading:


dlt currently supports 2 ways of incremental loading:
1. Append
    - Use for immutable or stateless events (data doesn't change)
        - Example: Facts that do not change
            - Every day there are new taxi rides, but this does not change any of yesterday's taxi rides (aka history of events do not change... *yet*)
        - This allows only needing to load the new ones
    - Use to load different versions of stateful data to track when changes occur
        - Example: Creating a slowly changing dimension table for auditing changes
            - A list of cars and their colors is loaded every day
            - One day one of the cars changes color
            - We need both sets of data to know that a change occurred
2. Merge
    - Use to update data that changes
        - Example: Taxi availability status
            - Begins as "booked" but later may change into "paid", "rejected" or "cancelled"

![Image: A flowchart describing the decision process of choosing a loading method. Is it stateful data? If not, it is stateless, and choose to append it to the table. If it is stateful data, can it be incrementally requested? If not, choose to replace the table. If it can be incrementally requested, choose to merge the data into the table (aka upsert). Note: in order to keep track of changes in stateful data, the data must be appeneded.](assets/incremental_loading.png)

**Merging (UpSerting)**: ***Replaces*** an old record with a new one based on a key
    - Key could consist of multiple fields or a single unique id
    - If no unique key, can create one deterministically out of several fields that will not change and are, combined, unique (e.g. concatenating the data and hashing it)
    - Does not update the row; replaces it
        - To update only part of a row, need to load the new data by appending it and doing a custom transformation to combine the old and new data

[^1]: Code by [Adrian Brudaru](https://www.linkedin.com/in/data-team/) for his [DataTalks.Club's dlt workshop](https://github.com/DataTalksClub/data-engineering-zoomcamp/blob/main/cohorts/2024/workshops/dlt_resources/data_ingestion_workshop.md) (*with minor alteration*)

## Homework
[Linked colab notebook](https://colab.research.google.com/drive/1Te-AT0lfh0GpChg1Rbd0ByEKOHYtWXfm#scrollTo=wLF4iXf-NR7t&forceEdit=true&sandboxMode=true) has exercises to practice these concepts.

#### Question 1: What is the sum of the outputs of the generator for limit = 5?
- A: 10.234
- B: 7.892
- C: 8.382
- D: 9.123
#### Question 2: What is the 13th number yielded by the generator?
- A: 4.236
- B: 3.605
- C: 2.345
- D: 5.678
#### Question 3: Append the 2 generators. After correctly appending the data, calculate the sum of all ages of people.
- A: 353
- B: 365
- C: 378
- D: 390
#### Question 4: Merge the 2 generators using the ID column. Calculate the sum of ages of all the people loaded as described above.
- A: 205
- B: 213
- C: 221
- D: 230