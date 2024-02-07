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
    - Resource optimization
        - If Orchestrator is managing where jobs are executed, it ideally plays a role in optimizing the best route for that execution
    - Observability
        - Having visibility into every part of the data pipeline
        - Ideally comes with built-in observability functionality
    - Debugging
        - A part of observability
        - Orchestrator should allow easy debugging of data pipelines
    - Compliance/Auditing
        - Ideally should help with compliance/auditing for data workflows

A good workflow orchestrator prioritizes the developer experience
- Flow state
    - Feeling of flow; effortless development
    - Not having to switch between 7 tools/services
- Feedback Loops
    - Ability to iterate quickly, to fail fast, to get tangible feedback from what is built very quickly
    - Not having to spend a lot of time testing a single product
- Cognitive Load
    - How much effort does it take to manage everything while trusting the tools you're using?

A part of being a data engineer is 
- Figuring out how your situation is unique
- Doing the research to make sure the right solution is found
-------------------
02 INTRO TO MAGE

Mage is an open-source pipeline tool for orchestrating, transforming, and integrating data
- Data integration:
    - The process of extracting data from a variety of disparate sources and combining it into a single unified view for analysis and management
        - Can be accomplished via manual integration, data virtualization, application integration, or by moving data from multiple sources into a unified destination
        - Most common: ETL - datasets brought together from different data sources and harmonized, then loaded into a target data warehouse or database
        - Alternate: ELT - data delivered into a large data system and transformed at a later stage
    - Common tools for this: airbyte, fivetran
    - Mage has a data integration functionality that is separate from the rest of the tool

Mage Concepts:
1. Instance/Environment: Contains one or more projects
2. Project: Kind of like "Home Base", contains one or more pipelines
3. Pipeline: Comprised of one or more blocks
    - Workflow that executes a data operation (ex. ETL from an API)
    - Called DAGs on other platforms
    - Can contain Blocks (written SQL, Python, or R) and Charts
    - Represented by a YAML file in the "pipelines" folder of the project
        - Makes it possible to dynamically create template pipelines or automate the creation of pipeline files
4. Blocks: The atomic unit that make up a transformation in Mage
    - Files that are reusable, atomic pieces of code that perform certain actions
        - Changing a block changes it everywhere it's used
        - If necessary, can detach blocks to separate instances if necessary
    - Can be executed independently or within a pipeline
        - Used together, form data pipelines (aka Directed Acyclic Graphs aka DAGs aka a workflow)
    - Can be written in python, SQL or R
    - Commonly used to export, transform or load data, but can be customized for any task (even ML models)
    - Will not run in a pipeline until all upstream dependencies are met
    - Contains unique functionality out of the box:
        1. Sensors
            - Triggers when an event occurs
        2. Conditionals
            - Branching logic as well as if else logic
        3. Dynamics
            - Can create dynamic children
        4. Webhooks
            - For additional functionality

Mage handles:
- Data Integration
- Unified Pipelines
- Multi-user environments
- Templating

Mage:
- Can use a hybrid environment (program GUI) for interactive development or work purely using an IDE (like VSCode)
- Can use blocks as testable, reusable pieces of code
- Allows coding and testing in parallel
- Helps reduce dependencies, reduce number of tools needed

Mage has Engineering best-practices built-in:
- In-line testing and debugging
    - Familiar, notebook-style format
- Fully-featured observability
    - Transformation in one place: 
        - Integrates with dbt models for complete lineage view of batch, streaming, and integration pipelines, & more
- DRY principles:
    - No more DAGs with duplicate functions and weird imports
    - DEaaS

Anatomy of a Block:
1. Imports
    - Declare what you need for the block
    - Import best practices: https://peps.python.org/pep-0008/#imports
2. Decorator
    - Defines the expected behavior of the block (declared using @ + keyword(s))
3. Function
    - Code that performs the desired task
4. Test/Assertion
    - Run on the output dataframe of the block

Updating Mage when using it from a Docker Image:
- enter the following commands:
    - docker pull mage-ai/mageai:latest
    - docker compose up
        - docker will rebuild the mageai image if it updated
-------------------
03 ETL: API TO POSTGRES

In Tutorial, we were provided with a Postgres DB and Mage-ai container connected via Docker Compose. We will now move towards connecting Mage-ai with Postgres from within the Mage-ai program, then loading data from an API

Note: in project file, it is a good idea to have a .env file with assigned variables. Similar to a variables.tf file, these variables can be used in main images and files in order to maintain security while developing locally. As such, the files themselves should be included in the .gitignore file as well.

Postgres Facts:
- Structured OLTP Database
    - Just means it's "row-oriented" rather than "column-oriented"

Within the Mage instance's dashboard:
1. select the files icon (left side of dashboard)
    - A list of files within the project folder will appear, displayed similarly to the VS Code Explorer
2. select the io_config.yaml file to edit in environment variables containing connection settings to database
    - default connections are located in this file, prepopulated with the necessary variables for a slew of different database connections
    - it is also possible to specify connection profiles
        - to specify a connection profile:
            1. At the end of default profile, with no indentation, name the custom connection profile
                - syntax: "profile_name:" (without double quotes)
                - example: "dev:"
            2. Pull in environment variables using Jinja templating (within single quotes) surrounding env_var() function (the internal variable also gets single quotes)
                - example: '{{ env_var( 'POSTGRES_DBNAME' ) }}'
3. Test that connection works
    1. Navigate to "Pipelines" using the Pipelines icon on left side of Mage UI
    2. Create a new pipeline by selecting the colored "New" Button, and choosing one of the options
        - Example: Standard (batch)
        - On creation, the pipeline is given a randomized name
            - To rename: 
                1. Click on the "Edit" dropdown menu in the top-center of the screen
                2. Select "pipeline settings"
                3. Rename the pipeline by clicking into the name textbox
                4. Save settings
                5. To continue editing pipeline, navigate to "Edit Pipeline" by clicking on the button with code braces
    3. Add a Data loader block
        1. To add a new code block while in the "edit pipeline" screen
            1. Select the desired block type
            2. In the drop-down menu that appears, select desired language
            3. If the language has more options, select desired template
            4. In the dialogue that pops up, you may use the randomly generated name or enter your own
            5. Click "Save and add" to generate the block
                - After the block has been generated, the block name can be edited by clicking on its name 
        2. To delete a code block
            1. Go to the header of the block that should be deleted
            2. On the right side of header, click on circle with three dots inside, "More actions"
            3. In the drop-down menu, click on "Delete Block"
    4. In Connection drop-down, select "PostgreSQL"
    5. In Profile drop-down, select the desired profile with valid credentials
    6. Check the "Use raw SQL" box
        - This removes the Mage templating
        - What you type is what is run within the Postgres database table
    7. Enter "SELECT 1;" as the SQL code to run
        - Mage-ai won't be running this; Postgres will. This is how to tell whether Mage has been correctly configured to connect to the Postgres database. 
        - If the block returns 1, the connection was configured correctly and you can move forward
        - If the block returns an error, time to debug

To Load data from an API to Postgres:
4. Add a new pipeline
5. Add a data loader block using Python using an API template
    1. If loading csv files (even compressed csv files like csv.gz), don't need requests; can load via pandas
    2. Map datatypes = Best Practice
        - Powerful in data engineering, especially with pandas
        - Drastically reduces memory usage pandas typically incurs when processing dataset
            - When a dataset is huge (e.g. 1 million rows), can make a huge difference in memory consumption
        - Take a look at the first 100 or so rows in Jupyter Notebook, infer the types, and create a datatype map for when building the dataset into pipeline
            - Creates an implicit assertion; if datatypes change, pipeline will fail
        - Give this variable to dtype parameter in pandas
    3. Create a list of any columns that include datetime dtypes
        - give this variable to parse_dates parameter in pandas
    4. return pandas dataframe
6. Add a transformer block using Python using generic template
    1. Transform dataframe to deal with any issues with the data
        - example: in Taxi dataset, taxi rides with 0 passengers could be dropped
    2. Add tests to ensure the transformations occurred as planned
        - All functions with @test decorator are run as tests; can have multiple tests after main transformer function
7. Add a data exporter block using Python to Postgres template
    1. Fill in the necessary variables
    2. Ensure that if database exists, it is replaced
        - This is part of idempotence, an important concept in Data Engineering
8. Add a Data Loader SQL block to ensure data was ingested as intended

-------------------
04 ETL: API TO GCS

GCS Facts:
- Rather than being an OLTP Database, GCS is a file system in the cloud.
    - In Data Engineering, we write data to these cloud storage locations because:
        - Storage is much cheaper
        - Accepts semi-structured data much better than a relational database
    - From here, workflows typically involve staging data, cleaning data, maybe writing data to an analytical source or using a DataLake or DataLakehouse solution in the cloud

To ensure Mage can connect to GCS and BigQuery, must set necessary variables in the project io_config.yaml.
- Similar process to connecting to Postgres, minor addition:
    - If a service account with proper permissions hasn't yet been made, make it and download the credential key json
    - Be sure to include the keyfile name in the .gitignore file
    - Copy the keyfile into the mage project folder
    - Add absolute path to keyfile (within the docker image) as a variable in .env
    - Add the path to io_config.yaml similar how environment variables were added to connect to Postgres Database

To test to make sure the connection is successful, run the same SQL test query against BigQuery that was run against Postgres
    - Once run, this code continues to exist and can be pulled from data loaders under the name it was saved under.
    - Change the database option from Postgres to BigQuery, and change the profile to the profile that hosts the path to the google cloud credentials

To test to make sure the connection is successful with GCS, load the titanic dataset into a google cloud storage bucket, then create a Data Loader block that pulls the data from the GCS bucket.

Creating a data pipeline from API to GCS:
1. We can reuse the data loader block we created to extract the yellow-taxi-data
2. We can reuse the transformer block we created to clean the data
3. Create a data exporter block using Python language and our GCS bucket as the target

We load a parquet into GCS.

Sidenote:
- In Data Engineering, we often don't want to write a very large dataset to a single parquet file.
- Instead, we would want to write to a partitioned parquet file structure
    - Partitioning means breaking a dataset up by a row or characteristic
    - A large file can be very slow to read and write; partitioning makes it easier to query as well as IO operations (e.g. reading/writing)
    - Partitioning by date is often useful
        - It creates an even distribution for daily activity
        - It's a natural way to query data, and makes it easy to access by extension

Mage can execute blocks in parallel. This means we can upload a full parquet to GCS as well as a partitioned parquet.

Writing the GCS Data Exporter block for parquet partitioning:
1. import pyarrow as pa
2. import pyarrow.parquet as pq
3. import os
4. Assign the file path (from within docker image) to google creds and assign it to os.environ['GOOGLE_APPLICATION_CREDENTIALS]
5. Assign variables for:
    - name of target GCS bucket
    - project id
    - table name
    - root path to bucket:
        - target GCS bucket name/table name
6. For partitioning by date, ensure that there's a table dedicated to only the date. 
    - If it doesn't yet exist, it can be created by extracting the date using Series.dt.date property
7. Assign a pyarrow table variable (necessary) using pa.Table.from_pandas(data)
8. Set the gcs creds by using pa.fs.GcsFileSystem()
    - This grabs the environment variable we assigned earlier
9. Write the partition to GCS using pyarrow.parquet:
    - pq.write_to_dataset(table, root_path, partition_cols, filesystem)
        - table: pyarrow table
        - root_path: earlier assigned variable
        - partition_cols: created (or existing) date column
        - filesystem: the file path assigned to the environmental variable

Benefit of using pyarrow:
    - It abstracts away chunking logic
        - Working with normal pandas, would need to iterate through dataframe with IO operations
    - Takes away the pain of communicating with pandas and GCS

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