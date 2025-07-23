import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from shapely import wkt
from geopy.distance import geodesic
import matplotlib.pyplot as plt


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


def plot_longitude_vs_time(df, hue_col="object_uid", kf_df=None):
    plt.figure(figsize=(10, 5))

    sns.scatterplot(x='time', y='lon', hue=hue_col, data=df, palette='tab10', s=20, legend=False)

    if kf_df is not None:
        sns.scatterplot(
            x="time", y="lon", data=kf_df,
            marker='X', color='black', s=50, label="Kalman Estimate", alpha=0.7
        )

    plt.title("Filtered Tracks - Longitude vs Time (with Kalman Estimates)")
    plt.xlabel("Time")
    plt.ylabel("Longitude")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

def plot_latitude_vs_time(df, hue_col="object_uid", kf_df=None):
    plt.figure(figsize=(10, 5))

    # Raw or associated data
    sns.scatterplot(x='time', y='lat', hue=hue_col, data=df, palette='tab10', s=20, legend=False)

    # Kalman overlay
    if kf_df is not None:
        sns.scatterplot(
            x="time", y="lat", data=kf_df,
            marker='X', color='black', s=50, label="Kalman Estimate", alpha=0.7
        )

    plt.title("Filtered Tracks - Latitude vs Time (with Kalman Estimates)")
    plt.xlabel("Time")
    plt.ylabel("Latitude")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

def plot_kalman_velocity_components_vs_time(active_tracks):
    """
    Plots Kalman-estimated velocity components (vx, vy) vs time for each track.
    vx ~ longitude velocity, vy ~ latitude velocity
    """
    import pandas as pd
    import matplotlib.pyplot as plt

    records = []
    for track in active_tracks:
        records.extend(track.get_velocity_trace())

    df = pd.DataFrame(records)
    if df.empty:
        print("No velocity component data to plot.")
        return

    fig, axes = plt.subplots(2, 1, figsize=(12, 8), sharex=True)

    for track_id, group in df.groupby("track_id"):
        axes[0].plot(group["time"], group["vx"], label=f"Track {track_id[:6]}")
        axes[1].plot(group["time"], group["vy"], label=f"Track {track_id[:6]}")

    axes[0].set_ylabel("vx (m/s) ~ Longitude velocity")
    axes[1].set_ylabel("vy (m/s) ~ Latitude velocity")
    axes[1].set_xlabel("Time")

    axes[0].set_title("Kalman-Estimated Velocity Components vs Time")
    axes[0].legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize='small')
    plt.tight_layout()
    plt.show()

