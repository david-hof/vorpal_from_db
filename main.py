from data.loader import load_sigint_csv
from visualization.plot_tracks import (
    preprocess_df,
    plot_events_vs_time,
    plot_latitude_vs_time,
    plot_longitude_vs_time,
)
from visualization.map_view import plot_on_map
from fusion.basic_track_association import assign_basic_tracks, get_state_history_df
from visualization.plot_tracks import plot_kalman_velocity_components_vs_time
from fusion.basic_track_association import create_local_projector

folder_path = r"C:\Users\david\PycharmProjects\vorpal_from_db\data\15_7_to_16_7"
scenario_name = '1752558395_0_to_1752558395_20'
df = load_sigint_csv(r"0_368_to_0_378.csv")
df = preprocess_df(df)
df = df.drop_duplicates(
    subset=[col for col in df.columns if col not in ("uid", "raw_event")]
).reset_index(drop=True)

plot_events_vs_time(df)
plot_latitude_vs_time(df, hue_col="object_uid")
plot_longitude_vs_time(df, hue_col="object_uid")

# m = plot_on_map(df)
# m.save("sigint_map_495_to_518.html")  # View this file in a browser

df_with_tracks, active_tracks = assign_basic_tracks(df, time_window_sec=30, dist_threshold=100, min_points=5)
associated_df = df_with_tracks[df_with_tracks["track_id"].notnull()]

origin_lat, origin_lon = df.iloc[0]["lat"], df.iloc[0]["lon"]
_, to_global_degrees = create_local_projector(origin_lat, origin_lon)

kf_df = get_state_history_df(active_tracks, to_global_degrees)

plot_latitude_vs_time(associated_df, hue_col="track_id")
plot_longitude_vs_time(associated_df, hue_col="track_id")

# plot_kalman_velocity_components_vs_time(active_tracks)
