import json
import re
from datetime import datetime

from flask import Flask, render_template, request, jsonify, Blueprint
from sqlalchemy.orm import joinedload

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


@bp.route('/item/<unique_name>')
def item_details(unique_name):
    item = session.query(Item).filter_by(unique_name=unique_name).first()

    # Handle the case where the exact item (including enchantment level) is not found
    if not item:
        return jsonify({'error': 'Item not found'}), 404

    ingredients = []

    # Try to get the ingredients for the exact item first
    if item.ingredients:
        try:
            item_ingredients = json.loads(item.ingredients)
        except (json.JSONDecodeError, TypeError) as e:
            print(f"JSON decode error or Type error: {e}")
            item_ingredients = []
    else:
        item_ingredients = []

    # Prepare ingredients data for response
    for ingredient in item_ingredients:
        ingredient_unique_name = ingredient['ingredient']
        print(ingredient_unique_name)
        ingredient_quantity = ingredient['quantity']
        ingredient_item = session.query(Item).filter_by(unique_name=ingredient_unique_name).first()
        if ingredient_item:
            ingredients.append({
                'name': ingredient_item.en_name,
                'quantity': ingredient_quantity,
                'unique_name': ingredient_unique_name
            })

        print(ingredients)

    # Get similar items
    general_item = re.sub(r"(T\d_)|(_LEVEL\d)|(@\d)", "", item.unique_name)
    similar_items = session.query(Item).filter(Item.unique_name.contains(general_item)).all()

    data = {
        'item': item.to_dict(),
        'ingredients': ingredients,
        'similar_items': [sim_item.to_dict() for sim_item in similar_items]
    }
    return jsonify(data)


@bp.route('/calculate_craft', methods=['POST'])
def calculate_craft():
    data = request.get_json()
    unique_name = data.get('unique_name')
    quantity = int(data.get('quantity', 1))
    item = session.query(Item).filter_by(unique_name=unique_name).first_or_404()
    ingredients = []
    total_cost = 0
    if item.ingredients:
        item_ingredients = json.loads(item.ingredients)
        for ingredient in item_ingredients:
            ingredient_unique_name = ingredient['ingredient']
            ingredient_quantity = ingredient['quantity'] * quantity
            ingredient_item = session.query(Item).filter_by(unique_name=ingredient_unique_name).first()
            if ingredient_item:
                ingredient_cost = get_item_price(ingredient_unique_name) * ingredient_quantity
                total_cost += ingredient_cost
                ingredients.append({
                    'name': ingredient_item.en_name,
                    'quantity': ingredient_quantity,
                    'unique_name': ingredient_unique_name,
                    'cost': ingredient_cost
                })
    return jsonify({'ingredients': ingredients, 'total_cost': total_cost})


@bp.route('/popular_items')
def popular_items():
    popular_items = session.query(Item).limit(20).all()
    data = {'items': [item.to_dict() for item in popular_items]}
    return jsonify(data)


def get_item_price(unique_name):
    item = Item.query.filter_by(unique_name=unique_name).first()
    if item and item.prices:
        return item.prices[-1].price  # Return the latest price
    return 0


@bp.route('/item_prices/<unique_name>')
def item_prices(unique_name):
    item = session.query(Item).filter_by(unique_name=unique_name).options(joinedload(Item.prices)).first_or_404()
    prices_by_city = {}
    for price in item.prices:
        if price.city not in prices_by_city:
            prices_by_city[price.city] = []
        prices_by_city[price.city].append(price.to_dict())
    return jsonify(prices_by_city)


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

    item = Item.query.filter_by(unique_name=unique_name).first()
    if not item:
        return jsonify({'error': f'Item {unique_name} not found'}), 404

    price_data = Price(item_id=item.id, city=city, price=price, last_updated=datetime.now())
    db.session.add(price_data)
    db.session.commit()

    return jsonify({'success': 'Price updated successfully'}), 200


app.register_blueprint(bp)
