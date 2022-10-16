from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, EmailField, BooleanField
from wtforms.validators import DataRequired, Email, Length

class LoginForm(FlaskForm):
    nickname = StringField("Никнейм: ", validators=[DataRequired()])
    email = EmailField("Email: ", validators=[Email()])
    password = PasswordField("Password: ", validators=[DataRequired(), Length(8)])
    remember = BooleanField('Remember Me')
    submit = SubmitField("Submit")

class RegistrationForm(FlaskForm):
    nickname = StringField("Никнейм: ", validators=[DataRequired()])
    email = EmailField("Email: ", validators=[Email()])
    password = PasswordField("Password: ", validators=[DataRequired(), Length(8)])
    password2 = PasswordField("Password: ", validators=[DataRequired(), Length(8)])
    submit = SubmitField("Submit")