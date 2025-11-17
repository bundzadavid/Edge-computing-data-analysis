import logging
import zmq
import requests
import json
import time

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# URL for the GET request
url = "http://147.232.60.230:5001/updateHouseUI"

# Initialize ZeroMQ context and PUB socket
context = zmq.Context()
socket = context.socket(zmq.PUB)
socket.connect("tcp://proxy:5559")
logging.debug("PUB is ready and sending messages to the proxy...")

# Time interval for logging (5 seconds)
log_interval = 5
last_logged = time.time()

while True:
    try:
        # Send GET request to the smart house API
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            
            # Get the 'sensorsData' dictionary from the JSON response
            sensors_data = data.get('sensorsData', {})
            
            # Extract lux and temperature values from the 'sensorsData'
            lux_values = {f'lux{i}': sensors_data.get(f'lux{i}', None) for i in range(1, 5)}
            temperature_values = {f'temperature{i}': sensors_data.get(f'temperature{i}', None) for i in range(1, 5)}

            # Create the message to send via ZeroMQ
            message = {
                **lux_values,
                **temperature_values
            }

            # Log incoming data if the logging interval has passed
            current_time = time.time()
            if current_time - last_logged >= log_interval:
                logging.debug(f"Received data: {data}")
                last_logged = current_time

            # Send the message over ZeroMQ
            socket.send_string(json.dumps(message))

            time.sleep(5)  # Wait before sending the next GET request

        else:
            logging.error(f"Failed to fetch data. Status code: {response.status_code}")

    except Exception as e:
        logging.error(f"Error occurred: {e}")
        time.sleep(5)
