from data.loader import load_sigint_csv
from visualization.plot_tracks import (
    preprocess_df,
    plot_events_vs_time,
    plot_latitude_vs_time,
    plot_longitude_vs_time,
)
from visualization.map_view import plot_on_map
from fusion.basic_track_association import assign_basic_tracks
from visualization.plot_tracks import plot_kalman_velocity_components_vs_time

df = load_sigint_csv("0_531_to_0_540.csv")
df = preprocess_df(df)
df = df.drop_duplicates(
    subset=[col for col in df.columns if col not in ("uid", "raw_event")]
).reset_index(drop=True)

plot_events_vs_time(df)
plot_latitude_vs_time(df, hue_col="object_uid")
plot_longitude_vs_time(df, hue_col="object_uid")

# m = plot_on_map(df)
# m.save("sigint_map_495_to_518.html")  # View this file in a browser

df_with_tracks, active_tracks = assign_basic_tracks(df, time_window_sec=300, dist_threshold=100, min_points=5)
associated_df = df_with_tracks[df_with_tracks["track_id"].notnull()]

plot_latitude_vs_time(associated_df, hue_col="track_id")
plot_longitude_vs_time(associated_df, hue_col="track_id")

# plot_kalman_velocity_components_vs_time(active_tracks)
