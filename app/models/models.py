import secrets

from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import ARRAY, JSONB


Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(50), nullable=False)
    followers = Column(ARRAY(JSONB), default=[])
    following = Column(ARRAY(JSONB), default=[])
    api_key = Column(String(), default=secrets.token_urlsafe(32), unique=True)

    def __repr__(self):
        return f"Пользователь {self.username}"






