import secrets

from fastapi import HTTPException
from sqlalchemy.orm import relationship, Session
from sqlalchemy import Column, Integer, String, ForeignKey

from db.database import Base


class Tweet(Base):
    __tablename__ = 'tweets'

    id = Column(Integer, primary_key=True)
    text = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'))
    count_likes = Column(Integer, default=0)

    author = relationship('User', back_populates='tweets')
    media = relationship('Media', back_populates='tweet')
    likes = relationship('Like', back_populates='tweet', cascade='all, delete-orphan')

    def __repr__(self):
        return f"Твит {self.text}"


class Like(Base):
    __tablename__ = 'likes'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    tweet_id = Column(Integer, ForeignKey('tweets.id'))

    user = relationship('User', back_populates='likes')
    tweet = relationship('Tweet', back_populates='likes')


class Media(Base):
    __tablename__ = 'media'

    id = Column(Integer, primary_key=True)
    image_url = Column(String)
    tweet_id = Column(Integer, ForeignKey('tweets.id'))
    user_id = Column(Integer, ForeignKey('users.id'))

    user = relationship('User', back_populates='user_media')
    tweet = relationship('Tweet', back_populates='media')


class Subscribers(Base):
    __tablename__ = 'subscribers'

    id = Column(Integer, primary_key=True)
    subscribers_id = Column(Integer, ForeignKey('users.id'))
    subscriber_id = Column(Integer, ForeignKey('users.id'))

    user = relationship('User', back_populates='subscribers', foreign_keys=[subscribers_id])
    subscribed_user = relationship('User', foreign_keys=[subscriber_id])

    def __repr__(self):
        return f"Подписчик {self.user.username} подписан на пользователя {self.subscribed_user.username}"


class Subscriptions(Base):
    __tablename__ = 'subscriptions'

    id = Column(Integer, primary_key=True)
    subscriptions_id = Column(Integer, ForeignKey('users.id'))
    subscriber_id = Column(Integer, ForeignKey('users.id'))

    user = relationship('User', back_populates='subscriptions', foreign_keys=[subscriptions_id])
    subscriber = relationship('User', foreign_keys=[subscriber_id])

    def __repr__(self):
        return f"Пользователь {self.user.username} подписан на {self.subscriber.username}"


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(50), nullable=False)
    api_key = Column(String, default=secrets.token_urlsafe(32), unique=True)

    tweets = relationship('Tweet', back_populates='author')
    likes = relationship('Like', back_populates='user')
    subscribers = relationship('Subscribers', back_populates='user', foreign_keys=[Subscribers.subscribers_id])
    subscriptions = relationship('Subscriptions', back_populates='user', foreign_keys=[Subscriptions.subscriptions_id])
    user_media = relationship('Media', back_populates='user')

    def __repr__(self):
        return f"Пользователь {self.username}"

    @classmethod
    def get_user_api_key(cls, db: Session, api_key: str):
        return db.query(cls).filter(cls.api_key == api_key).first()

    @classmethod
    def validate_api_key(cls, db: Session, api_key: str):
        user = cls.get_user_api_key(db, api_key)
        if not user:
            raise HTTPException(status_code=404, detail='Sorry. Wrong api-key token. This user does not exist.')
        return user

