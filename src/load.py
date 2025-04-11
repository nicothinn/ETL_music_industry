import os
import psycopg2
from dotenv import load_dotenv
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

DATA_PROCESSED = "/data/processed"
CSV_FILENAME = "final_dataset.csv"
CSV_FILE_PATH = f"{DATA_PROCESSED}/{CSV_FILENAME}"

def load_and_store_final_dataset(**kwargs):
    load_dotenv()

    dbname   = os.getenv("DB_NAME")
    user     = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    host     = os.getenv("DB_HOST")
    port     = os.getenv("DB_PORT")

    conn = psycopg2.connect(
        dbname=dbname,
        user=user,
        password=password,
        host=host,
        port=port
    )
    cur = conn.cursor()

    create_table_query = """
    CREATE TABLE IF NOT EXISTS public.music_dataset (
        song_name TEXT,
        artist TEXT,
        popularity INTEGER,
        explicit BOOLEAN,
        tempo FLOAT,
        valence FLOAT,
        energy FLOAT,
        danceability FLOAT,
        acousticness FLOAT,
        duration_minutes FLOAT,
        track_genre TEXT,
        year INTEGER,
        category TEXT,
        first_chart_date TEXT,
        billboard_peak INTEGER,
        total_weeks_on_chart INTEGER
    );
    """
    cur.execute(create_table_query)
    conn.commit()

    copy_query = """
    COPY public.music_dataset (
        song_name, artist, popularity, explicit, tempo, valence, energy,
        danceability, acousticness, duration_minutes, track_genre, year,
        category, first_chart_date, billboard_peak, total_weeks_on_chart
    )
    FROM STDIN WITH CSV HEADER DELIMITER ',' NULL ''
    """
    with open(CSV_FILE_PATH, 'r', encoding='utf-8') as f:
        cur.copy_expert(copy_query, f)

    conn.commit()
    cur.close()
    conn.close()
    print("Final dataset loaded into PostgreSQL.")

    gauth = GoogleAuth()
    gauth.LoadClientConfigFile("/client_secrets.json")
    gauth.LocalWebserverAuth()
    drive = GoogleDrive(gauth)

    file_to_upload = drive.CreateFile({'title': CSV_FILENAME})
    file_to_upload.SetContentFile(CSV_FILE_PATH)
    file_to_upload.Upload()
    print("Final dataset uploaded to Google Drive.")

__all__ = ["load_and_store_final_dataset"]
