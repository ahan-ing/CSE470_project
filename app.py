from flask import Flask,render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from models import tables,db
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from werkzeug.utils import secure_filename
from controller.project import project
from models.tables import Item,User,db,Article
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
 
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SECRET_KEY'] = 'cse470'  
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'jpg', 'jpeg', 'png', 'gif'}

db.init_app(app)


login_manager = LoginManager(app)
login_manager.login_view = 'project.login' 


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


app.register_blueprint(project)
with app.app_context():
    db.create_all()

    
   

if __name__ == '__main__':
    app.run(debug=True, port=7777)