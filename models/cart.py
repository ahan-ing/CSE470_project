# models/cart.py
from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from models import db



class CartItem(db.Model):
    id = Column(Integer, primary_key=True)
    item_id = Column(Integer, ForeignKey('item.id'))
    cart_id = Column(Integer, ForeignKey('cart.id'))

class Cart(db.Model):
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    items = relationship('CartItem', backref='cart')

