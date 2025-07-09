from data.loader import load_sigint_csv
from visualization.plot_tracks import (
    preprocess_df,
    plot_events_vs_time,
    plot_latitude_vs_time,
    plot_longitude_vs_time,
)
from visualization.map_view import plot_on_map

df = load_sigint_csv("0_368_to_0_378.csv")
df = preprocess_df(df)

plot_events_vs_time(df)
plot_latitude_vs_time(df)
plot_longitude_vs_time(df)


m = plot_on_map(df)
m.save("sigint_map.html")  # View this file in a browser
