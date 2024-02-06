WEEK 2: WORKFLOW ORCHESTRATION

Overview of what is going to be built:
1. Tools:
    - Docker
        - Mage container
        - Postgres Database container

2. Project (using Mage):
    - Extract and Transform a New York taxi dataset ("dataset")
    - Load it into Postgres
    - Load it into GCS
    - Extract dataset from GCS
    - Transform it using Pandas, Apache Arrow, SQL
    - Load it to Google BigQuery

01 INTRO TO ORCHESTRATION

Orchestration: How you can orchestrate data workflows via a tool. In this case: Mage
    - A large part of data engineering is extracting, transforming, and loading data between sources
    - Orchestration is a process of dependency management, facilitated through automation
        - Automation is key piece; we want to minimize manual work by automating as many processes as possible
    - The data orchestrator manages scheduling, triggering, monitoring, and even resource allocation

Orchestration Facts:
    - Every workflow requires sequential steps in a particular order to be successful
        - Example:
            - Taking data from X
            - Clean it & Transform it
            - Move it to Y
            - Downstream Processes that depend on Y are then kicked off
    - Each step is a task
    - Workflows are thought of as DAGs (directed acyclic graphs)
        - Also can be known as a data pipeline

Data Engineering Lifecycle:
1. Data is generated
2. It travels through ingestion, transformation, and serving (may travel through this pipeline multiple times), where its base home becomes data storage
3. It is eventually served to Analytics, Machine Learning, Reverse ETL, etc

Data Engineering Lifecycle Undercurrents:
    - Security
    - Data management
    - DataOps
    - Data architecture
    - Orchestration
    - Software engineering

It is important to have a good solution that fits your use case
    - There is no one single perfect solution

A good orchestrator handles:
    - Workflow management
        - Define, schedule, and manage workflows efficiently
        - Ensure tasks are executed in the right order
        - Manages dependencies
    - Automation
        - As data engineers are focused on automating as much as possible, solution should be good at automating many things at once
    - Error handling
        - Orchestrators should have built-in solutions for:
            - Handling errors
            - Conditional logic branching
            - Retrying failed tasks
    - Recovery
        - When things break, if data is lost, there must be a way to backfill/recover missing/lost data
    - Monitoring, alerting
        - If a pipeline fails, or retries must happen, has the capability to send a notification


A part of being a data engineer is 
- Figuring out how your situation is unique
- Doing the research to make sure the right solution is found
-------------------
02 INTRO TO MAGE

-------------------
03 ETL: API TO POSTGRES

-------------------
04 ETL: API TO GCS

-------------------
05 ETL: GCS TO BIGQUERY

-------------------
06 PARAMETERIZED EXECUTION

-------------------
07 DEPLOYMENT

-------------------
08 HOMEWORK

## Week 2 Homework

ATTENTION: At the end of the submission form, you will be required to include a link to your GitHub repository or other public code-hosting site. This repository should contain your code for solving the homework. If your solution includes code that is not in file format, please include these directly in the README file of your repository.

> In case you don't get one option exactly, select the closest one 

For the homework, we'll be working with the _green_ taxi dataset located here:

`https://github.com/DataTalksClub/nyc-tlc-data/releases/tag/green/download`

You may need to reference the link below to download via Python in Mage:

`https://github.com/DataTalksClub/nyc-tlc-data/releases/download/green/`

### Assignment

The goal will be to construct an ETL pipeline that loads the data, performs some transformations, and writes the data to a database (and Google Cloud!).

- Create a new pipeline, call it `green_taxi_etl`
- Add a data loader block and use Pandas to read data for the final quarter of 2020 (months `10`, `11`, `12`).
  - You can use the same datatypes and date parsing methods shown in the course.
  - `BONUS`: load the final three months using a for loop and `pd.concat`
- Add a transformer block and perform the following:
  - Remove rows where the passenger count is equal to 0 _and_ the trip distance is equal to zero.
  - Create a new column `lpep_pickup_date` by converting `lpep_pickup_datetime` to a date.
  - Rename columns in Camel Case to Snake Case, e.g. `VendorID` to `vendor_id`.
  - Add three assertions:
    - `vendor_id` is one of the existing values in the column (currently)
    - `passenger_count` is greater than 0
    - `trip_distance` is greater than 0
- Using a Postgres data exporter (SQL or Python), write the dataset to a table called `green_taxi` in a schema `mage`. Replace the table if it already exists.
- Write your data as Parquet files to a bucket in GCP, partioned by `lpep_pickup_date`. Use the `pyarrow` library!
- Schedule your pipeline to run daily at 5AM UTC.

### Questions

## Question 1. Data Loading

Once the dataset is loaded, what's the shape of the data?

* 266,855 rows x 20 columns
* 544,898 rows x 18 columns
* 544,898 rows x 20 columns
* 133,744 rows x 20 columns

## Question 2. Data Transformation

Upon filtering the dataset where the passenger count is greater than 0 _and_ the trip distance is greater than zero, how many rows are left?

* 544,897 rows
* 266,855 rows
* 139,370 rows
* 266,856 rows

## Question 3. Data Transformation

Which of the following creates a new column `lpep_pickup_date` by converting `lpep_pickup_datetime` to a date?

* `data = data['lpep_pickup_datetime'].date`
* `data('lpep_pickup_date') = data['lpep_pickup_datetime'].date`
* `data['lpep_pickup_date'] = data['lpep_pickup_datetime'].dt.date`
* `data['lpep_pickup_date'] = data['lpep_pickup_datetime'].dt().date()`

## Question 4. Data Transformation

What are the existing values of `VendorID` in the dataset?

* 1, 2, or 3
* 1 or 2
* 1, 2, 3, 4
* 1

## Question 5. Data Transformation

How many columns need to be renamed to snake case?

* 3
* 6
* 2
* 4

## Question 6. Data Exporting

Once exported, how many partitions (folders) are present in Google Cloud?

* 96
* 56
* 67
* 108

## Submitting the solutions

* Form for submitting: https://courses.datatalks.club/de-zoomcamp-2024/homework/hw2
* Check the link above to see the due date
  
## Solution

Will be added after the due date
-------------------
09 NEXT STEPS