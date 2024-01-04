import os
import shutil
from typing import List

from fastapi import Header, Depends, HTTPException, APIRouter, UploadFile
from sqlalchemy import desc
from sqlalchemy.orm import Session

from ..schemas.schemas import TweetData
from db.database import get_db
from db.models import User, Subscribers, Subscriptions, Tweet, Media, Like

media_dir = 'static/images'
if not os.path.exists(media_dir):
    os.makedirs(media_dir)

router = APIRouter()


# Функция получения всех твитов
@router.get('/api/tweets')
def get_tweets(
        api_key: str = Header(),
        db: Session = Depends(get_db)
):
    User.validate_api_key(db, api_key)

    tweets = db.query(Tweet).order_by(desc(Tweet.id)).all()
    tweets_response = [
        {
            "id": tweet.id,
            "content": tweet.text,
            "attachments": [
                media.image_url for media in db.query(Media)
                .filter_by(tweet_id=tweet.id).all()
            ],
            "author": {
                "id": tweet.user_id,
                "name": tweet.author.username
            },
            "likes": [
                {"user_id": like.user.id, "name": like.user.username}
                for like in tweet.likes if like.user is not None
            ] if tweet.likes else []
        } for tweet in tweets
    ]

    return {"result": True, "tweets": tweets_response}


# Фукция добавления нового твита
@router.post("/api/tweets")
async def create_tweet(
        tweet_data: str,
        tweet_media_ids: List[int] = [],
        api_key: str = Header(),
        db: Session = Depends(get_db)
):
    user = User.validate_api_key(db, api_key)

    new_tweet = Tweet(text=tweet_data, user_id=user.id)

    db.add(new_tweet)
    db.commit()
    db.refresh(new_tweet)

    if tweet_media_ids:
        for media_id in tweet_media_ids:
            media = db.query(Media).filter(Media.id == media_id).first()
            if media:
                new_tweet.media.append(media)
                media.tweet_id = new_tweet.id

    db.commit()

    return {"result": True, "tweet_id": new_tweet.id}


# Функция загрузки изображений к твитам
@router.post("/api/medias")
async def upload_media(
        file: UploadFile,
        api_key: str = Header(),
        db: Session = Depends(get_db)
):
    user = User.validate_api_key(db, api_key)

    with open(f'{media_dir}/{file.filename}', 'wb') as image:
        shutil.copyfileobj(file.file, image)

    new_media = Media(image_url=file.filename, user_id=user.id)
    db.add(new_media)
    db.commit()
    db.refresh(new_media)

    return {"result": True, "media_id": new_media.id}


# Функция удаления твита по id
@router.delete('/api/tweets/{tweet_id}')
async def delete_tweet(
        tweet_id: int,
        api_key: str = Header(),
        db: Session = Depends(get_db)
):
    user = User.validate_api_key(db, api_key)

    tweet = db.query(Tweet).filter(Tweet.id == tweet_id, Tweet.user_id == user.id).first()

    if tweet is None:
        raise HTTPException(status_code=404, detail="Твит не найден")

    db.delete(tweet)
    db.commit()

    return {'result': True}


# Функция для лайка твита
@router.post('/api/tweets/{tweet_id}/likes')
async def like_tweet(
        tweet_id: int,
        api_key: str = Header(),
        db: Session = Depends(get_db)
):
    user = User.validate_api_key(db, api_key)

    tweet = db.query(Tweet).filter(Tweet.id == tweet_id).first()

    if tweet is not None:
        if not any(like.user_id == user.id for like in tweet.likes):
            tweet.likes.append(Like(user_id=user.id, user=user))
            tweet.count_likes = str(int(tweet.count_likes) + 1)
            db.commit()

        return {'result': True}

    raise HTTPException(status_code=404, detail="Твит не найден")


# Функция для удаления лайка с твита
@router.delete('/api/tweets/{tweet_id}/likes')
async def unlike_tweet(
        tweet_id: int,
        api_key: str = Header(),
        db: Session = Depends(get_db)
):
    user = User.validate_api_key(db, api_key)

    tweet = db.query(Tweet).filter(Tweet.id == tweet_id).first()

    if tweet is None:
        raise HTTPException(status_code=404, detail="Твит не найден")

    like_to_remove = next((like for like in tweet.likes if like.user_id == user.id), None)

    if like_to_remove:
        tweet.likes.remove(like_to_remove)
        tweet.count_likes = str(int(tweet.count_likes) - 1)
        db.commit()

    return {'result': True}


# Функция для подписки на пользователя
@router.post('/api/users/{user_id}/follow')
async def follow_user(
        user_id: int,
        api_key: str = Header(),
        db: Session = Depends(get_db)
):
    user = User.validate_api_key(db, api_key)

    subscriber = db.query(User).filter(User.id == user_id).first()

    if subscriber is None:
        raise HTTPException(status_code=404, detail="Пользователь для подписки не найден")
    db.add(
        Subscriptions(
            user=user,
            subscriber=subscriber
        )
    )
    db.add(
        Subscribers(
            user=user,
            subscribed_user=subscriber
        )
    )
    db.commit()
    return {'result': True}


# Функция для удаления подписки на пользователя
@router.delete('/api/users/{user_id}/follow')
async def unfollow_user(
        user_id: int,
        api_key: str = Header(),
        db: Session = Depends(get_db)
):
    user = User.validate_api_key(db, api_key)

    subscription = (
        db.query(Subscriptions)
        .filter(Subscriptions.user == user, Subscriptions.subscriber.has(id=user_id))
        .first()
    )
    if subscription:
        db.delete(subscription)

    subscriber = (
        db.query(Subscribers)
        .filter(Subscribers.subscribers_id == user.id, Subscribers.subscriber_id == user_id)
        .first()
    )
    if subscriber:
        db.delete(subscriber)

    db.commit()
    return {'result': True}


# Фукция получения информации о текущем пользователе
@router.get('/api/users/me')
async def user_info(
        api_key: str = Header(),
        db: Session = Depends(get_db)
):
    user = User.validate_api_key(db, api_key)

    subscriptions = db.query(Subscriptions).filter_by(subscriber_id=user.id).all()
    subscribers = db.query(Subscribers).filter_by(subscriber_id=user.id).all()

    user_response = {
        "id": user.id,
        "name": user.username,
        "followers": [
            {
                "id": subscriber.subscribers_id,
                "name": subscriber.subscribed_user.username
            }
            for subscriber in subscribers
        ],
        "following": [
            {
                "id": subscription.subscriptions_id,
                "name": subscription.user.username
            }
            for subscription in subscriptions
        ],
    }

    return {"result": True, "user": user_response}


# Функция получения информации о другом пользователе
@router.get('/api/users/{user_id}')
async def user_info_by_id(
        user_id: int,
        db: Session = Depends(get_db)
) -> dict:
    another_user = db.query(User).get(user_id)

    if another_user is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    subscriptions = db.query(Subscriptions).filter_by(subscriber_id=user_id).all()
    subscribers = db.query(Subscribers).filter_by(subscriber_id=user_id).all()

    return {
        "result": True,
        "user": {
            "id": another_user.id,
            "name": another_user.username,
            "followers": [
                {
                    "id": subscriber.subscribers_id,
                    "name": subscriber.subscribed_user.username
                }
                for subscriber in subscribers
            ],
            "following": [
                {
                    "id": subscription.subscriptions_id,
                    "name": subscription.user.username
                }
                for subscription in subscriptions
            ],
        }
    }
