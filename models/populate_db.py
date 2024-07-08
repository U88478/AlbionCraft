# populate_db.py
import logging
import re

from sqlalchemy.orm import sessionmaker

from models import Item, engine

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

Session = sessionmaker(bind=engine)
session = Session()


def parse_item_line(line):
    parts = line.split(':')
    if len(parts) != 3:
        logging.warning(f"Skipping line due to insufficient parts: {line.strip()}")
        return None

    id_part, unique_name_part, en_name_part = parts
    item_id = int(id_part.strip())
    unique_name = unique_name_part.strip()
    en_name = en_name_part.strip()

    tier = None
    set_ = None
    enchantment_level = 0

    # Detect and remove '@\d' part if LEVEL is present
    # if 'LEVEL' in unique_name:
    #     unique_name = re.sub(r'@\d', '', unique_name).strip()
    #     _, enchantment_level = unique_name.split('_LEVEL')
    #     enchantment_level = int(enchantment_level)
    # elif '@' in unique_name:
    #     _, enchantment_level = unique_name.split('@')
    #     enchantment_level = int(enchantment_level)

    if 'LEVEL' in unique_name or '@' in unique_name:
        return None

    tier_match = re.search(r'T(\d)', unique_name)
    if tier_match:
        tier = int(tier_match.group(1))

    set_match = re.search(r'SET(\d)', unique_name)
    if set_match:
        set_ = int(set_match.group(1))

    return {
        'id': item_id,
        'unique_name': unique_name,
        'item_power': 0,
        'tier': tier,
        'set': set_,
        'enchantment_level': enchantment_level,
        'en_name': en_name
    }


def populate_db(file_path):
    with open(file_path, 'r') as file:
        for line in file:
            if 'QUESTITEM' in line or 'UNIQUE' in line:
                continue

            item_data = parse_item_line(line)
            if item_data:
                logging.debug(f"Adding item: {item_data}")
                item = Item(**item_data)
                session.add(item)

    session.commit()
    session.close()


if __name__ == '__main__':
    populate_db('items.txt')
