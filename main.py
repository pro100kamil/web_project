from flask import Flask, render_template, redirect, abort, request, url_for
from flask_login import LoginManager, login_user, current_user, logout_user, \
    login_required

from data import db_session, users_api
from data.users import User
from data.posts import Post
from data.categories import Category
from PIL import Image
import os

from forms.user import RegisterForm, LoginForm
from forms.post import PostForm


app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


# обработка ошибок
@app.errorhandler(404)
def page_not_found(error):
    return render_template('error.html',
                           error='Такой страницы не существует',
                           title='Страница не найдена')


@app.errorhandler(401)
def page_not_available(error):
    return render_template('error.html',
                           error='Эта страница доступна только '
                                 'авторизованным пользователем',
                           title='Страница не доступна')


# страницы сайта
@app.route("/")
@app.route("/index")
def index():
    db_sess = db_session.create_session()
    posts = db_sess.query(Post).all()

    return render_template("index.html", title='Главная', posts=posts)


@app.route("/about")
def about():
    return render_template("about.html", title='О сайте')


@app.route("/users")
def all_users():
    db_sess = db_session.create_session()
    users = db_sess.query(User).all()
    return render_template("users.html",
                           title='Пользователи',
                           users=users)


# авторизация и тому подобное
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(
            User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html', title='Авторизация',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form, reg=True,
                                   message="Email занят")
        user = User()
        user.email = form.email.data
        user.surname = form.surname.data
        user.name = form.name.data
        user.about = form.about.data
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html',
                           title='Регистрация', reg=True, form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route("/about_user", methods=['GET', 'POST'])
@login_required
def about_user():
    form = RegisterForm()
    if request.method == "GET":
        form.email.data = current_user.email
        form.surname.data = current_user.surname
        form.name.data = current_user.name
        form.about.data = current_user.about
    else:
        db_sess = db_session.create_session()
        user = db_sess.query(User).get(current_user.id)
        # Если пользователь сменил email на занятый другим пользователем email
        if user.email != form.email.data and db_sess.query(User).filter(
                User.email == form.email.data).first():
            return render_template('register.html', title='Личный кабинет',
                                   form=form, reg=False,
                                   message="Email занят")
        user.email = form.email.data
        user.surname = form.surname.data
        user.name = form.name.data
        user.about = form.about.data
        db_sess.commit()
        return render_template('register.html', title='Личный кабинет',
                               form=form, reg=False,
                               message="Изменения сохранены")
    return render_template('register.html',
                           title='Личный кабинет', reg=False, form=form)


# работа с постами
@app.route('/posts/create', methods=['GET', 'POST'])
@login_required
def create_post():
    form = PostForm()

    db_sess = db_session.create_session()
    categories = db_sess.query(Category).all()

    if form.validate_on_submit():

        post = Post()
        post.title = form.title.data
        post.content = form.content.data
        post.author_id = current_user.id

        path = 'static/img/thumbnails'
        num_images = len(os.listdir(path)) - 1
        filename = f'post_{num_images}.jpg'

        if form.icon.data:
            # если прикреплённый файл является изображением
            if form.icon.data.content_type.startswith('image'):
                image: Image.Image = Image.open(form.icon.data)
                image.thumbnail((200, 200))
                image = image.convert('RGB')
                image.save(os.path.join(path, filename))
                post.icon = filename
            else:
                return render_template('add_edit_post.html',
                                       title='Добавление поста',
                                       message='Надо прекреплять изображение',
                                       form=form, categories=categories)

        id_category = request.form['category']
        category = db_sess.query(Category).filter(Category.id == id_category).first()
        post.categories.append(category)

        db_sess.commit()
        return redirect('/')

    return render_template('add_edit_post.html', title='Добавление поста',
                           form=form, categories=categories)


@app.route('/posts/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_post(id):
    form = PostForm()
    db_sess = db_session.create_session()
    categories = db_sess.query(Category).all()

    if request.method == "GET":
        post = db_sess.query(Post).filter(Post.id == id,
                                          Post.author_id == current_user.id
                                          ).first()
        if post:
            form.title.data = post.title
            form.content.data = post.content
        else:
            abort(404)
    if form.validate_on_submit():
        post = db_sess.query(Post).filter(Post.id == id,
                                          Post.author_id == current_user.id
                                          ).first()
        if post:
            post.title = form.title.data
            post.content = form.content.data

            path = 'static/img/thumbnails'
            num_images = len(os.listdir(path)) - 1
            filename = f'post_{num_images}.jpg'

            if form.icon.data:
                # если прикреплённый файл является изображением
                if form.icon.data.content_type.startswith('image'):
                    image: Image.Image = Image.open(form.icon.data)
                    image.thumbnail((350, 350))
                    image = image.convert('RGB')
                    image.save(os.path.join(path, filename))
                    post.icon = filename
                else:
                    return render_template('add_edit_post.html',
                                           title='Добавление поста',
                                           message='Надо прекреплять изображение',
                                           form=form, categories=categories)
            db_sess.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('add_edit_post.html', title='Редактирование поста',
                           form=form, categories=categories)


if __name__ == '__main__':
    db_session.global_init("db/data.db")
    app.register_blueprint(users_api.blueprint)
    app.run()
