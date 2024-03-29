import datetime as dt
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

class ReactionType(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String, nullable=False)
    value = db.Column(db.Integer, server_default="1", nullable=False)

    @property
    def getWidget(self):
        if self.value > 0:
            return f"{self.name} (+{self.value})"
        return f"{self.name} ({self.value})"
    
class Reaction(db.Model, Methods):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    creation_datetime = db.Column(db.DateTime, server_default=db.func.now())
    type = db.Column(db.Integer, db.ForeignKey('reaction_type.id'), nullable=False)
    article_id = db.Column(db.Integer, db.ForeignKey('article.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __init__(self, article_id : int, user_id: int, type: int):
        self.type = type
        self.article_id = article_id
        self.user_id = user_id

    @property
    def reaction_type(self) -> ReactionType:
        return ReactionType.query.get(self.type)
    
    @property
    def value(self) -> ReactionType:
        return ReactionType.query.get(self.type).value
    
    @property
    def user(self):
        return User.query.get(self.user_id)

class User(db.Model, UserMixin, Methods):
    id = db.Column(db.Integer, primary_key=True, unique=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.String(20), nullable=False)
    registration_date = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)
    avatar = db.Column(db.String(200))
    background = db.Column(db.String(200))
    about = db.Column(db.Text)
    age = db.Column(db.Integer)
    articles = db.relationship('Article', backref='user')
    admin = db.Column(db.Boolean, server_default="0")

    def __init__(self, username : str, email : str, password : str):
        self.username = username
        self.email = email
        self.password = password

    def __repr__(self):
        return f'<User {self.id}, {self.username}, {self.email}>'
    
    def mostPopularArticles(self, count: int = 5):
        data = Article.query.filter_by(author_id = self.id).all()
        return list(sorted(data, key=lambda x: x.rating, reverse=True))[:count]
    
    @property
    def reputation(self):
        return sum([article.rating for article in self.articles])

    @property
    def articles_count(self):
        return len(self.articles)

    @property
    def is_admin(self):
        return bool(self.admin)

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

class Category(db.Model, Methods):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String, nullable=False)
    is_hidden = db.Column(db.Boolean, server_default="0", nullable=False)
    articles = db.relationship('Article', backref='category')

    def __init__(self, name : str):
        self.name = name

    def __repr__(self) -> str:
        return self.name
    
    @property
    def articlesCount(self) -> int:
        return len(self.articles)
    
    @property
    def isVisible(self) -> bool:
        return (not bool(self.is_hidden))
    
    def articleSorted(self) -> list:
        return Article.query.order_by(Article.creation_date).filter_by(category_id = self.id).all()[::-1]
    
    @classmethod
    def getData(self):
        categories = Category.query.filter_by(is_hidden = False).all()
        if current_user.is_authenticated:
            if current_user.is_admin:
                categories = Category.getAll()
        return categories

class Article(db.Model, Methods):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String, nullable=False)
    content = db.Column(db.Text, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    creation_date = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)
    is_hidden = db.Column(db.Boolean, server_default="0", nullable=False)
    is_verified = db.Column(db.Boolean, server_default="0", nullable=False)

    def __init__(self, name : str, content : str, author_id : int, category_id : int):
        self.name = name
        self.content = content
        self.author_id = author_id
        self.category_id = category_id

    @property
    def author(self) -> User:
        return User.query.get(self.author_id)

    @property
    def reactions(self) -> list[Reaction]:
        return Reaction.query.filter_by(article_id = self.id).all()
    
    @property
    def reactions_count(self) -> list[Reaction]:
        return len(self.reactions)
    
    @property
    def avgRating(self) -> float:
        if len(self.reactions) > 0:
            result = round(sum([reaction.value for reaction in self.reactions]) / len(self.reactions), 2)
            return result
        return 0.0
    
    @property
    def rating(self) -> int:
        if len(self.reactions) > 0:
            return sum([reaction.value for reaction in self.reactions])
        return 0
    
    @property
    def reactionsInfo(self) -> dict[str, int]:
        return {k.name: len(Reaction.query.filter_by(article_id=self.id, type=k.id).all()) for k in ReactionType.query.all()}

    @property
    def category(self) -> Category:
        return Category.query.get(self.category_id)

    @property
    def datetime(self) -> str:
        return self.creation_date.strftime("%H:%M %m.%d.%Y")
    
    @property
    def isVisible(self) -> bool:
        return (not self.is_hidden) and self.category.isVisible
    
    def getDatesRange(self, count: int) -> list[dt.datetime]:
        return [self.creation_date.date() + dt.timedelta(days=x) for x in range(count)]
    
    def getReactionsInRange(self, count: int) -> list[list[Reaction]]:
        return [self.reactionsByDate(v) for v in self.getDatesRange(count)]

    def reactionValuesInRange(self, count: int) -> list[int]:
        return [sum([reaction.value for reaction in v]) for v in self.getReactionsInRange(count)]
    
    def reactionAvgInRange(self, count: int) -> dict[dt.date, int]:
        result = []
        for v in self.getReactionsInRange(count):
            if len(v) > 0:
                result.append(round(sum([reaction.value for reaction in v])/len(v), 2))
                continue
            result.append(0)
        return result
    
    def reactionCountInRange(self, count: int) -> dict[dt.date, int]:
        return [len(v) for v in self.getReactionsInRange(count)]
    
    def reactionsByDate(self, date: dt.date) -> list[Reaction]:
        start = dt.datetime(year=date.year, month=date.month, day=date.day, hour=0, minute=0)
        end = dt.datetime(year=date.year, month=date.month, day=date.day, hour=23, minute=59)
        return Reaction.query.filter_by(article_id = self.id).filter(Reaction.creation_datetime >= start).filter(Reaction.creation_datetime <= end).all()
    
    def reactionFrom(self, user: User = current_user) -> Reaction | None:
        if user.is_authenticated:
            return Reaction.query.filter_by(user_id = user.id, article_id = self.id).first()
    
    def canEdit(self, user: User = current_user) -> bool:
        if not user:
            return False
        if not user.is_authenticated:
            return False
        return user.is_admin or user.id == self.author_id
    
    def canDelete(self, user: User = current_user) -> bool:
        if not user:
            return False
        if not user.is_authenticated:
            return False
        return user.is_admin or user.id == self.author_id
    
    def canSeeStatistic(self, user: User = current_user) -> bool:
        if user.is_authenticated:
            return user.id == self.author_id or user.is_admin
        return False
    
    def canSetReactions(self, user: User = current_user) -> bool:
        if user.is_authenticated:
            return user.id != self.author_id
        return False

class Rule(db.Model, Methods):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    title = db.Column(db.String, server_default="Default Title", nullable=False)
    description = db.Column(db.Text, server_default="Default description of the rule", nullable=False)
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
    name = db.Column(db.String, server_default="Default name", nullable=False)

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
    return render_template('main.html', globals=getGlobalsInfo())

@app.route("/rules/")
def rules():
    return render_template('rules.html', Rules=Rule.query.filter_by(parent_id = None).all(), globals=getGlobalsInfo())

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
    form.category.choices = [(data.id, data.name)for data in Category.getData()]

    if form.validate_on_submit():
        article = Article(form.name.data, form.content.data, current_user.id, form.category.data)
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
    form.category.choices = [(data.id, data.name) for data in Category.getData()]

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

@app.route("/article/<id>/delete", methods=["GET"])
@login_required
def delete_article(id):
    article: Article = Article.query.get(id)
    if not article:
        return redirect(url_for("main"))
    if not article.canDelete(current_user):
        return redirect(url_for("detail_article", id=article.id))
    
    db.session.delete(article)
    db.session.commit()

    return redirect(url_for("main"))

@app.route("/article/<id>/add_reaction/<reaction_type>", methods=["GET"])
@login_required
def add_reaction_article(id, reaction_type):
    article: Article = Article.query.get(id)
    if not article:
        return redirect(url_for("main"))
    
    if current_user.id == article.author_id:
        return redirect(url_for("detail_article", id=article.id))

    reaction: Reaction = Reaction.query.filter_by(user_id = current_user.id, article_id = id).first()
    try:
        if reaction:
            reaction.type = reaction_type
            reaction.creation_datetime = dt.datetime.utcnow()
            db.session.commit()

            return redirect(url_for("detail_article", id=article.id))
        
        user_reaction = Reaction(id, current_user.id, reaction_type)
        db.session.add(user_reaction)
        db.session.commit()

        return redirect(url_for("detail_article", id=article.id))
    except Exception as e:
        db.session.rollback()
        print('Error:', e)

    return redirect(url_for("detail_article", id=article.id))

@app.route("/article/<id>", methods=["GET"])
def detail_article(id):
    article = Article.query.get(id)
    if not article:
        return redirect(url_for('main'))
    
    reactions = ReactionType.query.all()
    return render_template("./article/articles_detail.html", article = article, reactions=reactions, globals=getGlobalsInfo())

@app.route("/view_articles/", methods=["GET"])
def view():
    categories = Category.getData()
    return render_template("./article/articles_view.html", categories=categories, globals=getGlobalsInfo())

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug = True)