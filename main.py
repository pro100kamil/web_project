import hashlib
import uuid

from flask import Flask, render_template, redirect, abort, request, url_for, \
    render_template_string
from flask_login import LoginManager, login_user, current_user, logout_user, \
    login_required

from data import youtube, tg, news

from data import db_session, users_api, posts_api
from data.users import User
from data.posts import Post, AnonimPost
from data.comments import Comment
from data.categories import Category
from PIL import Image
import os

from forms.user import RegisterForm, LoginForm
from forms.post import PostForm
from forms.anonim_post import AnonimPostForm
from forms.comment import CommentMainForm, CommentSecondForm
from data import functions

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)
NEWS = news.get_news()


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
@app.route("/posts")
@app.route("/index")
def index():
    db_sess = db_session.create_session()
    posts = db_sess.query(Post).all()[::-1]

    return render_template("index.html", title='Главная', posts=posts)


@app.route("/about")
def about():
    return render_template("about.html", title='О сайте')


@app.route("/api")
def api_description():
    return render_template("api_description.html", title='Описание api')


@app.route("/liked")
@app.route("/liked_posts")
@login_required
def liked_posts():
    db_sess = db_session.create_session()
    cur_user = db_sess.query(User).get(current_user.id)
    posts = cur_user.liked_posts[::-1]
    if posts:
        return render_template("liked_posts.html",
                               title='Понравившиеся посты', posts=posts)
    else:
        return render_template("message.html",
                               title='Понравившиеся посты',
                               message='Понравившихся постов нет')


@app.route('/it_news')
def show_tg_news():
    ch_name = 'tbite'
    return render_template('tg_posts.html',
                           title='It-Новости',
                           urls=tg.latest_news(ch_name))


@app.route('/news')
def show_news():
    global NEWS
    NEWS = news.get_news()  # обновляем новости
    return render_template("news.html",
                           title='Главная', posts=NEWS)


@app.route("/news/<int:id>")
def news_by_id(id):
    cur = NEWS[id]
    return render_template('one_news.html', title=cur[0], post=cur)


@app.route("/users")
def all_users():
    db_sess = db_session.create_session()
    users = db_sess.query(User).all()
    for user in users:
        kol_likes = 0
        for post in user.posts:
            kol_likes += len(post.likes_)
        user.kol_likes = kol_likes
    return render_template("users.html",
                           title='Пользователи',
                           users=sorted(users,
                                        key=lambda user: -user.kol_likes))


@app.route("/users/<int:id>")
@login_required
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

        if form.icon.data:
            # если прикреплённый файл является изображением
            if form.icon.data.content_type.startswith('image'):
                user.icon = f'user_{uuid.uuid4().hex}.jpg'
                form.icon.data.save(f'static/img/users/{user.icon}')
            else:
                return render_template('register.html', title='Регистрация',
                                       form=form, reg=True,
                                       message="Надо прекреплять изображение")
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
        if form.icon.data:
            # если прикреплённый файл является изображением
            if form.icon.data.content_type.startswith('image'):
                try:
                    os.remove(os.path.join('static/img/users/', user.icon))
                except FileNotFoundError:
                    pass
                user.icon = f'user_{uuid.uuid4().hex}.jpg'
                form.icon.data.save(f'static/img/users/{user.icon}')
            else:
                return render_template('register.html', title='Личный кабинет',
                                       form=form, reg=False,
                                       message="Надо прекреплять изображение")
        db_sess.commit()
        return render_template('register.html', title='Личный кабинет',
                               form=form, reg=False,
                               message="Изменения сохранены")
    return render_template('register.html',
                           title='Личный кабинет', reg=False, form=form)


# работа с постами
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
    if posts:
        return render_template("index.html",
                               title=f'Посты {user.name} {user.surname}',
                               posts=posts)
    else:
        return render_template("message.html",
                               title=f'Посты {user.name} {user.surname}',
                               message='У этого пользователя нет постов')


@app.route('/posts/<int:post_id>', methods=['GET', 'POST'])
@login_required
def show_post(post_id):
    form = CommentMainForm()
    second_form = CommentSecondForm()

    db_sess = db_session.create_session()
    post = db_sess.query(Post).get(post_id)

    if not post:
        abort(404)

    if form.submit_main.data and form.validate():
        new_comment = Comment()
        new_comment.text = form.content.data
        new_comment.user_id = current_user.id
        new_comment.to_id = None
        post.comments.append(new_comment)
        db_sess.commit()
        return redirect(f'/posts/{post_id}')

    elif second_form.submit_second.data and second_form.validate():
        new_comment = Comment()
        new_comment.text = second_form.content.data
        new_comment.user_id = current_user.id
        new_comment.to_id = request.args.get('reply_to')
        post.comments.append(new_comment)
        db_sess.commit()
        return redirect(f'/posts/{post_id}')

    elif request.method == 'GET':
        comments = post.comments
        reply_id = request.args.get('reply_to')
        html_code = functions.reformat_comments(comments, reply_id=reply_id)
        rendered_html_code = render_template_string(html_code,
                                                    form=second_form)

        return render_template('post.html', title=post.title,
                               post=post, like=post.is_like(current_user),
                               form=form, html_code=rendered_html_code)


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
        filename = f'post_{uuid.uuid4().hex}.jpg'

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
        filename = f'post_{uuid.uuid4().hex}.jpg'

        if form.icon.data:
            # если прикреплённый файл является изображением
            if form.icon.data.content_type.startswith('image'):
                image: Image.Image = Image.open(form.icon.data)
                image.thumbnail((350, 350))
                image = image.convert('RGB')
                try:
                    os.remove(os.path.join(path, post.icon))
                except FileNotFoundError:
                    pass

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


@app.route('/anonim_posts/create', methods=['GET', 'POST'])
def create_anonim_post():
    form = AnonimPostForm()

    db_sess = db_session.create_session()

    if form.validate_on_submit():
        post = AnonimPost()
        post.title = form.title.data
        post.content = form.content.data

        post.link = hashlib.sha512(f'{post.title}{uuid.uuid4().hex}'.encode()
                                   ).hexdigest()[:12]

        db_sess.add(post)
        db_sess.commit()

        return redirect(f'/anonim_posts/{post.link}')

    return render_template('add_anonim_post.html', title='Добавление поста',
                           form=form)


@app.route('/anonim_posts/<string:post_link>', methods=['GET', 'POST'])
def show_anonim_post(post_link):
    db_sess = db_session.create_session()
    post = db_sess.query(AnonimPost).filter(
        AnonimPost.link == post_link).first()

    if not post:
        abort(404)

    return render_template('anonim_post.html', title=post.title,
                           post=post)


@app.route('/posts/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def post_delete(id):
    db_sess = db_session.create_session()
    post = db_sess.query(Post).filter(Post.id == id,
                                      Post.author == current_user
                                      ).first()
    if post:
        try:
            os.remove(os.path.join('static/img/thumbnails/', post.icon))
        except FileNotFoundError:
            pass

        db_sess.delete(post)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/')


@app.route('/video/<video_id>')
def get_video(video_id):
    video_data = youtube.get_by_id(video_id)

    return render_template('video.html',
                           title='Видео', video=video_data)


@app.route('/search', methods=['GET', 'POST'])
def search():
    db_sess = db_session.create_session()

    if request.method == 'GET':
        line = request.args.get('query', '')
        kind = request.args.get('kind', 'users')
        page = request.args.get('page', '1')
        max_results, num_of_btns = 10, 5

        if not page.isdigit() or kind not in ['videos', 'users', 'posts']:
            abort(404)

        page = int(page)

        range_of_pages = range(page - (page - 1) % num_of_btns,
                               page + num_of_btns - (page - 1) % num_of_btns)
        prev_url = url_for('search', query=line, kind=kind,
                           page=max(page - 1, 1))
        next_url = url_for('search', query=line, kind=kind, page=page + 1)

        params = {'last_query': line, 'kind': kind, 'prev_url': prev_url,
                  'next_url': next_url, 'pages': range_of_pages, 'page': page}

        if kind == 'users':
            users = db_sess.query(User).filter((User.name.like(f'%{line}%')) |
                                               (User.surname.like(
                                                   f'%{line}%'))).all()
            users = users[(page - 1) * max_results:page * max_results]
            return render_template('search_users.html', users=users,
                                   title='Поиск пользователя: ' + line,
                                   **params)

        elif kind == 'posts':
            posts = db_sess.query(Post).filter(
                Post.title.like(f'%{line}%')).all()
            posts = posts[::-1][(page - 1) * max_results:page * max_results]
            return render_template('search_posts.html', posts=posts,
                                   title='Поиск поста: ' + line, **params)

        elif kind == 'videos':
            latest_videos = youtube.get_latest(query=line, page=page)
            return render_template('search_videos.html', videos=latest_videos,
                                   title='Поиск видео: ' + line, **params)

    elif request.method == 'POST':
        url_arg = request.form.get('for_search')
        kind = request.form.get('kind')
        return redirect(url_for('search', query=url_arg, kind=kind))


if __name__ == '__main__':
    db_session.global_init("db/data.db")
    app.register_blueprint(users_api.blueprint)
    app.register_blueprint(posts_api.blueprint)

    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
    # app.run(host='127.0.0.1', port=5000)  # локальный запуск
