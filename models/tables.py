from sqlalchemy import Column, Integer, String, Float, ForeignKey
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import UserMixin
from sqlalchemy import Table, ForeignKey
from sqlalchemy.orm import relationship

db=SQLAlchemy()


volunteer_event_association = Table('volunteer_event_association', db.Model.metadata,
    db.Column('volunteer_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('event_id', db.Integer, db.ForeignKey('event.id')),
    

)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    items = db.relationship('Item', back_populates='seller')
    user_type = db.Column(db.String(20), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    joined_events = db.relationship('Event', secondary=volunteer_event_association, back_populates='volunteers')
    reviews = relationship('EventReview', back_populates='user')




 
    def __init__(self, username, email, password, user_type,is_admin):
        self.username = username
        self.email = email
        self.password = password
        self.user_type = user_type
        self.is_admin=is_admin


    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"




class Item(db.Model):
    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    description = Column(String(200), nullable=True)
    price = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False, default=1) 
    image_path = Column(String(255), nullable=True)
    seller_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    seller = db.relationship('User', back_populates='items')
    is_approved = db.Column(db.Boolean, default=False)


 


    def __init__(self, title, description, price,quantity, image_path,seller_id,is_approved):
        self.title = title
        self.description = description
        self.price = price
        self.quantity=quantity
        self.image_path = image_path
        self.seller_id = seller_id
        self.is_approved=is_approved


class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    is_approved = db.Column(db.Boolean, default=False)




class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    image_path = Column(String(255), nullable=True)
    location = db.Column(db.String(100), nullable=True)
    is_approved = db.Column(db.Boolean, default=False)
    volunteers = db.relationship('User', secondary=volunteer_event_association, back_populates='joined_events', cascade='all, delete')

class HistoryEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    image_path = Column(String(255), nullable=True)
    location = db.Column(db.String(100), nullable=True)
    reviews = relationship('EventReview', back_populates='history_event')





class Vlog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    youtube_link = db.Column(db.String(100), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    is_approved = db.Column(db.Boolean, default=False)


    def get_embedded_link(self):
        return f"https://www.youtube.com/embed/{self.youtube_link.split('/')[-1]}"

class Participant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)

    # Add any additional fields if necessary



class EventReview(db.Model):
    id = Column(Integer, primary_key=True)
    rating = Column(Integer, nullable=False)
    review_text = Column(String(255), nullable=True)

    # Foreign keys
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    history_event_id = Column(Integer, ForeignKey('history_event.id'), nullable=False)

    # Relationship with User and HistoryEvent tables
    user = relationship('User', back_populates='reviews')
    history_event = relationship('HistoryEvent', back_populates='reviews')

    # Additional columns
    usertype = Column(String(50), nullable=False)  # Assuming 'event maker' or 'volunteer'
    name = Column(String(100), nullable=False) 




