from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField, \
    TextAreaField, BooleanField, FileField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired, Length, EqualTo


class RegisterForm(FlaskForm):
    name = StringField('Имя', validators=[DataRequired()])
    surname = StringField('Фамилия', validators=[DataRequired()])
    email = EmailField('Email', validators=[DataRequired()])
    icon = FileField('Выберите аватарку')
    password = PasswordField(
        'Пароль',
        validators=[DataRequired(),
                    Length(min=4, max=100,
                           message="Пароль должен быть от 4 до 100 символов")])
    password_again = PasswordField(
        'Повтор пароля',
        validators=[DataRequired(),
                    EqualTo('password', message="Пароли не совпадают")])
    about = TextAreaField('Расскажите о себе')
    submit = SubmitField('Submit')


class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить')
    submit = SubmitField('Sign in')
