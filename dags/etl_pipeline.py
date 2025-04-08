# === DAG CONFIGURATION ===
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import logging
import sys

# === PATH CONFIGURATION ===
# Para que Airflow encuentre el módulo src dentro del contenedor
sys.path.append("../src")

# === IMPORTACIÓN DE FUNCIONES DEL PIPELINE ===
from src.extract import extract_spotify, extract_grammys, extract_billboard
from src.transform import transform_spotify, transform_grammys, transform_billboard
from src.merge_data import merge_datasets
from src.load import load_and_store_final_dataset

# === LOGGING CONFIGURATION ===
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def log_task(task_name, func):
    def wrapper(*args, **kwargs):
        logger.info(f"[START] Task: {task_name}")
        result = func(*args, **kwargs)
        logger.info(f"[END] Task: {task_name}")
        return result
    return wrapper

def return_none_wrapper(func):
    def wrapper(*args, **kwargs):
        func(*args, **kwargs)
        return None
    return wrapper

# === DAG DEFINITION ===
with DAG(
    dag_id="etl_music_pipeline",
    default_args={
        "owner": "airflow",
        "start_date": datetime(2024, 3, 21),
        "retries": 1,
    },
    description="ETL pipeline for music data from Spotify, Grammys, and Billboard",
    schedule_interval="@daily",
    catchup=False,
) as dag:

    task_extract_spotify = PythonOperator(
        task_id="extract_spotify",
        python_callable=log_task("extract_spotify", return_none_wrapper(extract_spotify)),
    )

    task_extract_grammys = PythonOperator(
        task_id="extract_grammys",
        python_callable=log_task("extract_grammys", return_none_wrapper(extract_grammys)),
    )

    task_extract_billboard = PythonOperator(
        task_id="extract_billboard",
        python_callable=log_task("extract_billboard", return_none_wrapper(extract_billboard)),
    )

    task_transform_spotify = PythonOperator(
        task_id="transform_spotify",
        python_callable=log_task("transform_spotify", return_none_wrapper(transform_spotify)),
    )

    task_transform_grammys = PythonOperator(
        task_id="transform_grammys",
        python_callable=log_task("transform_grammys", return_none_wrapper(transform_grammys)),
    )

    task_transform_billboard = PythonOperator(
        task_id="transform_billboard",
        python_callable=log_task("transform_billboard", return_none_wrapper(transform_billboard)),
    )

    task_merge = PythonOperator(
        task_id="merge_datasets",
        python_callable=log_task("merge_datasets", return_none_wrapper(merge_datasets)),
    )

    task_load = PythonOperator(
        task_id="load_and_store",
        python_callable=log_task("load_and_store_final_dataset", return_none_wrapper(load_and_store_final_dataset)),
    )

    # === TASK DEPENDENCIES ===
    [
        task_extract_spotify,
        task_extract_grammys,
        task_extract_billboard,
    ] >> [
        task_transform_spotify,
        task_transform_grammys,
        task_transform_billboard,
    ] >> task_merge >> task_load
