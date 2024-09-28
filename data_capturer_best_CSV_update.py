import os
import time
import json
import queue
import pyshark
import pandas as pd
import threading
import asyncio
import concurrent.futures
import logging

# Configure logging to track packet capture and errors
logging.basicConfig(filename='packet_capture.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Define the broker, port, and topic you want to filter for
BROKER_IP = "192.168.9.237"
PORT = 1883  # MQTT port
TOPIC = "v1/devices/me/telemetry"

# Define the directory where the attack file and CSV will be stored
directory = os.path.dirname(__file__)  # Use the script's directory

# Define the file path for the current attack type
attack_file = os.path.join(directory, 'current_attack.txt')

# Define the base name for the CSV file
csv_base_name = os.path.join(directory, 'captured_data_loop')

# Set the file size limit (e.g., 10 MB)
FILE_SIZE_LIMIT = 10 * 1024 * 1024  # 10 MB

# Initialize a counter to track the CSV file versions
csv_counter = 1

# Initialize a queue to hold packets for processing
packet_queue = queue.Queue()

# Function to read the current attack type from the attack_file
def read_attack_type():
    if os.path.exists(attack_file):
        with open(attack_file, 'r') as f:
            return f.read().strip()
    return 'legitimate'

# Function to handle each packet and save it
def process_packet(mqtt_data):
    try:
        # Save the captured data to CSV
        save_to_csv(mqtt_data)
    except Exception as e:
        logging.error(f"Error processing packet: {e}")
        print(json.dumps({"status": "error", "message": f"Error processing packet: {e}"}))

# Save data to CSV function with file rotation
def save_to_csv(data):
    global csv_counter
    csv_path = f"{csv_base_name}_{csv_counter}.csv"

    # Check if the file size has exceeded the limit
    if os.path.exists(csv_path) and os.path.getsize(csv_path) > FILE_SIZE_LIMIT:
        # Increment the file counter to create a new file
        csv_counter += 1
        csv_path = f"{csv_base_name}_{csv_counter}.csv"
        logging.info(f"File size limit reached. Creating new file: {csv_path}")

    df = pd.DataFrame([data])

    # Check if the file exists
    if not os.path.isfile(csv_path):
        df.to_csv(csv_path, mode='w', header=True, index=False)
    else:
        df.to_csv(csv_path, mode='a', header=False, index=False)

# Batch Processing for incoming packets
def process_packets_in_batch():
    batch_size = 100  # Increased batch size to handle high-performance attacks
    while True:
        batch = []
        while not packet_queue.empty() and len(batch) < batch_size:
            batch.append(packet_queue.get())

        if batch:
            for mqtt_data in batch:
                process_packet(mqtt_data)

        time.sleep(0.001)  # Reduced sleep time to handle higher packet rates

# Capture the packets using pyshark
def start_capture():
    logging.info("Starting packet capture")
    asyncio.set_event_loop(asyncio.new_event_loop())
    # Broaden the filter to capture all TCP traffic
    capture = pyshark.LiveCapture(interface='enp3s0', display_filter='tcp')
    
    # Continuous capture without pause
    try:
        capture.apply_on_packets(packet_callback)
    except Exception as e:
        logging.error(f"Error during capture: {e}")
        print(json.dumps({"status": "error", "message": f"Error during capture: {e}"}))

# Post-processing to extract relevant MQTT packets from the broader TCP capture
def packet_callback(packet):
    try:
        # Ensure both TCP and MQTT layers are present
        if 'MQTT' in packet and 'TCP' in packet:
            mqtt_layer = packet['MQTT']
            tcp_layer = packet['TCP']

            # Extract TCP and MQTT fields, with default values if not found
            tcp_flags = getattr(tcp_layer, 'flags', '0x0000')
            tcp_time_delta = packet.sniff_time.timestamp()
            tcp_len = getattr(tcp_layer, 'len', '0')
            mqtt_conack_flags = getattr(mqtt_layer, 'conack_flags', '0')
            mqtt_conflag_cleansess = getattr(mqtt_layer, 'conflag_cleansess', '0')
            mqtt_conflags = getattr(mqtt_layer, 'conflags', '0')
            mqtt_dupflag = getattr(mqtt_layer, 'dupflag', '0')
            mqtt_hdrflags = getattr(mqtt_layer, 'hdrflags', '0x00')
            mqtt_kalive = getattr(mqtt_layer, 'kalive', '0')
            mqtt_msg = getattr(mqtt_layer, 'msgid', '0')
            mqtt_qos = getattr(mqtt_layer, 'qos', '0')

            # Filter packets based on destination IP, port, and topic
            if packet.ip.dst == BROKER_IP and tcp_layer.dstport == str(PORT) and mqtt_layer.topic == TOPIC:
                mqtt_data = {
                    "timestamp": tcp_time_delta,
                    "tcp_flags": tcp_flags,
                    "tcp_time_delta": tcp_time_delta,
                    "tcp_len": tcp_len,
                    "mqtt_conack_flags": mqtt_conack_flags,
                    "mqtt_conflag_cleansess": mqtt_conflag_cleansess,
                    "mqtt_conflags": mqtt_conflags,
                    "mqtt_dupflag": mqtt_dupflag,
                    "mqtt_hdrflags": mqtt_hdrflags,
                    "mqtt_kalive": mqtt_kalive,
                    "mqtt_msg": mqtt_msg,
                    "mqtt_qos": mqtt_qos,
                    "label": read_attack_type()
                }

                # Print captured data
                print(json.dumps({"status": "info", "message": "Captured Data", "data": mqtt_data}))
                logging.info(f"Captured Data: {mqtt_data}")

                packet_queue.put(mqtt_data)

    except AttributeError as e:
        # Log the error but continue processing, and only assign default values to missing attributes
        logging.error(f"Error accessing packet fields: {e}")

        mqtt_data = {
            "timestamp": packet.sniff_time.timestamp(),
            "tcp_flags": getattr(tcp_layer, 'flags', '0x0000'),
            "tcp_time_delta": packet.sniff_time.timestamp(),
            "tcp_len": getattr(tcp_layer, 'len', '0'),
            "mqtt_conack_flags": getattr(mqtt_layer, 'conack_flags', '0'),
            "mqtt_conflag_cleansess": getattr(mqtt_layer, 'conflag_cleansess', '0'),
            "mqtt_conflags": getattr(mqtt_layer, 'conflags', '0'),
            "mqtt_dupflag": getattr(mqtt_layer, 'dupflag', '0'),
            "mqtt_hdrflags": getattr(mqtt_layer, 'hdrflags', '0x00'),
            "mqtt_kalive": getattr(mqtt_layer, 'kalive', '0'),
            "mqtt_msg": getattr(mqtt_layer, 'msgid', '0'),
            "mqtt_qos": getattr(mqtt_layer, 'qos', '0'),
            "label": read_attack_type()
        }

        print(json.dumps({"status": "info", "message": "Captured Data with some default values", "data": mqtt_data}))
        logging.info(f"Captured Data with some default values: {mqtt_data}")
        packet_queue.put(mqtt_data)


if __name__ == "__main__":
    # Use a thread pool to handle packet processing
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        capture_thread = threading.Thread(target=start_capture)
        capture_thread.start()

        processing_thread = threading.Thread(target=process_packets_in_batch)
        processing_thread.start()

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logging.info("Stopping capture")
            print(json.dumps({"status": "info", "message": "Stopping capture..."}))
            capture_thread.join()
            processing_thread.join()
