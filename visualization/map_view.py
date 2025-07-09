import folium
from folium.plugins import MarkerCluster
import pandas as pd

def plot_on_map(df, lat_col='lat', lon_col='lon', object_uid_col='object_uid'):
    """Plot a map with all points using folium"""
    df = df.dropna(subset=[lat_col, lon_col])
    start_coords = (df[lat_col].mean(), df[lon_col].mean())
    m = folium.Map(location=start_coords, zoom_start=10)

    marker_cluster = MarkerCluster().add_to(m)

    for _, row in df.iterrows():
        popup_text = f"{row[object_uid_col]}<br>{row['time']}"
        folium.CircleMarker(
            location=(row[lat_col], row[lon_col]),
            radius=3,
            color='blue',
            fill=True,
            fill_opacity=0.7,
            popup=popup_text
        ).add_to(marker_cluster)

    return m
