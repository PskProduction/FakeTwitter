import secrets

from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.dialects.postgresql import ARRAY, JSONB

from app.db.database import Base


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(50), nullable=False)
    followers = Column(ARRAY(JSONB), default=[])
    following = Column(ARRAY(JSONB), default=[])
    api_key = Column(String(), default=secrets.token_urlsafe(32), unique=True)

    def __repr__(self):
        return f"Пользователь {self.username}"


class Tweet(Base):
    __tablename__ = 'tweets'

    id = Column(Integer, primary_key=True)
    user = Column(JSONB)
    user_id = Column(Integer, ForeignKey('users.id'))
    text = Column(String, nullable=False)
    medias = Column(ARRAY(JSONB), default=[])
    count_likes = Column(String, default='0')
    likes = Column(ARRAY(JSONB), default=[])

    like_relationships = relationship('Like', back_populates='tweet', cascade='all, delete-orphan')

    def __repr__(self):
        return f"Твит {self.text}"


class Like(Base):
    __tablename__ = 'likes'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    user_name = Column(String())
    tweet_id = Column(Integer, ForeignKey('tweets.id'))

    tweet = relationship('Tweet', back_populates='like_relationships')


class Followers(Base):
    __tablename__ = 'followers'

    id = Column(Integer, primary_key=True)
    followers_id = Column(Integer)
    name_followers = Column(String())
    name_followings = Column(String())
    my_id = Column(Integer)

    def __repr__(self):
        return f"Подписчик {self.follower_id} пользователя {self.user_id}"


class Followings(Base):
    __tablename__ = 'followings'

    id = Column(Integer, primary_key=True)
    followings_id = Column(Integer)
    followings_name = Column(String())
    my_id = Column(Integer)

    def __repr__(self):
        return f"Пользователь {self.user_id} подписан на {self.following_id}"


class Media(Base):
    __tablename__ = 'media'

    id = Column(Integer, primary_key=True)
    image_url = Column(String)
    user_id = Column(Integer, ForeignKey('users.id'))
    tweet_id = Column(Integer, ForeignKey('tweets.id'))
