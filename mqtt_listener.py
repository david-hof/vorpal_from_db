import paho.mqtt.client as mqtt
import json
from datetime import datetime

# Define the polygon
polygon = [
    (35.34653, 30.91724),
    (35.46648, 30.90697),
    (35.47246, 30.97691),
    (35.35597, 30.97826),
    (35.34653, 30.91724)
]

# Point-in-polygon check
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

# Timestamped print
def log(msg):
    print(f"[{datetime.utcnow().isoformat()}Z] {msg}")

# MQTT callbacks
def on_connect(client, userdata, flags, rc):
    log(f"Connected with result code {rc}")
    client.subscribe("/device/vorpal/vorpal-service/platform/map/events")

def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload)
        msg_type = payload.get("type")

        if msg_type == "target":
            point = payload.get("point", {})
            lat = point.get("lat")
            lon = point.get("lon")

            if lat is not None and lon is not None:
                is_inside = point_in_polygon(lon, lat, polygon)
                if is_inside:
                    log(f"🔥 target INSIDE polygon: ({lat}, {lon})")
                else:
                    log(f"⛔ target OUTSIDE polygon: ({lat}, {lon})")
            else:
                log("⚠️ target message missing lat/lon")
        # ignore all other message types (e.g., "device")
    except Exception as e:
        log(f"⚠️ Failed to process message: {e}")

# MQTT client setup
client = mqtt.Client("pythonMqttLoggerTest")

client.username_pw_set("admin", "Kelasys123!")
client.on_connect = on_connect
client.on_message = on_message

# Connect to broker
client.connect("localhost", 1884, 60)

# Start loop
client.loop_forever()
