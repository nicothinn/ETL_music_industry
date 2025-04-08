import os
import polars as pl
import requests
import pandas as pd
import psycopg2
from dotenv import load_dotenv

def extract_spotify():
    df = pl.read_csv("../data/raw/spotify_dataset.csv")
    df.write_csv("../data/raw/spotify_dataset2.csv")

def extract_grammys():
    load_dotenv()

    dbname = os.getenv("DB_NAME")
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    host = os.getenv("DB_HOST")
    port = os.getenv("DB_PORT")

    conn = psycopg2.connect(
        dbname=dbname,
        user=user,
        password=password,
        host=host,
        port=port
    )

    cur = conn.cursor()
    cur.execute("SELECT * FROM public.grammy_awards;")
    columns = [desc[0] for desc in cur.description]
    rows = cur.fetchall()
    cur.close()
    conn.close()

    df = pl.DataFrame(rows, schema=columns)
    df.write_csv("../data/raw/grammy_awards_full.csv")

def extract_billboard():
    url = "https://raw.githubusercontent.com/mhollingshead/billboard-hot-100/main/all.json"
    response = requests.get(url)

    if response.status_code == 200:
        charts = response.json()
        all_data = []

        for chart in charts:
            chart_date = chart["date"]
            for entry in chart["data"]:
                all_data.append({
                    "date": chart_date,
                    "rank": entry.get("this_week"),
                    "title": entry.get("song"),
                    "artist": entry.get("artist"),
                    "last_week": entry.get("last_week"),
                    "peak_position": entry.get("peak_position"),
                    "weeks_on_chart": entry.get("weeks_on_chart")
                })

        df = pd.DataFrame(all_data)
        df.to_csv("../data/raw/billboard_full_chart_data.csv", index=False)
        print("Billboard data extracted successfully!")

    else:
        print(f"Failed to fetch chart data. Status code: {response.status_code}")

__all__ = ["extract_spotify", "extract_grammys", "extract_billboard"]

