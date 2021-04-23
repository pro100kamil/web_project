from flask import Flask, render_template, redirect, abort, request, url_for
from flask_login import LoginManager, login_user, current_user, logout_user, \
    login_required

from data import youtube, vk

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
    posts = db_sess.query(Post).all()[::-1]

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


@app.route("/users/<int:id>")
def user_by_id(id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).get(id)
    cur_user = db_sess.query(User).get(current_user.id)  # Текущий пользователь

    if not user:
        abort(404)
    return render_template("user.html",
                           title=f'{user.name} {user.surname}', user=user,
                           is_subscribed=cur_user.is_following(user),
                           is_cur_user=(id == current_user.id))


@app.route("/users/<int:id>/subscribe")
@login_required
def subscribe(id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).get(id)
    cur_user = db_sess.query(User).get(current_user.id)  # Текущий пользователь

    if not user:
        abort(404)

    # Не работает по неизвестной причине. Как и с постами current_user.posts.append(...)
    # current_user.follow(user)
    # db_sess.merge(current_user)
    # db_sess.commit()

    cur_user.follow(user)  # Текущий юзер подписывается на нужного
    db_sess.commit()
    return redirect('/users/' + str(id))


@app.route("/users/<int:id>/unsubscribe")
@login_required
def unsubscribe(id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).get(id)
    cur_user = db_sess.query(User).get(current_user.id)  # Текущий пользователь

    if not user:
        abort(404)

    cur_user.unfollow(user)  # Текущий юзер отписывается от нужного
    db_sess.commit()
    return redirect('/users/' + str(id))


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
@app.route("/posts")
@login_required
def posts_current_user():
    db_sess = db_session.create_session()
    posts = db_sess.query(Post).filter(Post.author == current_user)[::-1]

    return render_template("index.html", title='Мои посты', posts=posts)


@app.route("/posts/categories/<string:category>")
def post_by_category(category):
    db_sess = db_session.create_session()
    category = db_sess.query(Category).filter(
        Category.name == category).first()
    posts = list(filter(lambda el: category in el.categories,
                        db_sess.query(Post).all()))[::-1]
    return render_template("index.html",
                           title=f'{category.name.capitalize()}', posts=posts)


@app.route("/posts/users/<int:user_id>")
def post_by_user_id(user_id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).get(user_id)

    if not user:
        abort(404)
    posts = db_sess.query(Post).filter(Post.author_id == user_id)[::-1]
    return render_template("index.html",
                           title=f'Посты {user.name} {user.surname}',
                           posts=posts)


@app.route('/posts/<int:id>', methods=['GET', 'POST'])
@login_required
def show_post(id):
    db_sess = db_session.create_session()
    post = db_sess.query(Post).filter(Post.id == id).first()
    if not post:
        abort(404)

    return render_template('post.html', title=post.title,
                           post=post, like=post.is_like(current_user))


@app.route("/posts/<int:id>/like")
@login_required
def like(id):
    db_sess = db_session.create_session()
    post = db_sess.query(Post).filter(Post.id == id).first()
    if not post:
        abort(404)
    cur_user = db_sess.query(User).get(current_user.id)  # Текущий пользователь
    post.like(cur_user)
    db_sess.commit()
    return redirect(f'/posts/{id}')


@app.route("/posts/<int:id>/dislike")
@login_required
def dislike(id):
    db_sess = db_session.create_session()
    post = db_sess.query(Post).filter(Post.id == id).first()
    if not post:
        abort(404)
    cur_user = db_sess.query(User).get(current_user.id)  # Текущий пользователь
    post.dislike(cur_user)
    db_sess.commit()
    return redirect(f'/posts/{id}')


@app.route('/posts/create', methods=['GET', 'POST'])
@login_required
def create_post():
    form = PostForm()

    db_sess = db_session.create_session()
    categories = db_sess.query(Category).all()
    # заполнение комбобокса категориями
    form.category.choices = [(c.id, c.name) for c in categories]

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
                image.thumbnail((350, 350))
                image = image.convert('RGB')
                image.save(os.path.join(path, filename))
                post.icon = filename
            else:
                return render_template('add_edit_post.html',
                                       title='Добавление поста',
                                       message='Надо прекреплять изображение',
                                       form=form)

        categories = db_sess.query(Category).filter(
            Category.id.in_(form.category.data)).all()
        post.add_categories(categories)

        db_sess.add(post)
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
    # заполнение комбобокса категориями
    form.category.choices = [(c.id, c.name) for c in categories]

    if request.method == "GET":
        post = db_sess.query(Post).filter(Post.id == id,
                                          Post.author == current_user
                                          ).first()
        if post:
            form.title.data = post.title
            form.content.data = post.content
            form.icon.data = post.icon
        else:
            abort(404)
    if form.validate_on_submit():
        post = db_sess.query(Post).filter(Post.id == id,
                                          Post.author == current_user
                                          ).first()
        if not post:
            abort(404)

        post.title = form.title.data
        post.content = form.content.data
        categories = db_sess.query(Category).filter(
            Category.id.in_(form.category.data)).all()

        # Категории меняются если хотя бы одна была выбрана
        if categories:
            post.add_categories(categories)

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
                                       title='Редактирование поста',
                                       message='Надо прекреплять изображение',
                                       form=form, categories=categories)
        db_sess.commit()
        return redirect('/')

    return render_template('add_edit_post.html', title='Редактирование поста',
                           form=form)


@app.route('/video/<video_id>')
def get_video(video_id):
    video_data = youtube.get_by_id(video_id)

    return render_template('video.html', video=video_data)


@app.route('/search', methods=['GET', 'POST'])
def search():
    db_sess = db_session.create_session()

    if request.method == 'GET':
        line = request.args.get('query', '')
        kind = request.args.get('kind', 'users')
        page = int(request.args.get('page', 1))
        max_results, num_of_btns = 10, 5
        range_of_pages = range(page - (page - 1) % num_of_btns,
                               page + num_of_btns - (page - 1) % num_of_btns)
        prev_url = url_for('search', query=line, kind=kind, page=max(page - 1, 1))
        next_url = url_for('search', query=line, kind=kind, page=page + 1)

        if kind == 'users':
            users = db_sess.query(User).filter((User.name.like(f'%{line}%')) |
                                               (User.surname.like(
                                                   f'%{line}%'))).all()
            users = users[(page - 1) * max_results + 1:page * max_results + 1]
            return render_template('search_users.html', users=users,
                                   title='Поиск пользователя: ' + line,
                                   last_query=line, kind=kind, prev_url=prev_url,
                                   next_url=next_url, pages=range_of_pages, page=page)

        elif kind == 'posts':
            posts = db_sess.query(Post).filter(
                Post.title.like(f'%{line}%')).all()
            posts = posts[(page - 1) * max_results + 1:page * max_results + 1]
            return render_template('search_posts.html', posts=posts,
                                   title='Поиск поста: ' + line,
                                   last_query=line, kind=kind,
                                   pages=range_of_pages, next_url=next_url,
                                   prev_url=prev_url, page=page)

        elif kind == 'videos':
            latest_videos = youtube.get_latest(query=line, page=page)
            return render_template('search_videos.html', videos=latest_videos,
                                   title='Поиск видео: ' + line,
                                   kind=kind, last_query=line,
                                   pages=range_of_pages, prev_url=prev_url,
                                   next_url=next_url, page=page)

    elif request.method == 'POST':
        url_arg = request.form.get('for_search')
        kind = request.form.get('kind')
        return redirect(url_for('search', query=url_arg, kind=kind))


if __name__ == '__main__':
    db_session.global_init("db/data.db")
    app.register_blueprint(users_api.blueprint)
    app.run()
