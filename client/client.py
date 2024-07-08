import json
import logging
import re
import sys
from datetime import datetime
from os.path import dirname, abspath, exists

import pyshark
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.append(dirname(dirname(abspath(__file__))))
from models.models import Item, Price

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Database setup
engine = create_engine('sqlite:///../models/albion_items.db')
Session = sessionmaker(bind=engine)
session = Session()

# Dictionary to store partial messages
message_buffer = {}
current_city = "Unknown"
last_logged_city = "Unknown"  # Track the last logged location

# Constants for mapping market location IDs to city names
LOCATION_ID_TO_CITY = {
    "0007": "Thetford Market",
    "1002": "Lymhurst Market",
    "2004": "Bridgewatch Market",
    "3005": "Caerleon Market",
    "3008": "Martlock Market",
    "4002": "Fort Sterling Market",
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
                        last_logged_city = current_city  # Update the last logged location
                        save_last_location(current_city)  # Save the location to the database
            elif src_ip.startswith("5.188.125.15"):
                # Market packet
                packet_id = f"{packet.ip.src}:{packet.udp.srcport}->{packet.ip.dst}:{packet.udp.dstport}"
                json_payload = extract_json_from_payload(ascii_payload)
                if not json_payload:
                    json_payload = reassemble_message(packet_id, ascii_payload)
                if json_payload:
                    unique_name = json_payload.get("ItemTypeId", "N/A")
                    unit_price = int(json_payload.get("UnitPriceSilver", 0)) // 10000
                    total_price = int(json_payload.get("TotalPriceSilver", 0)) // 10000
                    amount = json_payload.get("Amount", 0)
                    tier = json_payload.get("Tier", 0)
                    seller_name = json_payload.get("SellerName", "N/A")
                    city = current_city[:-7]  # Remove the last 7 characters to get the city name

                    logging.info(
                        f"Data: {unique_name}, {unit_price}, {total_price}, {amount}, {tier}, {seller_name}, {city}")
                    save_price_data(unique_name, city, unit_price)  # Save the price to the database
    except Exception as e:
        logging.error(f"Error processing packet: {e}")


# Function to save the last location to the database
def save_last_location(location):
    try:
        with open(location_file_path, 'w') as file:
            file.write(location)
    except Exception as e:
        logging.error(f"Error saving last location: {e}")


# Function to load the last location from the database
def load_last_location():
    global current_city, last_logged_city
    try:
        with open(location_file_path, 'r') as file:
            last_logged_city = file.read().strip()
            current_city = last_logged_city
            logging.info(f"Loaded last known location: {current_city}")
    except Exception as e:
        logging.error(f"Error loading last location: {e}")


# Function to save price data to the database
def save_price_data(unique_name, city, price):
    try:
        # Check if the item already exists
        item = session.query(Item).filter_by(unique_name=unique_name).first()
        if not item:
            logging.info(f"Item {unique_name} not found in database, skipping price save.")
            return

        # Add price data
        price_data = Price(item_id=item.id, city=city, price=price, last_updated=datetime.now())
        session.add(price_data)
        session.commit()
    except Exception as e:
        logging.error(f"Error saving price data: {e}")


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

# Close the database session when done
session.close()
