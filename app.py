import datetime
from flask import Flask, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_required, login_user, logout_user, current_user
from form import ArticleForm, LoginForm, RegistrationForm
from flaskext.markdown import Markdown

app = Flask(__name__)
app.config['SECRET_KEY'] = 'a-really-really-really-really-long-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///main.db'
db = SQLAlchemy(app)
Markdown(app)

login_manager = LoginManager()
login_manager.init_app(app)

class Methods(): 
    """
    Class for similar class methods
    """

    @classmethod
    def getCount(self) -> int:
        return len(self.query.filter_by().all())

    @classmethod
    def getLast(self, count : int):
        return self.query.order_by(-self.creation_date).limit(count).all()

    @classmethod
    def getAll(self):
        return self.query.filter_by().all()

class User(db.Model, UserMixin, Methods):
    id = db.Column(db.Integer, primary_key=True, unique=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.String(20), nullable=False)
    registration_date = db.Column(db.DateTime, default=datetime.datetime.utcnow, nullable=False)
    articles = db.relationship('Article', backref='user')

    def __init__(self, username : str, email : str, password : str):
        self.username = username
        self.email = email
        self.password = password

    def __repr__(self):
        return f'<User {self.id}, {self.username}, {self.email}>'
    
    # TODO: Репутация пользователя
    @property
    def reputation(self):
        return 0

    @property
    def articles_count(self):
        return len(self.articles)

    # TODO: Проверку, администратор ли пользователь
    @property
    def is_admin(self):
        return False

    # TODO: Проверку, модератор ли пользователь
    @property
    def is_moderator(self):
        return False 

class Article(db.Model, Methods):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String, nullable=False)
    content = db.Column(db.Text, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    creation_date = db.Column(db.DateTime, default=datetime.datetime.utcnow, nullable=False)
    is_hidden = db.Column(db.Boolean, default=False, nullable=False)
    is_verified = db.Column(db.Boolean, default=False, nullable=False)
    reactions = db.relationship("Reaction", backref="article")

    def __init__(self, name : str, content : str, author_id : int, category_id : int):
        self.name = name
        self.content = content
        self.author_id = author_id
        self.category_id = category_id

    @property
    def author(self) -> User:
        return User.query.get(self.author_id)

    @property
    def category(self) -> User:
        return Category.query.get(self.category_id)

    @property
    def datetime(self) -> str:
        return self.creation_date.strftime("%H:%M %m.%d.%Y")

class Category(db.Model, Methods):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String, nullable=False)
    is_hidden = db.Column(db.Boolean, default=False, nullable=False)
    articles = db.relationship('Article', backref='category')

    def __init__(self, name : str):
        self.name = name

    def __repr__(self) -> str:
        return self.name
    
    @property
    def articlesCount(self) -> int:
        return len(self.articles)

class Reaction(db.Model, Methods):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    value = db.Column(db.Integer, default=1, nullable=False)
    article_id = db.Column(db.Integer, db.ForeignKey('article.id'), nullable=False)

    def __init__(self, article_id : int, value = 1):
        self.value = value
        self.article_id = article_id

@login_manager.user_loader
def user_loader(user_id):
    return User.query.get(user_id)

@app.route("/")
def main():
    return render_template('main.html', articleCount=Article.getCount(), categoryCount=Category.getCount(), userCount=User.getCount(), lastPages = Article.getLast(3))

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

@app.route("/add_article/", methods=["GET", "POST"])
@login_required
def add_article():
    form = ArticleForm()
    form.category.choices = [(data.id, data.name)for data in Category.query.filter_by().all()]

    if form.validate_on_submit():
        article = Article(form.name.data, form.content.data, current_user.id, int(form.category.data))
        try:
            db.session.add(article)
            db.session.flush()
            db.session.commit()

            return redirect(url_for("main"))
        except Exception as e:
            db.session.rollback()
            print('Error:', e)

    return render_template("./article/article_create.html", form=form)

@app.route("/view_articles/", methods=["GET"])
def view():
    categories = Category.getAll()
    return render_template("./article/articles_view.html", categories=categories)

@app.route("/detail_article/<id>", methods=["GET"])
def detail_article(id):
    article = Article.query.get(id)
    return render_template("./article/articles_detail.html", article = article)

@app.route("/registration/", methods=["GET", "POST"])
def registration():
    if current_user.is_authenticated:
        return redirect(url_for("main"))

    form = RegistrationForm()

    if form.validate_on_submit():
        try:
            isUserExist = db.session.query(User.query.filter(User.username == form.nickname.data).exists()).scalar()
            IsEmailExist = db.session.query(User.query.filter_by(email = form.email.data).exists()).scalar()

            if isUserExist:
                form.nickname.errors.append('User already exist!')
                return render_template("registration.html", form=form)
            if IsEmailExist:
                form.email.errors.append('Email already used!')
                return render_template("registration.html", form=form)
            if not form.password.data == form.password2.data:
                form.password.errors.append('Password are not same!')
                form.password2.errors.append('Password are not same!')
                return render_template("registration.html", form=form)

            user = User(username = form.nickname.data, email = form.email.data, password = form.password.data)
            try:
                db.session.add(user)
                db.session.flush()
                db.session.commit()
                if current_user.is_authenticated:    
                    logout_user()

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