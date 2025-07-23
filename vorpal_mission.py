import paho.mqtt.client as mqtt
import json
from datetime import datetime, timedelta
from geopy.distance import geodesic

# Parameters
POLYGON = [
    (35.34653, 30.91724),
    (35.46648, 30.90697),
    (35.47246, 30.97691),
    (35.35597, 30.97826),
    (35.34653, 30.91724),
]
TRACKING_WINDOW_SEC = 30
DISTANCE_THRESHOLD_METERS = 100
MIN_MESSAGES_FOR_TRACK = 3

PRINT_DEVICE_MESSAGES = True

# In-memory buffer of recent targets inside polygon
recent_targets = []


# --- Utilities ---
def log(msg):
    print(f"[{datetime.utcnow().isoformat()}Z] {msg}")


def point_in_polygon(x, y, poly):
    num = len(poly)
    j = num - 1
    inside = False
    for i in range(num):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi + 1e-12) + xi):
            inside = not inside
        j = i
    return inside


def compute_distance(p1, p2):
    return geodesic(p1, p2).meters


# --- Core logic ---
def handle_target_message(payload):
    global recent_targets

    point = payload.get("point", {})
    lat = point.get("lat")
    lon = point.get("lon")
    timestamp = payload.get("time")

    if lat is None or lon is None or timestamp is None:
        log("⚠️ target message missing lat/lon/time")
        return

    dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))

    if not point_in_polygon(lon, lat, POLYGON):
        log(f"⛔ target OUTSIDE polygon: ({lat}, {lon})")
        return

    log(f"🔥 target INSIDE polygon: ({lat}, {lon}) at {dt.isoformat()}")

    # Add to buffer
    recent_targets.append((dt, lat, lon))

    # Clean old entries
    recent_targets = [
        (t, la, lo) for (t, la, lo) in recent_targets
        if (dt - t).total_seconds() <= TRACKING_WINDOW_SEC
    ]

    # Check for cluster
    count = 0
    for (t2, la2, lo2) in recent_targets:
        if (dt - t2).total_seconds() <= TRACKING_WINDOW_SEC:
            if compute_distance((lat, lon), (la2, lo2)) <= DISTANCE_THRESHOLD_METERS:
                count += 1

    if count >= MIN_MESSAGES_FOR_TRACK:
        log(f"✅ TRACK DECLARED with {count} close messages")
        trigger_camera_action((lat, lon))


# --- Stub for camera logic ---
def trigger_camera_action(position):
    # Future: pick best camera from list
    log(f"🎯 Triggering camera to look at {position}")
    # Placeholder for ONVIF command
    # e.g., move_camera_to(position)


# --- MQTT Callbacks ---
def on_connect(client, userdata, flags, rc):
    log(f"Connected with result code {rc}")
    client.subscribe("/device/vorpal/vorpal-service/platform/map/events")


def handle_device_message(payload):
    log(f"📡 device message received: {json.dumps(payload)}")


def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload)
        msg_type = payload.get("type")
        if msg_type == "target":
            handle_target_message(payload)
        elif msg_type == "device" and PRINT_DEVICE_MESSAGES:
            handle_device_message(payload)
    except Exception as e:
        log(f"⚠️ Failed to process message: {e}")


# --- MQTT Setup ---
client = mqtt.Client("pythonMqttLoggerTest")
client.username_pw_set("admin", "Kelasys123!")
client.on_connect = on_connect
client.on_message = on_message
client.connect("localhost", 1884, 60)
client.loop_forever()
print("hi")
