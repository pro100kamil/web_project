from flask_wtf import FlaskForm
from wtforms import TextAreaField
from wtforms import SubmitField
from wtforms.validators import DataRequired


class CommentMainForm(FlaskForm):
    content = TextAreaField('Текст комментария', validators=[DataRequired()])
    submit_main = SubmitField('Написать')


class CommentSecondForm(FlaskForm):
    content = TextAreaField('Текст комментария', validators=[DataRequired()])
    submit_second = SubmitField('Написать')