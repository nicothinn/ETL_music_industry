import polars as pl
import os
import re

DATA_RAW = "../data/raw"
DATA_PROCESSED = "../data/processed"

def normalize_text(value):
    if isinstance(value, str):
        value = value.lower()
        value = re.sub(r"[^a-z0-9\s;]", "", value)
        value = re.sub(r"\s+", " ", value)
        return value.strip()
    return value

def transform_spotify():
    df = pl.read_csv(f"{DATA_RAW}/spotify_dataset2.csv")
    df = df.rename({col: col.strip().lower().replace(" ", "_") for col in df.columns})

    df = df.with_columns([
        pl.col("track_name").map_elements(normalize_text, return_dtype=pl.Utf8),
        pl.col("artists").map_elements(normalize_text, return_dtype=pl.Utf8)
    ])

    df = df.select([
        pl.col("track_name").alias("song_name"),
        pl.col("artists").alias("artist"),
        "track_genre",
        "popularity",
        "explicit",
        "tempo",
        "valence",
        "energy",
        "danceability",
        "acousticness",
        "duration_ms"
    ])

    df = df.with_columns([
        (pl.col("duration_ms") / 60000).alias("duration_minutes")
    ])

    df.write_csv(f"{DATA_PROCESSED}/spotify_transformed.csv")

def transform_grammys():
    df = pl.read_csv(f"{DATA_RAW}/grammy_awards_full.csv")
    df = df.rename({col: col.strip().lower().replace(" ", "_") for col in df.columns})

    df = df.with_columns([
        pl.col("nominee").map_elements(normalize_text, return_dtype=pl.Utf8),
        pl.col("artist").map_elements(normalize_text, return_dtype=pl.Utf8),
        pl.col("category").map_elements(normalize_text, return_dtype=pl.Utf8)
    ])

    df = df.filter(
        (pl.col("category").str.contains("song") | pl.col("category").str.contains("record")) &
        ~(pl.col("category").str.contains("album") | pl.col("category").str.contains("artist"))
    )

    df = df.with_columns([
        pl.col("nominee").alias("song_name")
    ])

    df.write_csv(f"{DATA_PROCESSED}/grammys_transformed.csv")

def transform_billboard():
    df = pl.read_csv(f"{DATA_RAW}/billboard_full_chart_data.csv")
    df = df.rename({col: col.strip().lower().replace(" ", "_") for col in df.columns})

    df = df.with_columns([
        pl.col("title").map_elements(normalize_text, return_dtype=pl.Utf8),
        pl.col("artist").map_elements(normalize_text, return_dtype=pl.Utf8)
    ])

    df = df.with_columns([
        pl.col("title").alias("song_name"),
        pl.col("date").str.slice(0, 4).cast(pl.Int64).alias("first_year_on_chart")
    ])

    df.write_csv(f"{DATA_PROCESSED}/billboard_transformed.csv")

_all__ = [
    "transform_spotify",
    "transform_grammys",
    "transform_billboard"
]