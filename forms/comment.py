from flask_wtf import FlaskForm
from wtforms import TextAreaField
from wtforms import SubmitField
from wtforms.validators import DataRequired


class CommentForm(FlaskForm):
    content = TextAreaField('Текст комментария', validators=[DataRequired()])
    submit = SubmitField('Написать')
