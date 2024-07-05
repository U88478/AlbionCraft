import logging

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from models import db

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s',
                    filename=r'app\script_logs.log', filemode='w')

Base = declarative_base()


class Item(db.Model):
    __tablename__ = 'items'
    id = db.Column(db.Integer, primary_key=True)
    unique_name = db.Column(db.String(50), nullable=False)
    tier = db.Column(db.Integer, nullable=False)
    set = db.Column(db.String(50), nullable=True)
    enchantment_level = db.Column(db.Integer, nullable=True)
    en_name = db.Column(db.String(50), nullable=False)
    ingredient1 = db.Column(db.String(50), nullable=True)
    ingredient2 = db.Column(db.String(50), nullable=True)
    ingredient3 = db.Column(db.String(50), nullable=True)
    quantity1 = db.Column(db.Integer, nullable=True)
    quantity2 = db.Column(db.Integer, nullable=True)
    quantity3 = db.Column(db.Integer, nullable=True)

    prices = db.relationship("Price", back_populates="item")
    recipes = db.relationship("Recipe", back_populates="item")

    def __repr__(self):
        return f"<Item(unique_name={self.unique_name}, en_name={self.en_name})>"

    def to_dict(self):
        return {
            'id': self.id,
            'unique_name': self.unique_name,
            'tier': self.tier,
            'set': self.set,
            'enchantment_level': self.enchantment_level,
            'en_name': self.en_name,
            'ingredient1': self.ingredient1,
            'ingredient2': self.ingredient2,
            'ingredient3': self.ingredient3,
            'quantity1': self.quantity1,
            'quantity2': self.quantity2,
            'quantity3': self.quantity3
        }


class Price(db.Model):
    __tablename__ = 'prices'
    id = db.Column(db.Integer, db.Sequence('price_id_seq'), primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'))
    city = db.Column(db.String(50))
    price = db.Column(db.Float)
    last_updated = db.Column(db.Date)

    item = db.relationship("Item", back_populates="prices")


class Recipe(db.Model):
    __tablename__ = 'recipes'
    id = db.Column(db.Integer, db.Sequence('recipe_id_seq'), primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'))
    resource_name = db.Column(db.String(50))
    resource_count = db.Column(db.Integer)

    item = db.relationship("Item", back_populates="recipes")


# Create an engine that stores data in the local directory's albion_items.db file.
engine = create_engine('sqlite:///albion_items.db')

# Create all tables in the engine.
Base.metadata.create_all(engine)

# Bind the engine to the sessionmaker.
Session = sessionmaker(bind=engine)
session = Session()
