from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from models.tables import User  
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'  
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

with app.app_context():
    db.create_all()
    hashed_password = bcrypt.generate_password_hash('admin12345').decode('utf-8')
    admin_user = User(username='admin', email='admin@example.com', password=hashed_password, user_type='admin', is_admin=True)
    
    db.session.add(admin_user)
    db.session.commit()

    print('Admin user created successfully.')