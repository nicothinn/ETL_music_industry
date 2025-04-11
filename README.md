# Music Industry ETL & Dashboard Project

This project implements an end-to-end ETL pipeline to integrate and analyze music data from **Spotify**, **Grammy Awards**, and **Billboard Hot 100**. In addition, an interactive dashboard built with Dash and Plotly displays key insights about music industry trends. The solution is developed in Python within a virtual environment, using Docker Compose to deploy Apache Airflow (with PostgreSQL and Redis) and other services.

---

## Table of Contents

1. [Requirements and Technologies](#requirements-and-technologies)
2. [Project Structure](#project-structure)
3. [ETL Pipeline Components](#etl-pipeline-components)
    - [Extraction Phase](#extraction-phase)
    - [Transformation Phase](#transformation-phase)
    - [Load & Storage Phase](#load--storage-phase)
4. [Airflow Orchestration](#airflow-orchestration)
5. [Dashboard Visualization](#dashboard-visualization)
6. [Credentials and Google Drive API Setup](#credentials-and-google-drive-api-setup)
7. [Setup and Usage Instructions](#setup-and-usage-instructions)
8. [Conclusions](#conclusions)

---

## 1. Requirements and Technologies

### Prerequisites
- **Python 3.8 or higher**
- **Docker and Docker Compose**
- **Git**
- **A Virtual Environment** (recommended to use `venv` or `virtualenv`)

### Technologies Used
- **Python:** Primary language for ETL, data manipulation, and dashboard development.
- **Polars, Pandas, NumPy:** Data processing and numerical computations.
- **psycopg2, SQLAlchemy:** PostgreSQL database interaction.
- **Plotly and Dash:** For interactive visualizations and dashboard creation.
- **Apache Airflow:** To orchestrate the ETL pipeline.
- **Docker Compose:** For container management (Airflow, PostgreSQL, Redis).
- **PyDrive:** For uploading the final dataset to Google Drive via the Google Drive API.

---

## 2. Project Structure

```plaintext
├── dags                   # Airflow DAGs (workflow definitions)
├── data                   # Raw and processed data storageD
│   ├── raw                # Raw data files (Spotify CSV, Grammy CSV, Billboard JSON)
│   └── processed          # Transformed data and the final merged dataset
├── src                    # ETL source code
│   ├── extract.py         # Extraction functions for each data source
│   ├── transform.py       # Transformation functions for cleaning and normalization
│   ├── merge_data.py      # Function to merge datasets into one final CSV
│   └── load.py            # Functions to load data into PostgreSQL and upload to Google Drive
├── config                 # Additional configuration files
├── plugins                # Airflow plugins (if applicable)
├── logs                   # Airflow logs
├── requirements.txt       # Python dependencies
├── docker-compose.yml     # Docker Compose configuration for Airflow and related services
├── Dockerfile             # Custom Dockerfile for the Airflow image
├── .env                   # Environment variables (DB credentials and others)
└── client_secrets.json    # Google Drive API credentials (OAuth client)
```
## 1. Requirements and Technologies

### Prerequisites
- **Python 3.8 or higher**
- **Docker and Docker Compose**
- **Git**
- **A Virtual Environment** (recommended to use `venv` or `virtualenv`)

### Technologies Used
- **Python:** Primary language for ETL, data manipulation, and dashboard development.
- **Polars, Pandas, NumPy:** Data processing and numerical computations.
- **psycopg2, SQLAlchemy:** PostgreSQL database interaction.
- **Plotly and Dash:** For interactive visualizations and dashboard creation.
- **Apache Airflow:** To orchestrate the ETL pipeline.
- **Docker Compose:** For container management (Airflow, PostgreSQL, Redis).
- **PyDrive:** For uploading the final dataset to Google Drive via the Google Drive API.

---

## 2. Project Structure

```plaintext
├── dags                   # Airflow DAGs (workflow definitions)
├── data                   # Raw and processed data storage
│   ├── raw                # Raw data files (Spotify CSV, Grammy CSV, Billboard JSON)
│   └── processed          # Transformed data and the final merged dataset
├── src                    # ETL source code
│   ├── extract.py         # Extraction functions for each data source
│   ├── transform.py       # Transformation functions for cleaning and normalization
│   ├── merge_data.py      # Function to merge datasets into one final CSV
│   └── load.py            # Functions to load data into PostgreSQL and upload to Google Drive
├── config                 # Additional configuration files
├── plugins                # Airflow plugins (if applicable)
├── logs                   # Airflow logs
├── requirements.txt       # Python dependencies
├── docker-compose.yml     # Docker Compose configuration for Airflow and related services
├── Dockerfile             # Custom Dockerfile for the Airflow image
├── .env                   # Environment variables (DB credentials and others)
└── client_secrets.json    # Google Drive API credentials (OAuth client)
```
## 3. ETL Pipeline Components

### Extraction Phase
- **extract_spotify:**  
  Extracts Spotify raw data from a CSV file, creates an intermediate copy at `/data/raw/spotify_dataset2.csv`.

- **extract_grammys:**  
  Connects to the PostgreSQL database to extract Grammy Awards data (using environment variables from `.env`) and saves it to `/data/raw/grammy_awards_full.csv`.

- **extract_billboard:**  
  Retrieves historical Billboard Hot 100 chart data from a public JSON dataset on GitHub and saves it to `/data/raw/billboard_full_chart_data.csv`.

### Transformation Phase
- **transform_spotify:**  
  Cleans and normalizes Spotify data (renames columns, normalizes text, converts duration to minutes) and stores the result at `/data/processed/spotify_transformed.csv`.

- **transform_grammys:**  
  Normalizes and filters the Grammy Awards data (focusing on track-related categories) and saves it at `/data/processed/grammys_transformed.csv`.

- **transform_billboard:**  
  Processes and standardizes the Billboard dataset, extracting key date information, and stores the processed data at `/data/processed/billboard_transformed.csv`.
### Load & Storage Phase
- **merge_datasets:**  
  Merges the transformed datasets from Spotify, Grammys, and Billboard on a standardized key (`song_name`). The final merged dataset is written to `/data/processed/final_dataset.csv`.

- **load_and_store_final_dataset:**  
  Loads the final dataset into a PostgreSQL table using the `COPY` command, and then uploads the CSV to Google Drive via PyDrive. This requires proper Google Drive API credentials.
## 4. Airflow Orchestration

The ETL pipeline is orchestrated with Apache Airflow. The Airflow DAG (found in the `dags` directory) defines tasks and dependencies as follows:
- **Extraction Tasks:** `extract_spotify`, `extract_grammys`, `extract_billboard`
- **Transformation Tasks:** `transform_spotify`, `transform_grammys`, `transform_billboard`
- **Merge Task:** `merge_datasets`
- **Load Task:** `load_and_store_final_dataset`

The DAG uses a daily schedule (`@daily`), with dependencies configured so that:
1. All extraction tasks run first,
2. Their outputs feed into the corresponding transformation tasks,
3. Then the transformed data is merged,
4. Finally, the final dataset is loaded into PostgreSQL and uploaded to Google Drive.

The Docker Compose file (version `3.8`) sets up Airflow alongside PostgreSQL and Redis.
## 5. Dashboard Visualization

The dashboard is built using Dash and Plotly and provides interactive visualizations such as:
- **Explicit vs. Non-Explicit Songs (Pie Chart)**
- **Popularity Distribution (Histogram)**
- **Billboard Chart Performance (Bar Charts for weeks on chart and weeks at #1)**
- **Top Grammy-Winning Artists (Bar Chart)**
- **Treemap of Billboard Songs (Treemap)**
- **Average Danceability by Genre (Bar Chart)**
- **Feature Correlation Heatmap (Heatmap)**
- **Source Coverage (Bar Chart)**
- **Grammy Winners per Year (Stacked Bar Chart)**

These visualizations are displayed on a responsive dashboard with a consistent dark theme. SQLAlchemy is used to connect to PostgreSQL and extract the merged dataset for visualization.
## 6. Credentials and Google Drive API Setup

To enable the upload of the final dataset to Google Drive:

**Download Google Cloud Credentials:**
1. Go to [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project or select an existing one.
3. Enable the Google Drive API.
4. Create OAuth client credentials and download the `client_secrets.json` file.
5. Place `client_secrets.json` in the project root (or the path specified in the Docker Compose file).

**Configure Environment Variables:**
Create a `.env` file in the project root with your database credentials and any other required variables:

DB_NAME=your_database_name DB_USER=your_database_user DB_PASSWORD=your_database_password DB_HOST=your_database_host DB_PORT=your_database_port

## 7. Setup and Usage Instructions

### A. Setting Up the Python Virtual Environment
1. **Create a Virtual Environment:**
   ```bash
   python3 -m venv venv
2.### Activate the Virtual Environment

**On Linux/Mac:**
```bash
source venv/bin/activate
```

**On Windows:**
```bash
venv\Scripts\activate
```

**Install Python Dependencies**
```bash
pip install -r requirements.txt
```
## Deploying the Project with Docker Compose

Ensure Docker and Docker Compose are installed.

---

###  Build and Start the Containers

From the project root directory, run:

```bash
docker-compose up --build
```
### Access the Airflow UI
Open your browser and navigate to:
```bash
http://localhost:8080
```
Use the admin credentials created during initialization:

Username: airflow
Password: airflow


## 8. Conclusions

This project unifies data from Spotify, Grammy Awards, and Billboard Hot 100 to provide a comprehensive overview of musical success. With a robust ETL pipeline orchestrated by Apache Airflow and deployed via Docker Compose, the project ensures reliable data extraction, transformation, merging, and loading. The interactive dashboard created with Dash and Plotly offers deep insights into how streaming popularity, chart performance, and award recognition intersect.

Key outcomes include:
- A robust framework ensuring high data quality and consistency.
- Insights into the correlations between commercial success (streaming and charts) and critical recognition (awards), valuable for artists, producers, and industry professionals.
- An interactive dashboard that empowers dynamic exploration of trends and patterns, supporting both strategic decision-making and detailed analytical research.

Overall, the project lays a strong foundation for advanced analytics, predictive modeling, and recommendation systems within the music industry.
