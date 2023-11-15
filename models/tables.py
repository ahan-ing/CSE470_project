from sqlalchemy import Column, Integer, String, Float, ForeignKey
from flask_sqlalchemy import SQLAlchemy


db=SQLAlchemy()


class Item(db.Model):
    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    description = Column(String(200), nullable=True)
    price = Column(Float, nullable=False)
    image_path = Column(String(255), nullable=True)
  

    def __init__(self, title, description, price, image_path):
        self.title = title
        self.description = description
        self.price = price
        self.image_path = image_path

class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)