from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FileField, PasswordField, FloatField, IntegerField
from wtforms.validators import Length, DataRequired, NumberRange, InputRequired

class AddProductForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    price_kutaisi = IntegerField('Price from Kutaisi', validators=[DataRequired(), NumberRange(min=0)])
    price_london = IntegerField('Price from London', validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField('Add Product')


class RegisterForm(FlaskForm):
    username = StringField(label="Username", validators=[DataRequired(), Length(min=4)])
    password = PasswordField(label="Password", validators=[DataRequired()])
    register = SubmitField(label="Register")

class LoginForm(FlaskForm):
    username = StringField(label="Username", validators=[DataRequired()])
    password = PasswordField(label="Password", validators=[DataRequired()])
    login = SubmitField(label="Login")

class UpdatePasswordForm(FlaskForm):
    current_password = PasswordField(label="Current Password", validators=[DataRequired()])
    new_password = PasswordField(label="New Password", validators=[DataRequired()])
    confirm_password = PasswordField(label="Confirm New Password", validators=[DataRequired()])
    update = SubmitField(label="Update Password")