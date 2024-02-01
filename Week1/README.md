Introduction to Docker, Postgres, and pgAdmin networking

Dataset used: Taxi Rides NY dataset
 - Used for practicing SQL and constructing data pipelines
----------------
DOCKER

What is docker?
 - Delivers software in packages called containers
   - These containers are isolated from one another and can communicated with each other through well-defined channels

What is a data-pipeline?
 - A fancy name for a process service that receives data from a source and produces more data to a destination.
 - A single data-pipeline can receive data from more than one source
 - A single data-pipeline can output data to more than one destination
 - A destination can be another data-pipeline, resulting in a chain of sources and destinations, which itself would be called a single data-pipeline
 - Example 1: 
   1. Python script gets a csv file from a source (e.g. computer, network, etc.)
   2. Script processes, transforms or cleans it
   3. Script outputs data to a destination (e.g. same as source or different) in the same or different format (e.g. a table in Postgres)
 - Example 2: Using a host computer (e.g. Windows, Linux, MacOS), can have multiple docker containers that each contain only what they need for their part of the pipeline chain
   1. A container (w. UbuntuOS) has Python 3.9 installed with Pandas library and Postgres connection library
   2. Another container that only has what it needs to run a Postgres database
   3. Another container that only has what it needs to run pgAdmin
   4. Connect 1 and 3 to 2, where 1 and 3 don't know about each other
   5. This allows SQL queries to be run on the data ingested to the Postgres container

The Benefits of Docker
 - Docker allows containers to be run in any environment:
   - A container can be built in a host computer environment, then put into Google Cloud (kubernetes) or AWS batch, and it will run exact same way as it was run locally on host computer
      - Has same libraries
      - Has same versioning
 - Reproducibility
   - An image can be copied as many times as needed and will still be the same image
 - Allows experiments, tests, and integration tests (CI/CD) to be run locally before sending work to production
   - For CI/CD, usually use Github Actions, GitLab CI/CD, Jenkins
 - Allows pipelines on the cloud (AWS Batch, Kubernetes jobs)
 - Spark - helps run data-pipelines by specifying all the dependencies we need for the data pipeline in Spark with Docker
 - Serverless (AWS Lambda, Google functions) - allows defining the environment as a Docker image

---------------------
WORKING WITH DOCKER

 - docker run hello-world
    1. Docker client contacted the Docker daemon
    2. Docker daemon searches for the docker image "hello-world" on the local machine
    3. If Docker daemon doesn't find the image name, pulls the "hello-world" image from the Docker Hub. (amd64)
    3. Docker daemon created a new container from that image which runs the executable that produces output it is commanded to do

 - docker run -it ubuntu bash
    - pulls and runs a docker image with an ubuntu base
    - enters it interactively in bash
    - everything that comes after image name "ubuntu" is a command/parameter to execute in the image container
        - in this case, it enters it interactively in bash
        - in other cases, it may be a command/parameter to give to whatever program runs when the docker image starts

Docker images run in isolation; they don't retain changed state by default, so if, while within the image, the user deletes everything and exits, the image can be reloaded and because it always starts at its frozen state, it will be as it was the first time it was loaded and entered.
 - This also allows host machine to not be affected by such potentially dangerous actions

 - docker run -it python:3.9
   - specify the image (python), and a tag
      - a tag can be thought of as a specific version of the image we want to run
   - to override the normal entrypoint:
      - add the --entrypoint="chosen_entrypoint" option, where the entrypoint can be something like bash
        - ex. docker run -it --entrypoint=bash python:3.9
      - adding "bash" after the commandline call to the docker image also appears to work

 For some images with program language base, have to install things from outside (e.g. pip install python requires being outside the python terminal)
    - To accomplish this, can open a docker python container and enter via bash
 - This works if it's a one-off image, but if it's an image that will be repeatedly used, it's better to create a Dockerfile.
 
-------------------------
ENTER THE DOCKERFILE

A Dockerfile can specify/execute everything we want to run on start up and set an outside folder to retain a persistent state
 - In Dockerfile
   - "FROM" - defines base image we want to use. Whatever is executed afterwards will use the base image
      - base_image:tag
   - "RUN" - executes commands, such as "pip install pandas", and creates a new image based on the result
   - "ENTRYPOINT" - overrides the normal entrypoint into the base_image
    - Can also execute commands on entry
      - Example: ENTRYPOINT ["python", "pipeline.py"]
        - The first parameter is the executable to be run (e.g. bash, python, etc)
        - The second parameter is a parameter to be given to the executable to run
        - This takes more parameters as arguments, which may be added in the Dockerfile or manually after the docker image:tag (e.g. docker run -it test:pandas arg1 arg2 arg3)
        - In this example, the container will start in the python environment and immediately run pipeline.py
   - "WORKDIR" - specifies the working directory (location in the image -- the container -- as the default working directory)
    - If directory doesn't exist, the Dockerfile will make it
    - It will then change the entry location in the image to this directory (e.g. cd /app)
   - "COPY" - copies file/directory from source (specified directory) to the destination (given directory in the image)
 - Example of simple Dockerfile
   * FROM python:3.9
   * RUN pip install pandas
   * WORKDIR /app
   * COPY pipeline.py pipeline.py
   * ENTRYPOINT ["bash"]

Next, we build this custom image via the "docker build" command
 - ex. "docker build -t test:pandas ."
   - "-t" - allows a tag to be added
   - "test" - the created_image name
   - "pandas" - the created image tag
   - "." - where to find the Dockerfile, in this case, in the current directory
   - can build in "tag" format, prepending with option -t and then "imageName:tag" format
 - This builds the image defined in the Dockerfile located in the specified folder
 - Once built, can be called with "docker run -it 'image_name':'tag'"

---------
MAKE IT SELF-SUFFICIENT

Container is still not a pipeline:
 - In order to call a docker image a pipeline, it must be self-sufficient
  - Container must run on its own
  - In current state:
    - Must open container
    - Must manually execute pipeline
 - Will want to add more parameters
  - Will want to have it scheduled to run on a specific date, where it will run on its own and save the results somewhere

---------------------
CONFIGURING DOCKER CONTAINER ENVIRONMENT VARIABLES

 - "-e" tag marks an environment variable being set
  - This is useful for pre-configuring user names, passwords, or other variables that must be preset to interact with the image as desired.
  - example: image: postgres:13
    - "-e POSTGRES_USER='root'"
 - "-v" tag marks a volumes directory being set
  - Maps a folder in the host machine file system (e.g. Documents/programs/scripts) to a folder within the Docker container image
    - Databases require a specific folder to write data to and later to read it
      - Since Docker containers reset the image to its original setting, it is necessary to map a folder outside the image to a folder within the docker container
      - This "mounts" the folder in the host computer onto the docker image, and thus retains the data history of what happens to the data within that folder
  - example: image: postgres:13
    - "-v ~/code_projx/de-practice/ny_taxi_postgres_data:/var/lib/postgresql/data"
    - format: directory_inside_host:directory_inside_container
      - for directory_inside_host, must be the full path to the directory
 - "-p" tag marks ports being mapped from a port on the host machine to a port on the container
  - This is necessary in order to send data from or to the container, such as SQL queries to the database
  - example: image: postgres:13
    - "-p 5432:5432"
      - format: port_inside_host:port_inside_container

----------------------
INGESTING DATA INTO POSTGRES USING PYTHON, PANDAS and PGCLI

 - pgcli (postgres command line interface)
  - For postgres docker containers, once the environmental variables, volumes and ports to be mapped have been set, can use PGCLI to test access via the terminal.
  - Once pgcli has been installed, can step inside the database using:
    - "pgcli -h host_name -p postgres_port -u user_name -d db_name"
    - If it is the first time within the database, it will ask you for the password
    - For terminal commands while inside postgres db, see: https://www.postgresql.org/docs/current/app-psql.html


 - Can use pandas to take a dataset and put it into a specific db type
  1. Create a connection to the desired database
    - from sqlalchemy import create_engine
    - create an engine variable using create_engine() function
      - required parameter format:
        - "db_type://user_name:user_password@host_name:port_name/database_name"
        - example: "postgresql://root:root@localhost:5432/ny_taxi"
    - test the connection to make sure the details are correct
      - engine_variable.connect()
      - if there's no errors/complaints, the correct details are in place
  2. Generate a schema using a sample of the entire dataset (n <= 100)
    - This is the DLL (Data Definition Language) instruction "CREATE TABLE" followed by the table columns and their datatypes
    - Use pandas.io.sql.get_schema()
      - Required parameters:
        - dataframe - the populated pandas dataframe to be ingested
        - name - the name of the new database table to be created
        - con - sqlalchemy.engine.(Engine or Connection) or sqlite3.Connection
      - ex. "pandas.io.sql.get_schema(df, name='yellow_taxi_data')"
    - This isn't a perfect function; it is better to print the output of pandas...get_schema() first to make sure pandas inferred the correct datatypes (e.g. DateTime instead of Text)
      - Should datatypes not meet expectations, transformations will have to be made on the dataset to align it with expected dtypes.
  3. If working with a large file (i.e. csvs with millions of rows), it will be ideal to load in the file in chunks rather than all at once. This allows the connection of multiple data processing stages to create memory-efficient data pipelines.
    - When reading in the dataset, create an iterator and set chunk size
      - example: "df_iter = pd.read_csv('yellow_tripdata_2021-01.csv'), iterator=True, chunksize=100_000)"
    - Use "next(iterator_variable)" to retrieve the first chunk from the iterator:
      1. Perform the necessary data transformations on the dataset to prepare/clean it, and validate using pandas...get_schema()
      2. Using df.head(n=0) as the DataFrame, use DataFrame.to_sql(name="table_name", con=engine_variable, if_exists="replace") to only insert the table definition to the database (no rows)
        - name: name of table
        - con: engine_variable
        - if_exists: what to do if table already exists, choices = 'fail', 'replace', 'append'; default = 'fail'
          - fail: Raises a ValueError
          - replace: Drops the table before inserting new values
          - append: Insert new values to the existing table
      3. Next, perform the df.to_sql on the full df chunk, setting "if_exists" parameter to "append"
    - Use a "for item in iterator" or "while condition == True" loop using "next(iterator_variable)" and sub-steps 1 and 3 to insert the rest of the dataset into the database
      - As this occurs, can use pgcli to check in directly with database table to see it iteratively grow

-------------------------
