import re

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import Item, Base  # Assuming models.py is in the same directory or appropriately imported


def is_resource(unique_name):
    # Define patterns for resources (logs, planks, ores, fibers, hides, stones)
    resource_patterns = [
        r'T\d+_WOOD', r'T\d+_PLANKS', r'T\d+_ORE', r'T\d+_METALBAR',
        r'T\d+_FIBER', r'T\d+_CLOTH', r'T\d+_HIDE', r'T\d+_LEATHER',
        r'T\d+_ROCK', r'T\d+_STONEBLOCK'
    ]

    for pattern in resource_patterns:
        if re.match(pattern, unique_name):
            return True
    return False


def process_file(filename):
    with open(filename, 'r') as file:
        lines = file.readlines()

    items = []
    for line in lines:
        parts = line.split(':', 1)
        if len(parts) == 2:
            id_part, rest = parts
            rest_parts = rest.strip().rsplit(' ', 1)
            if len(rest_parts) == 2:
                unique_name, name = rest_parts
                unique_name = unique_name.strip().split("@")[0]
                name = name.strip()
                items.append((unique_name, name))
            else:
                print(f"Skipping line due to unexpected format: {line.strip()}")
    return items


def save_resources_to_db(items, session):
    for unique_name, name in items:
        if is_resource(unique_name):
            tier = int(unique_name.split('_')[0][1])
            enchantment_level = int(re.search(r'_LEVEL(\d+)', unique_name).group(1)) if '_LEVEL' in unique_name else 0
            item = Item(
                unique_name=unique_name,
                en_name=name,
                tier=tier,
                enchantment_level=enchantment_level
            )
            session.add(item)
    session.commit()


def main():
    filename = 'items.txt'
    items = process_file(filename)

    # Database connection
    engine = create_engine('sqlite:///albion_items.db')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    # Save resources to the database
    save_resources_to_db(items, session)
    session.close()


if __name__ == "__main__":
    main()
