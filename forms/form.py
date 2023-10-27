from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, FloatField, SubmitField,PasswordField
from wtforms.validators import DataRequired, Email, Length

class SellItemForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description')
    price = FloatField('Price', validators=[DataRequired()])

    # Pass allowed extensions to the FileField as an argument
    image = FileField('Image', validators=[FileAllowed(['jpg', 'png', 'jpeg', 'gif'], 'Images only!')])

    submit = SubmitField('Submit')

class UpdateItemForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description')
    price = FloatField('Price', validators=[DataRequired()])



