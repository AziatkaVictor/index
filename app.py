import datetime
from tokenize import group
from flask import Flask, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_required, login_user, logout_user, current_user
from form import LoginForm, RegistrationForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'a-really-really-really-really-long-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///main.db'
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True, unique=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.String(20), nullable=False)
    registration_date = db.Column(db.DateTime, default=datetime.datetime.utcnow, nullable=False)

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password

    def __repr__(self):
        return f'<User {self.id}, {self.username}, {self.email}>'
    
    # TODO: Репутация пользователя
    @property
    def reputation(self):
        return 0

    # TODO: Количество записей в энциклопедии
    @property
    def articles_count(self):
        return 0

    # TODO: Проверку, администратор ли пользователь
    @property
    def is_admin(self):
        return False

    # TODO: Проверку, модератор ли пользователь
    @property
    def is_moderator(self):
        return False

@login_manager.user_loader
def user_loader(user_id):
    return User.query.get(user_id)

@app.route("/")
def main():
    return render_template('main.html')

@app.route("/login/", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main"))

    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username = form.nickname.data, email = form.email.data).first()
        if user:
            print('Login:', user)
            login_user(user, remember = form.remember.data)
            return redirect(url_for("main"))

    return render_template("login.html", form=form)

@app.route("/registration/", methods=["GET", "POST"])
def registration():
    if current_user.is_authenticated:
        return redirect(url_for("main"))

    form = RegistrationForm()

    if form.validate_on_submit():
        try:
            user = db.session.query(User.query.filter(User.username == form.nickname.data).exists()).scalar()

            if user:
                form.nickname.errors.append('User already exist!')
                return render_template("registration.html", form=form)
            if not form.password.data == form.password2.data:
                form.password.errors.append('Password are not same!')
                form.password2.errors.append('Password are not same!')
                return render_template("registration.html", form=form)

            u = User(username = form.nickname.data, email = form.email.data, password = form.password.data)
            try:
                db.session.add(u)
                db.session.flush()
                db.session.commit()
                return redirect(url_for("login"))
            except Exception as e:
                db.session.rollback()
                print('Error:', e)

        except Exception as e:
            print('Error:', e)
            
    return render_template("registration.html", form=form)

@app.route("/logout/", methods=["GET"])
@login_required
def logout():
    logout_user()
    return redirect(url_for("main"))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug = True)