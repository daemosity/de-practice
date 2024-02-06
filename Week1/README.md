WEEK 1 INTRODUCTION

01 Introduction to Docker, Postgres, and pgAdmin networking

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

 "-e" tag marks an environment variable being set
 - This is useful for pre-configuring user names, passwords, or other variables that must be preset to interact with the image as desired.
 - example: image: postgres:13
  - "-e POSTGRES_USER='root'"

 "-v" tag marks a volumes directory being set
 - Maps a folder in the host machine file system (e.g. Documents/programs/scripts) to a folder within the Docker container image
  - Databases require a specific folder to write data to and later to read it
    - Since Docker containers reset the image to its original setting, it is necessary to map a folder outside the image to a folder within the docker container
    - This "mounts" the folder in the host computer onto the docker image, and thus retains the data history of what happens to the data within that folder
 - example: image: postgres:13
  - "-v ~/path/to/data_folder:/var/lib/postgresql/data"
  - format: directory_inside_host:directory_inside_container
    - for directory_inside_host, must be the full path to the directory

 "-p" tag marks ports being mapped from a port on the host machine to a port on the container
 - This is necessary in order to send data from or to the container, such as SQL queries to the database
 - All requests/posts sent to the chosen port on the host machine will be forwarded to its mapped port in the container
  - example: image: postgres:13
    - "-p 5432:5432"
      - format: port_inside_host:port_inside_container

Full example:
- docker run -it \
    -e POSTGRES_USER="root" \
    -e POSTGRES_PASSWORD="root" \
    -e POSTGRES_DB="ny_taxi" \
    -v ~/path/to/data_folder:/var/lib/postgresql/data \
    -p 5432:5432 \
    postgres:13

----------------------
02 INGESTING DATA INTO POSTGRES USING PYTHON, PANDAS and PGCLI

pgcli (postgres command line interface)
 - For postgres docker containers, once the environmental variables, volumes and ports to be mapped have been set, can use PGCLI to test access via the terminal.
 - Once pgcli has been installed, can step inside the database using:
  - "pgcli -h host_name -p postgres_port -u user_name -d db_name"
  - If it is the first time within the database, it will ask you for the password
  - For terminal commands while inside postgres db, see: https://www.postgresql.org/docs/current/app-psql.html


Can use pandas to take a dataset and put it into a specific db type
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
03 CONNECTING PGADMIN AND POSTGRES

pgAdmin is a GUI tool used to interact with Postgres Database Sessions (both local and remote servers)
 - Allows performance of any database administration required for a Postgres database
 - More convenient for interacting with Postgres than a cli

Can run pgAdmin in a docker container as well:
 - pull docker image from dockerhub: 
  - example:
    - docker run -it \
      -e PGADMIN_DEFAULT_EMAIL="admin@admin.com" \
      -e PGADMIN_DEFAULT_PASSWORD="root" \
      -p 8080:80 \
      dpage/pgadmin4

If configured correctly, can connect to the pgAdmin GUI via "http://localhost:8080"

Note: if postgres is also connected via a container, a containerized pgAdmin will be unable to connect to it with default settings.
 - pgAdmin will look for the postgres db on a port within the container, which will not exist (because a connection hasn't yet been configured)
 - We will need to put both pgAdmin and postgres db containers within another container in order for them to be networked

Connecting two containers via a docker network:
 1. Create a docker network
  - example: docker network create network_name
    - network_name: can be any name for the network, cannot contain spaces
  - See more: https://docs.docker.com/network/
 2. recreate the docker containers (e.g. pgadmin and postgres images) to include the new network
  - essentially, for each container, add the following items:
    - --network=network_name
    - --name name_to_be_identified_by
      - name_to_be_identified_by: a name (without spaces) to be identified by on the network
 3. Run the container images, and you will be able to connect them (each way depending on their internal software) via their network names

------------------------
04 INTERLUDE 1a: Converting Notebook Files to Python Ingestion Scripts

In command-line, use "jupyter nbconvert --to=script path/to/script_name.ipynb"
 - Will convert the ipynb file to a script in the same folder as the ipynb file
 - Will need to be cleaned up; will contain vestigial notebook stubs

A word on security:
 - Avoid hard coding usernames, passwords, and other personal details into a script, module, etc.
 - Instead, better to pass them through environmental variables, e.g. have a separate protected file that is imported (and can only be seen/imported by you)

Finally, you can dockerize the ingestion script using a Dockerfile
 1. After the base container is identified using "FROM", use the "RUN" command to install the script's dependencies are inside the container.
    - Alternatively, this can be done by uploading a requirements.txt file and installing from there
 2. When preparing to run the image:
    - Prepend the command by adding it to the existing Docker network "e.g. --network=docker-network"
    - Append the arguments to be parsed inside the container after naming the container
    - In the case of ingesting data into an other networked container, be sure to include the other networked containers name as the host name for ingestion.

----------------
05 RUNNING POSTGRES AND PGADMIN WITH DOCKER-COMPOSE

More convenient than creating a docker network and then manually adding three separate docker containers:
 - Create a single YAML file that defines the network, containers and relationships between them
 - Docker-Compose enables this
  - See more: https://docs.docker.com/compose/

When specifying a Docker-Compose YAML file, it is structured similar to the indentations below:
 - version: "version" - the Docker-Compose version being used
 - services: - begins the structure for each image being used as part of the docker-compose architecture
    - image_name: - the name of the service you are giving the docker image
      - image: image_type:image_tag  - the base image to be constructed
      - environment: - begins the structure for the environmental variables to be associated with the container
        - name=value - environmental variables to be included as part of the image; parameter name and its value
      - volumes: - begins structure for volumes variables associated with container
        - hostPath:containerPath:mode - hostPath = path to volumes directory to mount, can be relative path; containerPath = path in container to be mounted; mode = "rw" or "ro" (readWrite or readOnly)
      - ports: - begins structure for port mapping
        - hostPort:containerPort
      - networks: - begins structure for networking containers together
        - network_name - name of common network
  - networks: - begins the structure for establishing the networks
    - network_name: - name of a network connecting containers within services
      - name: network_name - name of the same network

Other notes:
  - pg-admin needs permissions for read/write
    - add "user:" variable under the pgadmin hierarchy
    - set value to "${UID}:${GID}"

-----------------
07 INTRODUCTION TO GCP

Categories of Google Cloud Services:
- Compute
  - Compute Engine
  - Kubernetes Engine
  - App Engine
  - Cloud Functions
- Management
  - Cloud Console
  - Stackdriver
  - Trace
  - Logging
  - Debugger
  - Monitoring
- Networking
  - Cloud Load Balancing
  - Cloud CDN
  - Cloud DNS
  - Firewall Rules
  - Cloud Interconnect
  - Cloud VPN
- Storage & Databases
  - Cloud Bigtable
  - Cloud Datastore
  - Cloud Spanner
  - Cloud SQL
  - Cloud Storage
    - Create and Manage buckets
      - Similar to AWS S3
- Identity & Security
  - BigQuery
  - Cloud Dataflow
  - Cloud Dataprep
  - Cloud Dataproc
  - Cloud IoT Core
  - Cloud Pub/Sub
- Identity & Security
  - Cloud IAM
  - Cloud Endpoints
  - VPC
  - Identity Aware Proxy
  - KMS
  - Data Loss Prevention
- Machine Learning
  - Cloud ML
  - Natural Language API
  - Cloud Speech API
  - Cloud Vision API
  - Cloud Translate API

Cloud Platform works in terms of projects:
- Once within a project, navigation:
  - Drop-down menu
    - Contains all services grouped into different categories
  - Use Search Bar
-----------------
08 INTRODUCTION TERRAFORM: CONCEPTS AND OVERVIEW

Terraform is IaaC (Infrastructure as Code)

Benefits of IaaC:
  - Creates simplicity in keeping track of infrastructure
    - Defined in a file:
      - See what's going to be made, its parameters, disk size, types of storage, all which can be tweaked
  - Easier collaboration
    - Can be pushed to a repository (e.g. GitHub)
    - Can have others review it, make additions, corrections, and deploy once consensus has been reached
  - Reproducibility
    - Allows things to be built in a dev environment and then be deployed in production (after updating some parameters) and expect similar functionality
    - Allows the easy sharing and reproduction of project work
  - Ensures resources are removed
    - With a quick command, ensures all defined resources are taken down (avoids being charged for unused resources)

What Terraform Does Not Do:
  - Doesn't manage and update code on infrastructure
    - Doesn't deploy or update software (other tools are for that)
  - Doesn't allow the ability to change immutable resources
    - Ex. Cannot change virtual machine type:
      1. Requires VM destruction
      2. Requires recreation with new VM type
    - Ex. Cannot change GCS location:
      1. Requires creating a new bucket.
      2. Must copy data over
      3. Requires destruction of old Bucket
  - Cannot manage resources not defined in terraform files
    - Self-explanatory: can only manage what's in the files

What these notes are NOT:
  - Comprehensive info on Terraform (Look at docs and YouTube for more indepth)

What these notes are attempting to be:
  - Enough to get you standing up infrastructure
  - Allow the creation of resources for a project
  - Enough to make you dangerous
    - Depending on cloud provider and resource, can be VERY expensive
    - Be VERY sure of what you are deploying BEFORE you deploy it

Terraform takes a Cloud (GCP or AWS) or local (vSphere) platform and sets up infrastructure - places where your code can live and software can run.
  - Lets you define both cloud and on-prem resources in human-readable configuration files that can be versioned, reused, and shared.
  - Allows a consistent workflow to provision and manage all infrastructure throughout its lifecycle.

How Terraform Works:
- Download Terraform onto local machine, where it lives
- Users get a provider, which allows communication with services that allows them to bring up infrastructure
  - Ex. for AWS provider
    - Defined in terraform file
    - Terraform uses that provider to connect with AWS 
  - Requires some sort of access authorization
    - Service Account, Access Toke
    
What is a provider?
- Code that allows terraform to communicate to manage resources on
  - AWS
  - Azure
  - GCP
  - Kubernetes
  - VSphere
  - Alibaba Cloud
  - Oracle Cloud Infrastructure
  - Active Directory
  - And more (over 3k): https://registry.terraform.io/browse/providers

Key Terraform Commands:
- init: Get me the providers I need
  - Grabs provider code and brings back to local machine
- plan: What am I about to do?
  - After resources have been defined, shows the resources to be created
- apply: Do what is in the tf files
  - Actually build the infrastructure
- destroy: Remove everything defined in the tf files
-----------------
09 TERRAFORM BASICS: SIMPLE ONE FILE TERRAFORM DEPLOYMENT

Requires Cloud Service Account
Service Account:
  - Similar to regular user account
    - Has permissions assigned
      - Examples:
        - Abliity to open a word document
        - Ability to run python
  - Never meant to be logged into
    - Used by software to run tasks/programs/etc
- To set up (in GCP):
  1. Inside Project, navigate to IAM & Admin via dropdown menu or search bar
  2. Select Service Accounts
  3. While in Dashboard, select "Create Service Account":
    - Enter service acct name
    - Enter a description (optional)
  4. Select "Create and Continue"
  5. Grant Service Account access to a project:
    - Define the permissions; select the services we want the account to have access to
    - It is best practice to give the account access only to the services and jobs it will have access to.
      - The default "roles" have broad permissions; In the real world, these absolutely should be customized. The narrower and more specific, the more secure.
  6. Select "Continue"
  7. Specify any users or admins who should also have access to the account (optional)
  8. Select Done

To edit permissions of an existing service account:
  1. Within the IAM & Admin page, select "IAM"
  2. In the dashboard, select the pen icon to the right of the service account to change permissions
  3. Roles/permissions may be added/edited/removed from edit screen that pops up

To authenticate access to a service account:
  1. Go to Service Accounts dashboard
  2. Select the three dots next to the chosen Service Account
  3. Select "manage keys"
  4. Within the Keys dashboard that pops up, click the "Add Key" dropdown and select "Create New Key"
  5. In this case, download the JSON file.
    - Show these credentials to no-one, do not keep them saved anywhere long.
      - If credentials are stolen and permissions are broad enough, they could be used to run up thousands of dollars very quickly.
  6. Save these in a safe place to be accessed by terraform.

Setting up Terraform with Provider
- Likely, Hashicorp has the information on their website. Search for Terraform >Provider_Name<.
  - In the case of google, see: https://registry.terraform.io/providers/hashicorp/google/latest/docs/guides/provider_reference
    1. In desired directory, create a main.tf file. Copy over the template from the Hashicorp website.
    2. In provider block, Google will need project ID
    3. Also requires credentials, which can be inserted via a tf-variable or through the gcloud sdk
      - Can export the absolute path to these as a bash variable to be used later
    4. In terminal, while in the same folder as the main.tf file, use the "terraform init" command
      - Initializes backend
      - Initializes provider plugins
      - Creates a number of files to be included in repository to ensure the correct versions are running
    5. Begin adding resources as necessary. Seek them on the Hashicorp website with the chosen provider; the documentation is usually very good.
    6. Once desired resources have been added, run "terraform plan" to ensure you are creating what you expect
    7. Once plan ahs been double checked, run "terraform apply" to create resources in the cloud.
    8. Once resource use has been completed, run "terraform destroy" to destroy the resources and ensure there's nothing left to worry about.

Security Note:
  - Before pushing to a repository, ensure credentials and sensitive files are listed in .gitignore. 
  - Search for Terraform.gitignore; located on github, this file contains a terraform specific template list that should be kept private and local. It can easily be edited to add more files as necessary.

-----------------
10 DEPLOYMENT WITH A VARIABLES FILE

By convention we create a variables.tf file, which allows us to create variables to use in other tf files.
  - By placing necessary but secret information in the variables.tf file, this can allow a safe sharing of a main.tf file without sharing information that should be kept private (e.g. credentials, unique project name, etc).
  - General syntax of a variable in variables.tf file:
    - variable "property_name" {
        description = "helpful_description_of_variable"
        default     = "value_to_insert"
        }
  - Note: terraforms cannot be performed within the variables.tf file; instead, call them inside the files where the variables are used
    - Example: function "file()" tells terraform a string is a path location to a file (e.g. credentials)
  - For more information, see: https://developer.hashicorp.com/terraform/language/values/variables

-----------------
11 GITHUB CODESPACES

- A cloud-based development tool that can be used by a remote machine for development
- Free use limits for personal GitHub accounts: can store 15 GB-month and 120 core hours per month
  - GB-month - measured once per hour over the course of a whole month
    - Disk space & prebuilds assessed once per hour, use calculated as accumulated sum of all assessments
      - Assessment each hour: (total storage used) / (total hours in month)
    - Ex. storage is 15 GB on Jan 1 and remains through end of month:
      - By April 15, 7.5 GB-month used
        - (15days * 24hrs) * 15gb / (24hrs * 30days) = 7.5
      - By April 30, 15 GB-month used
  - Total Core hours =
    - (num hrs a codespace has been active) * (num cores of used machine type; 2-core, ..., 32-core)

To set up:
1. Create a (or sign into your) GitHub Account
2. Create a new (or select existing) repository
3. Create a new codespace
  - Within repository dashboard, click the three-line drop-down menu (top-left of dashboard)
  - Click on "Codespaces"
  - Click on green "New codespace" button
  - Select desired repository, branch, region, and machine type
  - Select green "Create codespace" button
4. GitHub will create and take you to codespace, which looks very similar to VSCode IDE
  - codespace will have some software packages pre-installed, but may still need to have install software if working on an already established project
    - Begins in bash, so can navigate and install new software as if on a local debian/ubuntu linux environment
    - Some pre-installed software:
      - python
      - docker
  - This codespace can also now be opened on the host Desktop VS Code
    - REQUIRES: GitHub Codespaces extension installed in VS Code Desktop
    - Click on three-line dropdown menu (top-left of codespace)
    - Click on "Open in VS Code Desktop"
    - Confirm that you want the codespace to be opened by the GitHub Codespaces extension
    - Will open in VS Code Desktop connected to your repository and your codespace (connected to a particular branch)

-----------------
12 SETTING UP THE ENVIRONMENT ON CLOUD VM (GCS)

Aim: Spinning up a VM instance to use as cloud-based development environment

1. Create a (or sign into your) Google Account
2. In console.cloud.google.com, create a new (or step into an existing) project
3. Generate an SSH key on host computer
  - https://cloud.google.com/compute/docs/connect/create-ssh-keys
  - Follow directions for creating an SSH key pair for your OS system
    - in Linux, SSH keys are saved in user's .ssh directory, and the above directions automatically assume this
      - format:
        - ssh-keygen -t rsa -f ~/.ssh/KEY_FILENAME -C USERNAME -b 2048
        - syntax:
          - ssh-keygen: command; OpenSSH authentication key utility
          - -t: option to have following parameter define the type of key to be generated
          - rsa: default type of key to be generated
          - -f: option to set the filename (and/or location) of the key file
          - ~/.ssh/filename: example of an absolute reference with filename
          - -C: option to set a username or comment
          - user_name: name that will be used in order to log into VM remotely
          - -b: Specifies number of bits in the key to create; for RSA, min-max is 1024-3072, where 3072 is considered sufficient
      - a passphrase will be requested (if left empty, there will be no passphrase)
  - two key files will be created:
    - a public key (has .pub filetype extension)
      -can be shared
    - a private key (same filename, no extension)
      - SHARE THIS WITH NO-ONE
4. Store public SSH key in google cloud:
  - In Dashboard, click on three-line dropdown menu, then select Compute Engine dropdown
  - Scroll down and under "Settings" category, select "Metadata"
  - In the associated dashboard, select "SSH Keys" to switch to SSH key screen.
  - If no SSH Keys already exist, select "Add SSH Key", else select "Edit" at top of screen then "add item" to add a new public SSH Key
  - Copy public SSH key (in linux, may be easy to use cat command, then copy and paste) and save it
  - All VMs will inherit the key
5. Create a VM instance
  - In Google Cloud Console, navigate back to "Compute Engine" (if not already there)
  - If VM instances is not the first dashboard to pop up, navigate to "VM instances"
  - Select blue "Create Instance" button, or select the 3 dots next to the "Learn" icon to dropdown the menu and select it from there
  - Within this new screen, populate parameters:
    - Name (required): VM name
    - Region: Region VM will be located
    - Zone: Zone VM will be located
    - Select Boot disk (the requested OS and storage-disk size)
    - Note: With each change, a monthly estimate will be provided/updated to help understand the cost of continuing to run the VM instance
  - Once finished, click on "Create" to create the VM
  - For more info, see: https://cloud.google.com/compute/docs/instances/create-start-instance
6. Log into VM instance from host terminal (for Linux)
  - In VM instances screen, copy external IP address of VM instance
  - In host terminal either:
    1. Log into VM with verbose ssh command:
      - ssh -i private/key/path ssh_key_username@external_ip_address
        - ssh: command to use OpenSSH remote login client
          - program for logging into a remote machine and executing commands on it
          - provides secure encrypted communications between two untrusted hosts over an insecure network
          - user must prove their identity to the remote machine
        - -i: option that indicates the next parameter is the absolute path to identity file (private key)
        - ssh_key_username: username used when creating ssh key-pair
        - external_ip_address: external ip address of VM to be logged into
    2. Log into VM via an ssh config file
      1. Create a file in /.ssh folder named config
        - Ex. cat config; touch config; etc.
      2. Within config file, configure access to external VM/server with following syntax
        - Syntax:
          - Host host_alias
              HostName VM_external_ip_address
              User username_for_ssh_key
              IdentityFile absolute_path_to_private_ssh_key
        - Save file
      3. Log into external server
        - Can now use "ssh host_alias" command
        - Alternatively, can use VS Code:
          1. Install "Remote - SSH" VS Code add-on
          2. In VS Code search bar, use "Connect to Host.."
          3. Select the alias, which should appear as an option due to the created config file
  - If all goes well, terminal will remotely log into (and be replaced with) the remote VM terminal
7. Install necessary software
  - Though GCP includes google cloud cli and some other pieces of software, the VM is a blank slate; it will be necessary to install all other software necessary to develop project
8. How to shutdown (NOT delete) VM
  1. via Google Cloud Console:
    1. Navigate to VM instances (In Compute Engine)
    2. Select VM you wish to stop
    3. Click Actions, then click Stop
  2. via Terminal
    1. Enter: "sudo shutdown now"
  - This will have the VM shutdown and close all SSH connections, and will no longer incur compute costs (if not within free tier)
  - All content/files of VM will be stored somewhere (which may incur charges if not in free tier), and will be accessible to VM once it restarts
9. How to restart VM
  1. via Google Cloud Console:
    1. Navigate to VM instances (In Compute Engine)
    2. Select VM you wish to start
    3. Click Actions, then click Start

---------------------
HOMEWORK

## Module 1 Homework

ATTENTION: At the very end of the submission form, you will be required to include a link to your GitHub repository or other public code-hosting site. This repository should contain your code for solving the homework. If your solution includes code that is not in file format (such as SQL queries or shell commands), please include these directly in the README file of your repository.

## Docker & SQL

In this homework we'll prepare the environment 
and practice with Docker and SQL


## Question 1. Knowing docker tags

Run the command to get information on Docker 

```docker --help```

Now run the command to get help on the "docker build" command:

```docker build --help```

Do the same for "docker run".

Which tag has the following text? - *Automatically remove the container when it exits* 

- `--delete`
- `--rc`
- `--rmc`
- `--rm`


## Question 2. Understanding docker first run 

Run docker with the python:3.9 image in an interactive mode and the entrypoint of bash.
Now check the python modules that are installed ( use ```pip list``` ). 

What is version of the package *wheel* ?

- 0.42.0
- 1.0.0
- 23.0.1
- 58.1.0


# Prepare Postgres

Run Postgres and load data as shown in the videos
We'll use the green taxi trips from September 2019:

```wget https://github.com/DataTalksClub/nyc-tlc-data/releases/download/green/green_tripdata_2019-09.csv.gz```

You will also need the dataset with zones:

```wget https://s3.amazonaws.com/nyc-tlc/misc/taxi+_zone_lookup.csv```

Download this data and put it into Postgres (with jupyter notebooks or with a pipeline)


## Question 3. Count records 

How many taxi trips were totally made on September 18th 2019?

Tip: started and finished on 2019-09-18. 

Remember that `lpep_pickup_datetime` and `lpep_dropoff_datetime` columns are in the format timestamp (date and hour+min+sec) and not in date.

- 15767
- 15612
- 15859
- 89009

## Question 4. Longest trip for each day

Which was the pick up day with the longest trip distance?
Use the pick up time for your calculations.

Tip: For every trip on a single day, we only care about the trip with the longest distance. 

- 2019-09-18
- 2019-09-16
- 2019-09-26
- 2019-09-21


## Question 5. Three biggest pick up Boroughs

Consider lpep_pickup_datetime in '2019-09-18' and ignoring Borough has Unknown

Which were the 3 pick up Boroughs that had a sum of total_amount superior to 50000?
 
- "Brooklyn" "Manhattan" "Queens"
- "Bronx" "Brooklyn" "Manhattan"
- "Bronx" "Manhattan" "Queens" 
- "Brooklyn" "Queens" "Staten Island"


## Question 6. Largest tip

For the passengers picked up in September 2019 in the zone name Astoria which was the drop off zone that had the largest tip?
We want the name of the zone, not the id.

Note: it's not a typo, it's `tip` , not `trip`

- Central Park
- Jamaica
- JFK Airport
- Long Island City/Queens Plaza



## Terraform

In this section homework we'll prepare the environment by creating resources in GCP with Terraform.

In your VM on GCP/Laptop/GitHub Codespace install Terraform. 
Copy the files from the course repo
[here](https://github.com/DataTalksClub/data-engineering-zoomcamp/tree/main/01-docker-terraform/1_terraform_gcp/terraform) to your VM/Laptop/GitHub Codespace.

Modify the files as necessary to create a GCP Bucket and Big Query Dataset.


## Question 7. Creating Resources

After updating the main.tf and variable.tf files run:

```
terraform apply
```

Paste the output of this command into the homework submission form.


## Submitting the solutions

* Form for submitting: https://courses.datatalks.club/de-zoomcamp-2024/homework/hw01
* You can submit your homework multiple times. In this case, only the last submission will be used. 

Deadline: 29 January, 23:00 CET