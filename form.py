import requests
from flask import render_template
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, EmailField, BooleanField, TextAreaField, SelectField, IntegerField
from wtforms.validators import DataRequired, Email, Length, NumberRange, StopValidation

class ImageField(StringField):
    x = 100
    y = 100

    @property
    def preview(self):
        return render_template("profile/profile_preview.html", image=self.data, source=self.name, sizeX = self.x, sizeY=self.y)
    
class IsImage():
    def __init__(self, image_formats=("image/png", "image/jpeg", "image/jpg", "image/gif")) -> None:
        self.image_formats = image_formats

    def __call__(self, form, field):
        data:str = field.data
        if (data is None or data is ''):
            field.data = None
            field.error = None
            return
        
        if (('https://' not in data) and ('http://' not in data)):
            field.error = "Invalid link"
            raise StopValidation("Invalid link")
        
        try:
            r = requests.head(data)
            if (r.headers["content-type"] in self.image_formats):
                field.error = None
                return

            field.error = "It`s not an image"
            raise StopValidation("It`s not an image")
        except:
            field.error = "Invalid link"
            raise StopValidation("It`s not an image")

class LoginForm(FlaskForm):
    nickname = StringField("Никнейм:", validators=[DataRequired()])
    email = EmailField("Email:", validators=[Email()])
    password = PasswordField("Password:", validators=[DataRequired(), Length(8)])
    remember = BooleanField('Remember Me')
    submit = SubmitField("Submit")

class RegistrationForm(FlaskForm):
    nickname = StringField("Никнейм:", validators=[DataRequired()])
    email = EmailField("Email:", validators=[Email()])
    password = PasswordField("Password:", validators=[DataRequired(), Length(8)])
    password2 = PasswordField("Password:", validators=[DataRequired(), Length(8)])
    submit = SubmitField("Submit")

class ArticleForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    category = SelectField("Category")
    content = TextAreaField("Content", validators=[DataRequired()])

    submit = SubmitField("Submit")

class ProfileForm(FlaskForm):
    avatar = ImageField("Avatar", validators=[IsImage()])
    background = ImageField("Background", validators=[IsImage()])
    age = IntegerField("Age", validators=[NumberRange(1, 100)])
    about = TextAreaField("About")

    submit = SubmitField("Apply")

    def setData(self, user):
        self.avatar.data = user.avatar
        self.background.data = user.background
        self.background.x = 720
        self.about.data = user.about
        self.age.data = user.age