from datetime import timedelta
from geopy.distance import geodesic
import uuid

# Track object definition
class Track:
    def __init__(self):
        self.id = str(uuid.uuid4())
        self.measurements = []

    def add(self, measurement):
        self.measurements.append(measurement)

    def last_time(self):
        return self.measurements[-1]['time']

    def last_position(self):
        return self.measurements[-1]['position']

# Distance helper (meters)
def compute_distance(pos1, pos2):
    return geodesic(pos1, pos2).meters

# Main function to call
def assign_basic_tracks(df, time_window_sec=30, dist_threshold=50, min_points=5):
    TIME_WINDOW = timedelta(seconds=time_window_sec)
    DIST_THRESHOLD = dist_threshold
    MIN_ASSOCIATION_COUNT = min_points

    df = df.sort_values(by="time").reset_index(drop=True)
    df["track_id"] = None

    untracked_measurements = []
    active_tracks = []

    for idx, row in df.iterrows():
        current_time = row["time"]
        current_position = (row["lat"], row["lon"])
        current_measurement = {
            "time": current_time,
            "position": current_position,
            "index": idx
        }

        # Try to associate with existing track
        matched = False
        for track in active_tracks:
            if current_time - track.last_time() <= TIME_WINDOW:
                if compute_distance(current_position, track.last_position()) <= DIST_THRESHOLD:
                    track.add(current_measurement)
                    df.at[idx, "track_id"] = track.id
                    matched = True
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
                new_track = Track()
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
    return df
