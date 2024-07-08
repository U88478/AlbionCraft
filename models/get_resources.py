import json
import re
import time

import requests
from bs4 import BeautifulSoup
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
        id_part, rest = parts
        rest_parts = [i.strip() for i in rest.split(":")]
        rest_parts[0] = rest_parts[0].split("@")[0]
        if is_resource(rest_parts[0]):
            if len(rest_parts) == 2:
                unique_name = rest_parts[0].strip()
                name = rest_parts[1].strip()
                print((unique_name, name))
                items.append((unique_name, name))
            else:
                continue

    return items


def fetch_recipe(unique_name, max_retries=5):
    url = f"https://albiononline2d.com/en/item/id/{unique_name}/craftingrequirements"
    retries = 0
    while retries < max_retries:
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            retries += 1
            print(f"Error fetching recipe for {unique_name}: {e}, retrying ({retries}/{max_retries})...")
            time.sleep(2 ** retries)  # Exponential backoff
    return None


def parse_recipe(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    recipe_data = []
    try:
        tables = soup.find_all('table', {'class': 'table-striped'})
        if len(tables) < 2:
            raise ValueError("Could not find the resources table")
        resources_table = tables[1]  # The second table contains the resources
        rows = resources_table.find_all('tr')[1:]  # Skip the header row
        for row in rows:
            cols = row.find_all('td')
            if len(cols) < 3:
                raise ValueError("Row does not have enough columns")
            ingredient_unique_name = cols[0].find('a')['href'].split('/')[-1]
            quantity = int(cols[2].text.strip())
            recipe_data.append({
                'ingredient': ingredient_unique_name,
                'quantity': quantity
            })
    except Exception as e:
        print(f"Error parsing recipe: {e}")
    return recipe_data


def save_resources_to_db(items, session):
    for unique_name, name in items:
        if is_resource(unique_name):
            tier = int(unique_name.split('_')[0][1])
            enchantment_level = int(re.search(r'_LEVEL(\d+)', unique_name).group(1)) if '_LEVEL' in unique_name else 0
            item = session.query(Item).filter_by(unique_name=unique_name).first()
            if not item:
                item = Item(
                    unique_name=unique_name,
                    en_name=name,
                    tier=tier,
                    enchantment_level=enchantment_level
                )
                session.add(item)
            else:
                item.en_name = name

            print(f"Fetching recipe for {item.unique_name}")
            html_content = fetch_recipe(unique_name)
            if html_content:
                recipe = parse_recipe(html_content)
                if recipe:
                    print(f"Recipe for {item.unique_name}: {recipe}")
                    item.ingredients = json.dumps(recipe)
                    session.add(item)
                    print(f"Updated {item.unique_name} with recipe: {recipe}")

    session.commit()


def main():
    filename = 'items.txt'  # Replace with the actual path to your file
    items = process_file(filename)

    # Database connection
    engine = create_engine('sqlite:///albion_items.db')  # Replace with your database URL
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    # Save resources to the database and update recipes
    save_resources_to_db(items, session)
    session.close()


if __name__ == "__main__":
    main()
