from sqlalchemy import Column, Integer, String, Float, ForeignKey, Sequence, Date
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Item(Base):
    __tablename__ = 'items'
    id = Column(Integer, primary_key=True)
    unique_name = Column(String(50), nullable=False)
    item_power = Column(Integer, nullable=True)
    tier = Column(Integer, nullable=True)
    set = Column(String(50), nullable=True)
    enchantment_level = Column(Integer, nullable=True)
    en_name = Column(String(50), nullable=False)
    ingredients = Column(String(255), nullable=True)

    prices = relationship("Price", back_populates="item")

    def __repr__(self):
        return f"<Item(unique_name={self.unique_name}, en_name={self.en_name})>"

    def to_dict(self):
        return {
            'id': self.id,
            'unique_name': self.unique_name,
            'en_name': self.en_name,
            'tier': self.tier,
            'set': self.set,
            'item_power': self.item_power,
            'enchantment_level': self.enchantment_level,
            'ingredients': self.ingredients,
            'prices': [price.to_dict() for price in self.prices]  # Include prices
        }


class Price(Base):
    __tablename__ = 'prices'
    id = Column(Integer, Sequence('price_id_seq'), primary_key=True)
    item_id = Column(Integer, ForeignKey('items.id'))
    city = Column(String(50))
    price = Column(Float)
    last_updated = Column(Date)

    item = relationship("Item", back_populates="prices")

    def to_dict(self):
        return {
            'city': self.city,
            'price': self.price,
            'last_updated': self.last_updated.strftime('%Y-%m-%d %H:%M:%S')
        }
