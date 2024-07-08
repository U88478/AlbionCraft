# fetch_recipes.py
import json
import logging
import time

import requests
from sqlalchemy.orm import sessionmaker

from models import Item, engine

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

Session = sessionmaker(bind=engine)
session = Session()

API_URL_TEMPLATE = "https://gameinfo.albiononline.com/api/gameinfo/items/{}/data/"
RATE_LIMIT_DELAY = 2  # Delay in seconds between requests


def fetch_item_data(unique_name):
    response = requests.get(API_URL_TEMPLATE.format(unique_name))
    if response.status_code == 200:
        return response.json()
    elif response.status_code == 429:
        logging.warning(f"Rate limit reached for {unique_name}. Retrying after delay.")
        time.sleep(RATE_LIMIT_DELAY)
        return fetch_item_data(unique_name)
    else:
        logging.error(f"Failed to fetch data for {unique_name} with status code {response.status_code}")
        return None


def parse_ingredients(crafting_requirements):
    if not crafting_requirements:
        return None
    ingredients = []
    for ingredient in crafting_requirements.get('craftResourceList', []):
        ingredients.append({
            'ingredient': ingredient['uniqueName'],
            'quantity': ingredient['count']
        })
    return ingredients


def update_item_with_recipe(item, data):
    if 'craftingRequirements' in data:
        ingredients = parse_ingredients(data['craftingRequirements'])
        item_power = 0
        if 'enchantments' in data and data['enchantments']:
            first_enchantment = data['enchantments'].get('enchantments', [])
            if first_enchantment:
                ench1_item_power = first_enchantment[0].get('itemPower', 0)
                item_power = ench1_item_power - 100  # Item power for ench level 0 is item power of ench level 1 minus 100

        item.ingredients = json.dumps(ingredients)
        item.item_power = item_power
        print(f"Updated item {item.unique_name} with ingredients: {ingredients} and item power: {item_power}")


def add_enchanted_items(item, data):
    if 'enchantments' in data and data['enchantments']:
        for enchantment in data['enchantments']['enchantments']:
            enchantment_level = enchantment['enchantmentLevel']
            enchanted_unique_name = f"{item.unique_name}@{enchantment_level}"
            ingredients = parse_ingredients(enchantment['craftingRequirements'])
            item_power = enchantment.get('itemPower', 'Unknown')
            new_item = Item(
                unique_name=enchanted_unique_name,
                item_power=item_power,
                tier=item.tier,
                set=item.set,
                enchantment_level=enchantment_level,
                en_name=item.en_name,
                ingredients=json.dumps(ingredients)
            )
            session.add(new_item)
            print(f"Enchanted item: {enchanted_unique_name}, Ingredients: {ingredients}, Item power: {item_power}")


def add_recipes_to_db():
    items = session.query(Item).all()

    for item in items:
        if item.enchantment_level != 0:  # Skip non-zero enchantment levels
            continue

        print(f"Processing item: {item.unique_name}")
        data = fetch_item_data(item.unique_name)
        if data:
            update_item_with_recipe(item, data)
            add_enchanted_items(item, data)

    session.commit()
    session.close()


if __name__ == '__main__':
    add_recipes_to_db()
