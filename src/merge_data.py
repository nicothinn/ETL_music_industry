import polars as pl
import os

DATA_PROCESSED = "../data/processed"

def merge_datasets():
    df_spotify = pl.read_csv(f"{DATA_PROCESSED}/spotify_transformed.csv")
    df_grammys = pl.read_csv(f"{DATA_PROCESSED}/grammys_transformed.csv")
    df_billboard = pl.read_csv(f"{DATA_PROCESSED}/billboard_transformed.csv")

    df_spotify = df_spotify.unique()
    df_grammys = df_grammys.unique()
    df_billboard = df_billboard.unique()

    df_spotify = df_spotify.with_columns([
        (pl.col("song_name") + "|" + pl.col("artist")).alias("merge_key")
    ]).sort("popularity", descending=True)

    df_spotify = df_spotify.group_by("merge_key").agg([
        pl.col("song_name").first(),
        pl.col("artist").first(),
        pl.col("track_genre").unique().alias("track_genres"),
        pl.col("popularity").first(),
        pl.col("explicit").first(),
        pl.col("tempo").first(),
        pl.col("valence").first(),
        pl.col("energy").first(),
        pl.col("danceability").first(),
        pl.col("acousticness").first(),
        pl.col("duration_minutes").first()
    ])

    df_spotify = df_spotify.with_columns([
        pl.col("track_genres").list.join(", ").alias("track_genre")
    ]).drop("track_genres")

    df_grammys = df_grammys.sort("year", descending=True)
    df_grammys = df_grammys.group_by("song_name").agg([
        pl.col("year").first(),
        pl.col("category").first(),
        pl.col("published_at").first()
    ])

    df_billboard = df_billboard.with_columns([
        (pl.col("song_name") + "|" + pl.col("artist")).alias("merge_key")
    ])

    df_billboard_grouped = df_billboard.group_by("merge_key").agg([
        pl.col("date").min().alias("first_chart_date"),
        pl.col("rank").min().alias("billboard_peak"),
        pl.col("weeks_on_chart").sum().alias("total_weeks_on_chart"),
        pl.col("first_year_on_chart").min()
    ])

    merged = df_spotify.join(df_grammys, on="song_name", how="left")
    merged = merged.join(df_billboard_grouped, on="merge_key", how="left")

    merged = merged.drop("merge_key")

    columns_to_drop = [
        "duration_ms",
        "nominee",
        "artist_grammy",
        "workers",
        "img",
        "winner",
        "first_year_on_chart",
        "billboard_artist",
        "updated_at",
        "title",
        "published_at"
    ]
    existing_to_drop = [col for col in columns_to_drop if col in merged.columns]
    merged = merged.drop(existing_to_drop)

    merged.write_csv(f"{DATA_PROCESSED}/final_dataset.csv")

_all = [
    "merge_datasets"
]