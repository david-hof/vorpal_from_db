import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from shapely import wkt


def preprocess_df(df):
    from shapely import wkt
    from shapely.geometry import Point

    # Fix object_uid to keep only the numeric part (e.g., "0_368" → 368)
    df["object_uid"] = df["object_uid"].astype(str).str.extract(r'_(\d+)$').astype(float)

    # Parse WKT column only if not already parsed
    if "event_point" not in df.columns:
        raise ValueError("Expected column 'event_point' not found in dataframe.")

    if not isinstance(df["event_point"].iloc[0], Point):
        df["event_point"] = df["event_point"].apply(wkt.loads)

    df["lon"] = df["event_point"].apply(lambda p: p.x)
    df["lat"] = df["event_point"].apply(lambda p: p.y)

    return df

def plot_events_vs_time(df):
    plt.figure(figsize=(12, 5))
    sns.scatterplot(x='time', y='object_uid', hue='object_uid', data=df, palette='tab10', s=10, legend=False)
    plt.title("Event Time vs Object UID")
    plt.xlabel("Time")
    plt.ylabel("Object UID (Coded)")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


def plot_latitude_vs_time(df, hue_col="object_uid"):
    plt.figure(figsize=(10, 5))
    sns.scatterplot(x='time', y='lat', hue=hue_col, data=df, palette='tab10', s=20, legend=False)
    plt.title(f"Latitude vs Time (colored by {hue_col})")
    plt.xlabel("Time")
    plt.ylabel("Latitude")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


def plot_longitude_vs_time(df, hue_col="object_uid"):
    plt.figure(figsize=(10, 5))
    sns.scatterplot(x='time', y='lon', hue=hue_col, data=df, palette='tab10', s=20, legend=False)
    plt.title("Longitude vs Time (colored by {hue_col})")
    plt.xlabel("Time")
    plt.ylabel("Longitude")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()
