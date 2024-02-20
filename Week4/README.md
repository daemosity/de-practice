# Week 4: Analytics Engineering Notes

Goal: Transforming data in DWH into Analytical Views by developing a [dbt project](https://github.com/DataTalksClub/data-engineering-zoomcamp/blob/main/04-analytics-engineering/taxi_rides_ny/README.md).

Prerequisites:
- Running DW (BigQuery or postgres)
- A set of running pipelines ingesting the project dataset (see week 3)
- [Datasets](https://github.com/DataTalksClub/nyc-tlc-data/) ingested from the course
    - Yellow taxi data - Years 2019 and 2020
    - Green taxi data - Years 2019 and 2020
    - fhv data - Year 2019

Focus:
- Data Modelling
- Data Presentation

## Setting up environment

#### Cloud (*The Preferred Option*)
Set up dbt for using BigQuery (cloud)
 1. [Open a free developer dbt](https://www.getdbt.com/signup/)
 2. [Follow instructions](https://github.com/DataTalksClub/data-engineering-zoomcamp/blob/main/04-analytics-engineering/dbt_cloud_setup.md) to connect to BigQuery instance

#### Local
Set up dbt for Postgres locally
 1. [Open a free developer dbt](https://www.getdbt.com/signup/)
 2. Choose one of the following:
    - Follow official dbt documentation 
    - Follow [dbt core with BigQuery on Docker guide](https://github.com/DataTalksClub/data-engineering-zoomcamp/blob/main/04-analytics-engineering/docker_setup/README.md) to setup dbt locally on docker
    - Use docker image from official [Install with Docker](https://docs.getdbt.com/docs/core/docker-install)
3. Must install latest version with BigQuery adapter (dbt-bigquery)
4. Must install latest version with postgres adapter (dbt-postgres)
5. After local installation, must set up connection to PG in the `profiles.yml`
    - [Templates found here](https://docs.getdbt.com/docs/core/connect-data-platform/postgres-setup)

## 01 Introduction to analytics Engineering

What is Analytics Engineering?

Part 1: Latest developments in data domain

1. Massively parallel processing (MPP) databases
    - Cloud DWs (BigQuery, Snowflake, Redshift) lower cost of storage in computing
2. Data-pipelines-as-a-service
    - Tools like fivetran or stitch simplify ETL process
3. SQL-first
    - Tools like Looker (also introduces version control systems to data workflow)
4. Version control systems
5. Self service analytics
    - BI tools like mode
6. Data Governance

These have changed the way data teams work & how stakeholders consume the data
- This left a gap in data team roles
    - Data Engineer
        - Prepares and maintains the infrastructure the data team needs
        - Great software engineers, but doesn't have training in how data will be used by business users
    
    - Data Analyst/Data Scientist
        - Uses data to answer questions and solve problems
        - Now writing more code due to new tech/software developments
            - Not originally meant to be software engineers; not originally meant to do that, isn't first priority
    
    - Analytics Engineer
        - Attempts to fill the gap between Data Analyst/Scientist and Data Engineer
        - Introduces good software engineering practices to the efforts of data analysts and data scientists
        - Potential scopes:
            - Data Loading
                - Tools:
            - Data Storing
                - Tools: Cloud data warehouses like Snowflake, Bigquery, Redshift
            - Data Modelling
                - Tools: dbt or Dataform
            - Data Presentation
                - BI tools: Looker, Mode, Power BI or Tableau

Part 2: Data Modelling concepts
1. ETL vs ELT
    - ETL:
        - Extract, Transform, Load
        - Takes longer to implement; must first transform data
        - Slightly more stable and compliant data analysis (data is cleaned)
        - Higher storage and compute costs
    - ELT:
        - Extract, Load, Transform
        - Faster and more flexible data analysis
        - Lower cost and lower maintenance
            - Takes advantage of cloud data warehousing (lower cost of storage and compute)

2. Kimball's Dimensional Modeling
    - Objective
        - Deliver data understandable to business users
        - Deliver fast query performance
    - Approach
        - Prioritize user understandability and query performance over non redundant data (3NF)
    - Other Approaches
        - Bill Inmon
        - Data vault
    
    - Elements of Dimensional Modeling
        - Fact Tables
            - Measurements, metrics, or facts
            - Corresponds to a business *process*
            - "verbs"
                - Ex. Sales, Orders
        - Dimensions tables
            - Corresponds to a business *entity*
            - Provides context to a business process
            - "nouns"
                - Ex. Customer, Market, Date, Product
    - Architecture of Dimensional Modeling: Kitchen analogy
        - Stage Area 
            - Kitchen/Raw food
            - Contains the raw data
            - Not meant to be exposed to everyone
        - Processing area 
            - Kitchen/Cook with recipes
            - From raw data to data models
            - Focuses on efficiency
            - Ensuring standards
        - Presentation area 
            - Dining Hall
            - Final presentation of the data
            - Exposure to business stakeholder

## 02 Introduction to analytics Engineering

## 03 Introduction to analytics Engineering

## 04 Introduction to analytics Engineering

## 05 Introduction to analytics Engineering

## 06 Introduction to analytics Engineering

## 07 Introduction to analytics Engineering

## Advanced Concepts

 - [Make a model Incremental](https://docs.getdbt.com/docs/building-a-dbt-project/building-models/configuring-incremental-models)
 - [Use of tags](https://docs.getdbt.com/reference/resource-configs/tags)
 - [Hooks](https://docs.getdbt.com/docs/building-a-dbt-project/hooks-operations)
 - [Analysis](https://docs.getdbt.com/docs/building-a-dbt-project/analyses)
 - [Snapshots](https://docs.getdbt.com/docs/building-a-dbt-project/snapshots)
 - [Exposure](https://docs.getdbt.com/docs/building-a-dbt-project/exposures)
 - [Metrics](https://docs.getdbt.com/docs/building-a-dbt-project/metrics)

## Week 4 Homework 

In this homework, we'll use the models developed during the week 4 videos and enhance the already presented dbt project using the already loaded Taxi data for fhv vehicles for year 2019 in our DWH.

This means that in this homework we use the following data [Datasets list](https://github.com/DataTalksClub/nyc-tlc-data/)
* Yellow taxi data - Years 2019 and 2020
* Green taxi data - Years 2019 and 2020 
* fhv data - Year 2019. 

We will use the data loaded for:

* Building a source table: `stg_fhv_tripdata`
* Building a fact table: `fact_fhv_trips`
* Create a dashboard 

If you don't have access to GCP, you can do this locally using the ingested data from your Postgres database
instead. If you have access to GCP, you don't need to do it for local Postgres - only if you want to.

> **Note**: if your answer doesn't match exactly, select the closest option 

### Question 1: 

**What happens when we execute dbt build --vars '{'is_test_run':'true'}'**
You'll need to have completed the ["Build the first dbt models"](https://www.youtube.com/watch?v=UVI30Vxzd6c) video. 
- It's the same as running *dbt build*
- It applies a _limit 100_ to all of our models
- It applies a _limit 100_ only to our staging models
- Nothing

### Question 2: 

**What is the code that our CI job will run? Where is this code coming from?**  

- The code that has been merged into the main branch
- The code that is behind the creation object on the dbt_cloud_pr_ schema
- The code from any development branch that has been opened based on main
- The code from the development branch we are requesting to merge to main


### Question 3 (2 points)

**What is the count of records in the model fact_fhv_trips after running all dependencies with the test run variable disabled (:false)?**  
Create a staging model for the fhv data, similar to the ones made for yellow and green data. Add an additional filter for keeping only records with pickup time in year 2019.
Do not add a deduplication step. Run this models without limits (is_test_run: false).

Create a core model similar to fact trips, but selecting from stg_fhv_tripdata and joining with dim_zones.
Similar to what we've done in fact_trips, keep only records with known pickup and dropoff locations entries for pickup and dropoff locations. 
Run the dbt model without limits (is_test_run: false).

- 12998722
- 22998722
- 32998722
- 42998722

### Question 4 (2 points)

**What is the service that had the most rides during the month of July 2019 month with the biggest amount of rides after building a tile for the fact_fhv_trips table?**

Create a dashboard with some tiles that you find interesting to explore the data. One tile should show the amount of trips per month, as done in the videos for fact_trips, including the fact_fhv_trips data.

- FHV
- Green
- Yellow
- FHV and Green


## Submitting the solutions

* Form for submitting: https://courses.datatalks.club/de-zoomcamp-2024/homework/hw4

Deadline: 22 February (Thursday), 22:00 CET


## Solution (To be published after deadline)

* Video: 
* Answers:
  * Question 1: 
  * Question 2: 
  * Question 3: 
  * Question 4: 

