from datetime import timedelta
from geopy.distance import geodesic
import uuid
from fusion.kalman_filter import KalmanFilterCV2D
import numpy as np
from pyproj import Proj, Transformer
import pandas as pd


# Track object definition
class Track:
    def __init__(self, init_pos, init_time):
        self.id = str(uuid.uuid4())
        self.measurements = []
        self.kf = KalmanFilterCV2D(init_pos)
        self.last_update_time = init_time
        self.state_history = []
        self.velocity_history = []  # ✅ record velocity over time

    def add(self, measurement):
        dt = (measurement["time"] - self.last_update_time).total_seconds()
        self.kf.predict(dt)
        self.kf.update(measurement["position_m"])
        self.measurements.append(measurement)
        self.last_update_time = measurement["time"]

        self.state_history.append({
            "time": measurement["time"],
            "x": self.kf.get_position()[0],
            "y": self.kf.get_position()[1],
            "track_id": self.id
        })

        vx, vy = self.kf.get_velocity()
        self.velocity_history.append({
            "time": measurement["time"],
            "vx": vx,
            "vy": vy,
            "track_id": self.id
        })


    def predict_position(self, current_time):
        dt = (current_time - self.last_update_time).total_seconds()
        return self.kf.get_predicted_position(dt)

    def last_time(self):
        return self.last_update_time

    def get_velocity_trace(self):
        return self.velocity_history

# Distance helper (meters)
def compute_distance(pos1, pos2):
    return geodesic(pos1, pos2).meters


def create_local_projector(origin_lat, origin_lon):
    transformer = Transformer.from_crs("epsg:4326", "epsg:3857", always_xy=True)
    x0, y0 = transformer.transform(origin_lon, origin_lat)

    def to_local_meters(lat, lon):
        x, y = transformer.transform(lon, lat)
        return x - x0, y - y0

    def to_global_degrees(x_m, y_m):
        lon, lat = transformer.transform(x_m + x0, y_m + y0, direction="INVERSE")
        return lat, lon

    return to_local_meters, to_global_degrees

def get_state_history_df(tracks, to_global_degrees):
    records = []
    for track in tracks:
        for s in track.state_history:
            lat, lon = to_global_degrees(s["x"], s["y"])
            records.append({
                "time": s["time"],
                "lat": lat,
                "lon": lon,
                "track_id": track.id
            })
    return pd.DataFrame(records)

# Main function to call
def assign_basic_tracks(df, time_window_sec=30, dist_threshold=50, min_points=5):
    TIME_WINDOW = timedelta(seconds=time_window_sec)
    DIST_THRESHOLD = dist_threshold
    MIN_ASSOCIATION_COUNT = min_points

    df = df.sort_values(by="time").reset_index(drop=True)

    origin_lat = df.iloc[0]["lat"]
    origin_lon = df.iloc[0]["lon"]
    to_local_meters, to_global_degrees = create_local_projector(origin_lat, origin_lon)

    df["track_id"] = None

    untracked_measurements = []
    active_tracks = []

    for idx, row in df.iterrows():
        current_time = row["time"]
        current_position = (row["lat"], row["lon"])
        current_position_m = to_local_meters(*current_position)

        current_measurement = {
            "time": current_time,
            "position": current_position,  # original lat/lon
            "position_m": current_position_m,  # in meters
            "index": idx
        }

        # Try to associate with existing track
        matched = False
        for track in active_tracks:
            if current_time - track.last_time() <= TIME_WINDOW:
                # First, check the last position only
                predicted_pos_m = track.predict_position(current_time)
                predicted_pos_deg = to_global_degrees(*predicted_pos_m)
                if compute_distance(current_position, predicted_pos_deg) <= DIST_THRESHOLD:
                    track.add(current_measurement)
                    df.at[idx, "track_id"] = track.id
                    matched = True
                    break
                else:
                    # Fallback: check up to 2 more previous positions (for a total of 3)
                    recent_measurements = track.measurements[-3:-1]  # second and third from the end
                    for m in reversed(recent_measurements):
                        dist = compute_distance(current_position, m["position"])
                        if dist <= DIST_THRESHOLD:
                            track.add(current_measurement)
                            df.at[idx, "track_id"] = track.id
                            matched = True
                            break
                    if matched:
                        break

        if not matched:
            # Add this unmatched measurement to the pool
            untracked_measurements.append(current_measurement)

            # Initialize a new list to hold nearby measurements
            cluster = []
            for m in untracked_measurements:
                time_difference = current_time - m["time"]
                distance = compute_distance(current_position, m["position"])
                if time_difference <= TIME_WINDOW and distance <= DIST_THRESHOLD:
                    cluster.append(m)

            # If enough close measurements are found, create a new track
            if len(cluster) >= MIN_ASSOCIATION_COUNT:
                # Use the first measurement as the initializer
                init_pos = cluster[0]["position_m"]
                init_time = cluster[0]["time"]
                new_track = Track(init_pos, init_time)

                for m in cluster:
                    new_track.add(m)
                    df.at[m["index"], "track_id"] = new_track.id

                active_tracks.append(new_track)

                # Remove clustered measurements from untracked pool
                remaining = []
                for m in untracked_measurements:
                    if m not in cluster:
                        remaining.append(m)
                untracked_measurements = remaining
    return df, active_tracks
