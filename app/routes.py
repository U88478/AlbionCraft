import json
import re
from datetime import datetime

import requests
from flask import Flask, render_template, request, jsonify, Blueprint

from app.extensions import db
from models.models import Item, Price

app = Flask(__name__)
bp = Blueprint('routes', __name__)
session = db.session


@bp.route('/')
def home():
    return render_template('main.html')


@bp.route('/search')
def search_items():
    query = request.args.get('query', '')
    if query:
        items = session.query(Item).filter(Item.en_name.ilike(f'%{query}%')).all()
    else:
        items = []
    data = {'items': [item.to_dict() for item in items]}
    return jsonify(data)


def fetch_item_data(unique_name):
    item = session.query(Item).filter_by(unique_name=unique_name).first()
    if not item:
        return

    # Prepare item details
    ingredients = []
    if item.ingredients:
        try:
            item_ingredients = json.loads(item.ingredients)
        except (json.JSONDecodeError, TypeError):
            item_ingredients = []
    else:
        item_ingredients = []

    for ingredient in item_ingredients:
        ingredient_unique_name = ingredient['ingredient']
        ingredient_quantity = ingredient['quantity']
        ingredient_item = session.query(Item).filter_by(unique_name=ingredient_unique_name).first()
        if ingredient_item:
            ingredients.append({
                'name': ingredient_item.en_name,
                'quantity': ingredient_quantity,
                'unique_name': ingredient_unique_name
            })

    general_item = re.sub(r"(T\d_)|(_LEVEL\d)|(@\d)", "", item.unique_name)
    similar_items = session.query(Item).filter(Item.unique_name.contains(general_item)).all()

    # Fetch latest Bridgewatch price
    bridgewatch_price = None
    bridgewatch_prices = [p for p in item.prices if p.city == 'Bridgewatch']
    if bridgewatch_prices:
        latest_bridgewatch_entry = max(bridgewatch_prices, key=lambda x: x.last_updated)
        bridgewatch_price = latest_bridgewatch_entry.price

    # Return item data
    item_data = {
        'unique_name': item.unique_name,
        'en_name': item.en_name,
        'tier': item.tier,
        'set': item.set,
        'item_power': item.item_power,
        'enchantment_level': item.enchantment_level,
        'price': bridgewatch_price,
        'ingredients': ingredients,
        'similar_items': [
            {'unique_name': si.unique_name, 'en_name': si.en_name, 'icon_url': f'https://render.albiononline.com/v1/item/{si.unique_name}'}
            for si in similar_items
        ]
    }

    return item_data


@bp.route('/item/<unique_name>')
def item_details(unique_name):
    item_data = fetch_item_data(unique_name)
    return render_template('item_page.html', item_data=item_data)


@bp.route('/api/item/<unique_name>')
def api_item_details(unique_name):
    item_data = fetch_item_data(unique_name)
    return jsonify(item_data)


@bp.route('/popular_items')
def popular_items():
    popular_items = session.query(Item).limit(20).all()
    data = {'items': [item.to_dict() for item in popular_items]}
    return jsonify(data)


def get_item_price(unique_name):
    item = session.query(Item).filter_by(unique_name=unique_name).first()
    if item and item.prices:
        return item.prices[-1].price
    return 0


@bp.route('/item_prices/<unique_name>', methods=['GET'])
def get_item_prices(unique_name):
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    city = request.args.get('city')

    query = session.query(Price).join(Item).filter(Item.unique_name == unique_name)
    if start_date:
        query = query.filter(Price.last_updated >= start_date)
    if end_date:
        query = query.filter(Price.last_updated <= end_date)
    if city:
        query = query.filter(Price.city == city)

    prices = query.order_by(Price.last_updated).all()
    prices_by_city = {}
    for price in prices:
        if price.city not in prices_by_city:
            prices_by_city[price.city] = []
        prices_by_city[price.city].append(price.to_dict())

    return jsonify(prices_by_city)


def fetch_current_prices(unique_name, cities):
    url = f"https://west.albion-online-data.com/api/v2/stats/prices/{unique_name}.json?locations={','.join(cities)}"
    response = requests.get(url)
    return response.json()


def store_prices(unique_name, current_prices_data):
    item = session.query(Item).filter_by(unique_name=unique_name).first()
    if not item:
        return

    for entry in current_prices_data:
        if 'sell_price_min' in entry and entry['sell_price_min'] > 0:
            new_price = Price(
                item_id=item.id,
                city=entry['city'],
                price=entry['sell_price_min'],
                last_updated=datetime.strptime(entry['sell_price_min_date'], '%Y-%m-%dT%H:%M:%S')
            )
            session.add(new_price)
    session.commit()


@bp.route('/fetch_prices/<unique_name>')
def fetch_prices(unique_name):
    cities = ['Caerleon', 'Bridgewatch', 'Lymhurst', 'Martlock', 'Thetford', 'Fort Sterling']

    current_prices = fetch_current_prices(unique_name, cities)
    store_prices(unique_name, current_prices)

    return jsonify({'message': 'Prices fetched and stored successfully'})


@bp.route('/update_price', methods=['POST'])
def update_price():
    data = request.json
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    unique_name = data.get('unique_name')
    city = data.get('city')
    price = data.get('price')

    if not unique_name or not city or price is None:
        return jsonify({'error': 'Missing data'}), 400

    item = session.query(Item).filter_by(unique_name=unique_name).first()
    if not item:
        return jsonify({'error': f'Item {unique_name} not found'}), 404

    price_data = Price(item_id=item.id, city=city, price=price, last_updated=datetime.now())
    session.add(price_data)
    session.commit()

    return jsonify({'success': 'Price updated successfully'}), 200


app.register_blueprint(bp)

if __name__ == '__main__':
    with app.app_context():
        app.run(debug=True)
