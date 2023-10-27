from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from models import tables,db
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from werkzeug.utils import secure_filename
from controller.project import project
from models.tables import Item

 
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SECRET_KEY'] = 'cse470'  # Replace with your secret key
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'jpg', 'jpeg', 'png', 'gif'}
# Initialize the SQLAlchemy instance

db.init_app(app)

#def create_app():
app.register_blueprint(project)
with app.app_context():
    db.create_all()

    
    #return app


if __name__ == '__main__':
    #app = create_app()
    app.run(debug=True, port=7777)