from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, FloatField, SubmitField,PasswordField,DateTimeField
from wtforms.validators import DataRequired, Email, Length
from wtforms.validators import DataRequired, Email, Length, URL

class SellItemForm(FlaskForm):
    title = StringField('Product name', validators=[DataRequired()])
    description = TextAreaField('Product description')
    price = FloatField('Selling price', validators=[DataRequired()])

    # Pass allowed extensions to the FileField as an argument
    image = FileField('Add product image', validators=[FileAllowed(['jpg', 'png', 'jpeg', 'gif'], 'Images only!')])

    submit = SubmitField('Submit')

class UpdateItemForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description')
    price = FloatField('Price', validators=[DataRequired()])

class ArticleForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField('Submit Article')

class CreateEventForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description')
    date = DateTimeField('Date', format='%Y-%m-%d %H:%M:%S', validators=[DataRequired()], render_kw={'class': 'flatpickr'})
    location = StringField('Location')

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