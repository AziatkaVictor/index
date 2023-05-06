import datetime
from flask import Flask, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_ckeditor import CKEditor
from flask_migrate import Migrate
from flask_login import UserMixin, LoginManager, login_required, login_user, logout_user, current_user
from sqlalchemy import MetaData, desc
from form import ArticleForm, LoginForm, ProfileForm, RegistrationForm

convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

app = Flask(__name__)
app.config['SECRET_KEY'] = 'a-really-really-really-really-long-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///main.db'
db = SQLAlchemy(app, metadata=MetaData(naming_convention=convention))
migrate = Migrate(app, db, render_as_batch=True)
ckeditor = CKEditor(app)

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
        return self.query.order_by(desc(self.creation_date)).limit(count).all()

    @classmethod
    def getAll(self):
        return self.query.filter_by().all()

class User(db.Model, UserMixin, Methods):
    id = db.Column(db.Integer, primary_key=True, unique=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.String(20), nullable=False)
    registration_date = db.Column(db.DateTime, default=datetime.datetime.utcnow, nullable=False)
    avatar = db.Column(db.String(400))
    background = db.Column(db.String(400))
    about = db.Column(db.Text)
    age = db.Column(db.Integer)
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
    
    @property
    def link(self):
        return url_for('profile', id=self.id)
     
    @property
    def datetime(self) -> str:
        return self.registration_date.strftime("%H:%M %m.%d.%Y")
    
    @property
    def date(self) -> str:
        return self.registration_date.strftime("%m.%d.%Y")

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
    
    def canEdit(self, user: User = current_user) -> bool:
        if not user.is_authenticated:
            return False
        return user.is_admin or user.id == self.author_id

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
    
    def articleSorted(self) -> list:
        return Article.query.order_by(Article.creation_date).filter_by(category_id = self.id).all()[::-1]

class Reaction(db.Model, Methods):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    value = db.Column(db.Integer, default=1, nullable=False)
    article_id = db.Column(db.Integer, db.ForeignKey('article.id'), nullable=False)

    def __init__(self, article_id : int, value = 1):
        self.value = value
        self.article_id = article_id

class Rule(db.Model, Methods):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    title = db.Column(db.String, default="Default Title", nullable=False)
    description = db.Column(db.Text, default="Default description of the rule", nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('rule.id'), index=True)
    children = db.relationship(lambda: Rule, remote_side=id, backref='sub_rules')

    def __init__(self, title: str, description: str, parent: int):
        self.title = title
        self.description = description
        self.parent_id = parent

class Сomplaint(db.Model, Methods):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    rules = db.Column(db.String)
    article_id = db.Column(db.Integer, db.ForeignKey('article.id'), nullable=False)
    status = db.Column(db.Integer, db.ForeignKey('complaint_status.id'), index=True)

    def __init__(self, article_id: int, rules: list[Rule]):
        self.rules = [f"{rule.id}," for rule in rules]
        self.article_id = article_id

class ComplaintStatus(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String, default="Default name", nullable=False)

    def __init__(self, name: str):
        self.name = name

def getGlobalsInfo():
    return {
            "lastPages" : Article.getLast(3),
            "articleCount" : Article.getCount(),
            "categoryCount" : Category.getCount(),
            "userCount" : User.getCount()
            }

@login_manager.user_loader
def user_loader(user_id):
    return User.query.get(user_id)

@app.route("/profile/<id>")
def profile(id):
    return render_template("profile/profile_detail.html", user=User.query.get(id))

@app.route("/profile/settings", methods=["GET", "POST"])
@login_required
def profile_settings():
    form = ProfileForm()

    if form.validate_on_submit():
        user = User.query.get(current_user.id)
        user.avatar = form.avatar.data
        user.background = form.background.data
        user.about = form.about.data
        user.age = int(form.age.data)
        db.session.commit()
        return redirect(url_for("profile", id=current_user.id))
    
    form.setData(current_user)
    return render_template("profile/profile_settings.html", form=form)

@app.route("/")
def main():
    return  render_template('main.html', globals=getGlobalsInfo())

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

    return render_template("login-registration.html", page_title="Вход", form=form)

@app.route("/logout/", methods=["GET"])
@login_required
def logout():
    logout_user()
    return redirect(url_for("main"))

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
                db.session.commit()
                if current_user.is_authenticated:    
                    logout_user()

                return redirect(url_for("login"))
            except Exception as e:
                db.session.rollback()
                print('Error:', e)

        except Exception as e:
            print('Error:', e)
            
    return render_template("login-registration.html", page_title="Регистрация", form=form)


@app.route("/article/add", methods=["GET", "POST"])
@login_required
def add_article():
    form = ArticleForm()
    form.category.choices = [(data.id, data.name)for data in Category.query.filter_by().all()]

    if form.validate_on_submit():
        article = Article(form.name.data, form.content.data, current_user.id, form.category.id)
        try:
            db.session.add(article)
            db.session.commit()

            return redirect(url_for("detail_article", id=article.id))
        except Exception as e:
            db.session.rollback()
            print('Error:', e)

    return render_template("./article/article_form.html", form=form)

@app.route("/article/<id>/edit", methods=["GET", "POST"])
@login_required
def edit_article(id):
    article: Article = Article.query.get(id)
    if not article.canEdit(current_user):
        return redirect(url_for("detail_article", id=article.id))
    
    form = ArticleForm()
    form.category.choices = [(data.id, data.name) for data in Category.query.filter_by().all()]

    if form.validate_on_submit():
        article = form.updateArticle(article)
        try:
            db.session.commit()
            return redirect(url_for("detail_article", id=article.id))
        except Exception as e:
            db.session.rollback()
            print('Error:', e)

    form.setData(article)
    return render_template("./article/article_form.html", form=form)

@app.route("/article/<id>", methods=["GET"])
def detail_article(id):
    article = Article.query.get(id)
    return render_template("./article/articles_detail.html", article = article, globals=getGlobalsInfo())

@app.route("/view_articles/", methods=["GET"])
def view():
    categories = Category.getAll()
    return render_template("./article/articles_view.html", categories=categories, globals=getGlobalsInfo())

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug = True)