import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase
import datetime
from sqlalchemy_serializer import SerializerMixin


class Post(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'posts'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    author_id = sqlalchemy.Column(sqlalchemy.Integer,
                                  sqlalchemy.ForeignKey('users.id'))
    title = sqlalchemy.Column(sqlalchemy.String, default='Безымяный')
    content = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                     default=datetime.datetime.now)

    icon = sqlalchemy.Column(sqlalchemy.String, default='default.jpg')

    categories = orm.relation("Category",
                              secondary="association",
                              backref="posts")

