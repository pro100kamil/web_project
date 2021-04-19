import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin
from werkzeug.security import generate_password_hash, check_password_hash

from .db_session import SqlAlchemyBase

followers = sqlalchemy.Table('followers', SqlAlchemyBase.metadata,
                             sqlalchemy.Column('follower_id',
                                               sqlalchemy.Integer,
                                               sqlalchemy.ForeignKey(
                                                   'users.id')),
                             sqlalchemy.Column('followed_id',
                                               sqlalchemy.Integer,
                                               sqlalchemy.ForeignKey(
                                                   'users.id'))
                             )
subscribers = sqlalchemy.Table('subscribers', SqlAlchemyBase.metadata,
                               sqlalchemy.Column('subscriber_id',
                                                 sqlalchemy.Integer,
                                                 sqlalchemy.ForeignKey(
                                                     'users.id')),
                               sqlalchemy.Column('subscribed_id',
                                                 sqlalchemy.Integer,
                                                 sqlalchemy.ForeignKey(
                                                     'users.id'))
                               )


class User(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    surname = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    about = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    email = sqlalchemy.Column(sqlalchemy.String,
                              index=True, unique=True, nullable=True)
    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    posts = orm.relation("Post", back_populates='author')

    followed = orm.relationship('User',
                                secondary=followers,
                                primaryjoin=(followers.c.follower_id == id),
                                secondaryjoin=(followers.c.followed_id == id),
                                backref=orm.backref('followers',
                                                    lazy='dynamic'),
                                lazy='dynamic')
    subscribed = orm.relationship('User',
                                  secondary=subscribers,
                                  primaryjoin=(
                                          subscribers.c.subscriber_id == id),
                                  secondaryjoin=(
                                          subscribers.c.subscribed_id == id),
                                  backref=orm.backref('subscribers',
                                                      lazy='dynamic'),
                                  lazy='dynamic')

    def follow(self, user):
        if user.id != self.id and not self.is_following(user):
            self.followed.append(user)
            user.subscribed.append(self)
            return self

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)
            user.subscribed.remove(self)
            return self

    def is_following(self, user):
        return self.followed.filter(followers.c.followed_id == user.id).count()

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)
