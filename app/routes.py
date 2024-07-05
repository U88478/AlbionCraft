from flask import Blueprint, render_template, request, jsonify

from models.models import Item

bp = Blueprint('routes', __name__)


@bp.route('/')
def index():
    return render_template('main.html')


@bp.route('/search')
def search_items():
    query = request.args.get('query', '')
    tier = request.args.get('tier', 'all')
    ench = request.args.get('ench', 'all')

    filters = []
    if query:
        filters.append(Item.en_name.ilike(f'%{query}%'))
    if tier != 'all' and tier:
        filters.append(Item.tier == int(tier))
    if ench != 'all' and ench:
        filters.append(Item.enchantment_level == int(ench))

    items = Item.query.filter(*filters).all()
    data = {'items': [item.to_dict() for item in items]}
    return jsonify(data)


@bp.route('/item/<unique_name>')
def item_page(unique_name):
    item = Item.query.filter_by(unique_name=unique_name).first_or_404()
    # Fetch the in-game names of the ingredients
    ingredients = []
    for ing_attr, qty_attr in [('ingredient1', 'quantity1'), ('ingredient2', 'quantity2'),
                               ('ingredient3', 'quantity3')]:
        ingredient_unique_name = getattr(item, ing_attr)
        if ingredient_unique_name:
            ingredient_item = Item.query.filter_by(unique_name=ingredient_unique_name).first()
            if ingredient_item:
                ingredients.append({
                    'name': ingredient_item.en_name,
                    'quantity': getattr(item, qty_attr),
                    'unique_name': ingredient_unique_name
                })
    return render_template('item.html', item=item, ingredients=ingredients)


@bp.route('/calculate_craft', methods=['POST'])
def calculate_craft():
    data = request.get_json()
    unique_name = data.get('unique_name')
    quantity = int(data.get('quantity', 1))

    item = Item.query.filter_by(unique_name=unique_name).first_or_404()

    ingredients = []
    for ing_attr, qty_attr in [('ingredient1', 'quantity1'), ('ingredient2', 'quantity2'),
                               ('ingredient3', 'quantity3')]:
        ingredient_unique_name = getattr(item, ing_attr)
        if ingredient_unique_name:
            ingredient_item = Item.query.filter_by(unique_name=ingredient_unique_name).first()
            if ingredient_item:
                ingredients.append({
                    'name': ingredient_item.en_name,
                    'quantity': getattr(item, qty_attr) * quantity,
                    'unique_name': ingredient_unique_name
                })

    total_cost = sum(ing['quantity'] for ing in ingredients) * 10  # Example cost calculation

    return jsonify({'ingredients': ingredients, 'total_cost': total_cost})
