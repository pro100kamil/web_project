from flask import Flask, render_template, redirect, abort, request
from flask_login import LoginManager, login_user, current_user, logout_user, \
    login_required

from data import db_session
from data.users import User

from forms.user import RegisterForm, LoginForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route("/")
@app.route("/index")
def index():
    return render_template("index.html", title='Главная')


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
        user.email = form.email.data
        user.surname = form.surname.data
        user.name = form.name.data
        user.about = form.about.data
        db_sess.commit()
        return redirect('/')
    return render_template('register.html',
                           title='Личный кабинет', reg=False, form=form)


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
                               problem="Неправильный логин или пароль",
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


if __name__ == '__main__':
    db_session.global_init("db/data.db")
    app.run()
