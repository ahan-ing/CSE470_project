from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, FloatField, SubmitField,PasswordField,DateTimeField,BooleanField,IntegerField  
from wtforms.validators import DataRequired, Email, Length,URL, EqualTo, Email,NumberRange

class SellItemForm(FlaskForm):
    title = StringField('Product name', validators=[DataRequired()])
    description = TextAreaField('Product description')
    price = FloatField('Selling price', validators=[DataRequired()])
    quantity=StringField('Quantity', validators=[DataRequired()])
    image = FileField('Add product image', validators=[FileAllowed(['jpg', 'png', 'jpeg', 'gif'], 'Images only!')])
    is_approved = BooleanField('Admin Approval', default=False, render_kw={'style': 'display: none'})
    submit = SubmitField('Submit')

class UpdateItemForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description')
    price = FloatField('Price', validators=[DataRequired()])
    quantity = StringField('quantity', validators=[DataRequired()])

class ArticleForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField('Submit Article')
    is_approved = BooleanField('Admin Approval', default=False, render_kw={'style': 'display: none'})


class CreateEventForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description')
    date = DateTimeField('Date', format='%Y-%m-%d %H:%M:%S', validators=[DataRequired()], render_kw={'class': 'flatpickr'})
    location = StringField('Location')
    image = FileField('Event Image', validators=[FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Images only!')])

class ModifyEventForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = StringField('Description', validators=[DataRequired()])
    date = DateTimeField('Date', format='%Y-%m-%d %H:%M:%S', validators=[DataRequired()])
    location = StringField('Location', validators=[DataRequired()])

class UploadVlogForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description')
    youtube_link = StringField('YouTube Link', validators=[DataRequired(), URL()])
    submit = SubmitField('Submit')
    is_approved = BooleanField('Admin Approval', default=False, render_kw={'style': 'display: none'})
   

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class SignupForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()]) 
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Signup')



class ReviewForm(FlaskForm):
    rating = IntegerField('Rating', validators=[DataRequired(), NumberRange(min=1, max=5)])
    review_text = TextAreaField('Review', validators=[DataRequired()])
    submit = SubmitField('Submit Review')