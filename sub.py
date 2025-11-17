import zmq
import influxdb_client
import time
import json
import logging
from influxdb_client import Point
from influxdb_client.client.write_api import SYNCHRONOUS

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# InfluxDB configuration
token = "Ig5hcOVgMy0CsEIISWCUvjmjtachhE6jM0m-HL1ffeSKLWWN_mmrKLANa2kN823EKmwoBLFPZlKb_p7Ta_fmaQ=="
org = "TUKE"
url = "http://influxdb:8086"
bucket = "my_db"

# Initialize InfluxDB client and write API
client = influxdb_client.InfluxDBClient(url=url, token=token, org=org)
write_api = client.write_api(write_options=SYNCHRONOUS)

# Initialize ZeroMQ SUB socket
context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.connect("tcp://proxy:5560")  # Connect to the proxy's SUB endpoint
socket.setsockopt_string(zmq.SUBSCRIBE, "")  # Subscribe to all topics

logging.debug("Connected to zmq.SUB socket and waiting for input")

while True:
    try:
        # Receive a message from the ZeroMQ socket
        message = socket.recv_string()
        logging.debug(f"Received message: {message}")

        # Parse the JSON-formatted message into a dictionary
        data = json.loads(message)
        logging.debug(f"Parsed data: {data}")

        # Create a new InfluxDB Point for the 'environment_data' measurement
        point = Point("environment_data")
        for key in ["lux1", "lux2", "lux3", "lux4", "temperature1", "temperature2", "temperature3", "temperature4"]:
            if key in data and data[key] is not None:
                point = point.field(key, float(data[key]))  # Add field to the point if it exists

        # Add a timestamp (nanoseconds)
        point = point.time(time.time_ns())

        # Write the point to InfluxDB
        write_api.write(bucket=bucket, org=org, record=point)
        logging.debug(f"Successfully written to InfluxDB: {point}")

    except Exception as e:
        logging.error(f"Error processing message: {e}")
