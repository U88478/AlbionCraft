import json
import logging
import re
import sys
from datetime import datetime
from os.path import dirname, abspath, exists

import pyshark
import requests

sys.path.append(dirname(dirname(abspath(__file__))))

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Dictionary to store partial messages
message_buffer = {}
current_city = "Unknown"
last_logged_city = "Unknown"

# Constants for mapping market location IDs to city names
LOCATION_ID_TO_CITY = {
    "0007": "Thetford",
    "1002": "Lymhurst",
    "2004": "Bridgewatch",
    "3005": "Caerleon",
    "3008": "Martlock",
    "4002": "Fort Sterling",
}

# Ensure the last location file exists
location_file_path = 'last_location.txt'
if not exists(location_file_path):
    with open(location_file_path, 'w') as file:
        file.write("Unknown")


# Function to clean and extract JSON from mixed payload
def extract_json_from_payload(payload):
    json_like = re.findall(r'\{.*?}', payload)
    for json_str in json_like:
        try:
            json_data = json.loads(json_str)
            return json_data
        except json.JSONDecodeError:
            continue
    return None


# Function to reassemble fragmented messages
def reassemble_message(packet_id, ascii_payload):
    if packet_id in message_buffer:
        message_buffer[packet_id] += ascii_payload
        json_payload = extract_json_from_payload(message_buffer[packet_id])
        if json_payload:
            del message_buffer[packet_id]
            return json_payload
    else:
        message_buffer[packet_id] = ascii_payload
    return None


# Function to extract and store relevant information from packets
def extract_info_from_packet(packet):
    global current_city, last_logged_city
    try:
        if 'IP' in packet and 'UDP' in packet:
            src_ip = packet.ip.src
            payload_hex = packet.udp.payload.replace(':', '')
            raw_payload = bytes.fromhex(payload_hex)
            ascii_payload = raw_payload.decode('utf-8', errors='ignore')

            if src_ip.startswith("5.188.125.14") or src_ip.startswith("5.188.125.37"):
                # Location packet
                location_id_match = re.search(r'20(07|02|04|05|08|02)', ascii_payload)
                if location_id_match:
                    location_id = location_id_match.group(0)
                    current_city = LOCATION_ID_TO_CITY.get(location_id, "Unknown")
                    if current_city != last_logged_city:
                        logging.info(f"Current Location: {current_city}")
                        last_logged_city = current_city
                        save_last_location(current_city)
            elif src_ip.startswith("5.188.125.15"):
                # Market packet
                packet_id = f"{packet.ip.src}:{packet.udp.srcport}->{packet.ip.dst}:{packet.udp.dstport}"
                json_payload = extract_json_from_payload(ascii_payload)
                if not json_payload:
                    json_payload = reassemble_message(packet_id, ascii_payload)
                if json_payload:
                    unique_name = json_payload.get("ItemTypeId", "N/A")
                    unit_price = int(json_payload.get("UnitPriceSilver", 0)) // 10000
                    city = current_city

                    logging.info(f"Data: {unique_name}, {unit_price}, {city}")
                    send_price_data(unique_name, city, unit_price)
    except Exception as e:
        logging.error(f"Error processing packet: {e}")


# Function to save the last location to a file
def save_last_location(location):
    try:
        with open(location_file_path, 'w') as file:
            file.write(location)
    except Exception as e:
        logging.error(f"Error saving last location: {e}")


# Function to load the last location from a file
def load_last_location():
    global current_city, last_logged_city
    try:
        with open(location_file_path, 'r') as file:
            last_logged_city = file.read().strip()
            current_city = last_logged_city
            logging.info(f"Loaded last known location: {current_city}")
    except Exception as e:
        logging.error(f"Error loading last location: {e}")


# Function to send price data to the server
def send_price_data(unique_name, city, price):
    try:
        url = 'https://quasarex.pythonanywhere.com/update_price'
        data = {
            'unique_name': unique_name,
            'city': city,
            'price': price
        }
        response = requests.post(url, json=data)
        if response.status_code == 200:
            logging.info(f"Successfully updated price for {unique_name}")
        else:
            logging.error(f"Failed to update price: {response.status_code} - {response.text}")
    except Exception as e:
        logging.error(f"Error sending price data: {e}")


# Function to capture packets continuously in real-time
def capture_packets():
    load_last_location()  # Load the last known location at the start
    try:
        capture = pyshark.LiveCapture(interface='WiFi 2', display_filter='udp')
        for packet in capture.sniff_continuously():
            extract_info_from_packet(packet)
    except Exception as e:
        logging.error(f"Error in packet capture: {e}")


# Run the packet capture
capture_packets()
