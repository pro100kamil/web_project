import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase
import datetime
from sqlalchemy_serializer import SerializerMixin

likes = sqlalchemy.Table('likes', SqlAlchemyBase.metadata,
                         sqlalchemy.Column('post_id',
                                           sqlalchemy.Integer,
                                           sqlalchemy.ForeignKey(
                                               'posts.id')),
                         sqlalchemy.Column('user_id',
                                           sqlalchemy.Integer,
                                           sqlalchemy.ForeignKey(
                                               'users.id'))
                         )


class Post(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'posts'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    author_id = sqlalchemy.Column(sqlalchemy.Integer,
                                  sqlalchemy.ForeignKey('users.id'))
    title = sqlalchemy.Column(sqlalchemy.String)
    content = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                     default=datetime.datetime.now)

    icon = sqlalchemy.Column(sqlalchemy.String, default='default.jpg')

    author = orm.relation('User')

    categories = orm.relation("Category",
                              secondary="association",
                              backref="posts")

    likes_ = orm.relation('User', secondary='likes')

    def like(self, user):
        # user лайкает этот пост
        if not self.is_like(user):
            self.likes_.append(user)
            user.liked_posts.append(self)
            return self

    def dislike(self, user):
        # user убирает лайк с этого поста
        if self.is_like(user):
            self.likes_.remove(user)
            user.liked_posts.remove(self)
            return self

    def is_like(self, user):
        # лайкнул ли user этот пост
        return user in self.likes_

    def add_categories(self, categories):
        for category in self.categories:
            self.categories.remove(category)
        self.categories += categories


class AnonimPost(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'anonim_posts'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String)
    link = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    content = sqlalchemy.Column(sqlalchemy.String, nullable=True)
