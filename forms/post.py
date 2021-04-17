from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, FileField
from wtforms import SubmitField
from wtforms.validators import DataRequired


class PostForm(FlaskForm):
    title = StringField('Заголовок', validators=[DataRequired()])
    content = TextAreaField("Содержание")
    icon = FileField('Выберите обложку публикациии')
    submit = SubmitField('Опубликовать / редактировать')