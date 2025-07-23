import time
import numpy as np
from collections import deque
from datetime import datetime, timedelta
from geopy.distance import geodesic


MIN_POINTS = 2
MAX_DISTANCE_METERS = 100
MAX_BUFFER_SECONDS = 30


track_buffer = deque()  # Stores (timestamp, (lat, lon))


def read_sys_msg():
    raw = {
        "type": "target",
        "point": {"lat": 30.96541 + np.random.randn() * 0.00005,
                  "lon": 35.404549 + np.random.randn() * 0.00005},
        "time": datetime.utcnow().isoformat()
    }
    if raw.get("type") != "target":
        return None
    try:
        point = raw.get("point", {})
        pos = (point["lat"], point["lon"])
        timestamp = datetime.fromisoformat(raw["time"])
    except Exception:
        return None
    return {"pos": pos, "time": timestamp}



def decide_if_real_track(meas):
    global track_buffer
    pos = (meas["lat"], meas["lon"])
    t = datetime.fromisoformat(meas["time"])

    # Keep only recent points in buffer
    track_buffer.append((t, pos))
    while track_buffer and (t - track_buffer[0][0]).total_seconds() > MAX_BUFFER_SECONDS:
        track_buffer.popleft()

    # Check if at least MIN_POINTS are within MAX_DISTANCE_METERS from each other
    if len(track_buffer) < MIN_POINTS:
        return False

    for i in range(len(track_buffer) - MIN_POINTS + 1):
        sub_seq = list(track_buffer)[i:i+MIN_POINTS]
        ref_point = sub_seq[0][1]
        if all(geodesic(ref_point, p[1]).meters < MAX_DISTANCE_METERS for p in sub_seq):
            return True

    return False


def choose_camera(track_position):
    pass


def point_camera(camera_id, target_position):
    pass


def main_loop():
    while True:
        msg = read_sys_msg()
        if msg is None:
            continue

        print(f"Received target at {msg['pos']}")

        if decide_if_real_track(msg):
            print("✅ Real track detected.")
            choose_camera(msg["pos"])
            point_camera("CAM_1", msg["pos"])
        else:
            print("Not a real track yet.")


if __name__ == "__main__":
    main_loop()
