import shutil

from fastapi import Header, Depends, HTTPException, APIRouter, UploadFile
from sqlalchemy import desc
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from ...db.database import get_db
from ...db.db_structure import User, Subscribers, Subscriptions, Tweet, Media, Like

router = APIRouter()


# Функция получения всех твитов
@router.get('/api/tweets')
def get_tweets(api_key: str = Header('test'), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.api_key == api_key).first()

    if user is None:
        raise HTTPException(status_code=404, detail='Пользователь не найден')

    tweets = db.query(Tweet).order_by(desc(Tweet.id)).all()
    tweets_response = [
        {
            "id": tweet.id,
            "content": tweet.text,
            "attachments": [
                media.image_url for media in db.query(Media)
                .filter_by(tweet_id=tweet.id).all()
            ],
            "author": tweet.user,
            "likes": tweet.likes
        } for tweet in tweets
    ]

    return {"result": True, "tweets": tweets_response}


# Фукция добавления нового твита
@router.post("/api/tweets")
async def create_tweet(tweet_data: dict, api_key: str = Header('test'), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.api_key == api_key).first()

    if user is None:
        raise HTTPException(status_code=404, detail='Пользователь не найден')

    if tweet_data not in tweet_data:
        raise HTTPException(status_code=404, detail='Отсутствуют обязательные поля')

    new_tweet = Tweet(text=tweet_data['tweet_data'], user_id=user.id)

    if "tweet_media_ids" in tweet_data:
        new_tweet.medias = tweet_data['tweet_media_ids']

    db.add(new_tweet)
    db.commit()
    db.refresh(new_tweet)
    return {"result": True, "tweet_id": new_tweet.id}


@router.post("/api/medias")
async def upload_media(file: UploadFile, api_key: str = Header('test'), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.api_key == api_key).first()

    if user is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    with open(f'media/{file.filename}, "wb"') as image:
        shutil.copyfileobj(file.file, image)
    db.add(
        Media(
            image_name=file.filename,
            user_id=user
        )
    )
    db.commit()
    media_id = db.query(Media).order_by(desc(Media.id)).first().id
    return JSONResponse(content={"result": True, "media_id": media_id})


# Функция удаления твита по id
@router.delete('/api/tweets/{tweet_id}')
async def delete_tweet(tweet_id: int, api_key: str = Header('test'), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.api_key == api_key).first()

    if user is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    tweet = db.query(Tweet).filter(Tweet.id == tweet_id, Tweet.user_id == user.id).first()

    if tweet is None:
        raise HTTPException(status_code=404, detail="Твит не найден")

    db.delete(tweet)
    db.commit()

    return {'result': True}


# Функция для лайка твита
@router.post('/api/tweets/{tweet_id}/likes')
async def like_tweet(tweet_id: int, api_key: str = Header('test'), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.api_key == api_key).first()

    if user is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    tweet = db.query(Tweet).filter(Tweet.id == tweet_id).first()

    if tweet is None:
        raise HTTPException(status_code=404, detail="Твит не найден")

    if not any(like.user_id == user.id for like in tweet.likes):
        tweet.likes.append(Like(user_id=user.id, user_name=user.username))
        tweet.count_likes = str(int(tweet.count_likes) + 1)
        db.commit()

    return {'result': True}


# Функция для удаления лайка с твита
@router.delete('/api/tweets/{tweet_id}/likes')
async def unlike_tweet(tweet_id: int, api_key: str = Header('test'), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.api_key == api_key).first()

    if user is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    tweet = db.query(Tweet).filter(Tweet.id == tweet_id).first()

    if tweet is None:
        raise HTTPException(status_code=404, detail="Твит не найден")

    if not any(like.user_id == user.id for like in tweet.likes):
        tweet.likes = [like for like in tweet.likes if like.user_id != user.id]
        tweet.count_likes = str(int(tweet.count_likes) - 1)

        db.commit()

    return {'result': True}


# Функция для подписки на пользователя
@router.post('/api/users/{subscriptions_id}/follow')
async def follow_user(subscriber_id: int, api_key: str = Header(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.api_key == api_key).first()

    if user is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    subscriber = db.get(User, subscriber_id)
    db.add(
        Subscriptions(
            subscriptions_id=subscriber_id,
            name_subscriptions=subscriber.full_name,
            my_id=user.id
        )
    )
    db.add(
        Subscribers(
            subscribers_id=user.id,
            name_subscribers=user.full_name,
            name_subscriptions=subscriber.username,
            my_id=subscriber_id
        )
    )
    db.commit()
    return {'result': True}


# Функция для удаления подписки на пользователя
@router.delete('/api/users/{user_id}/follow')
async def unfollow_user(subscriptions_id: int, api_key: str = Header('test'), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.api_key == api_key).first()

    if user is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    subscriptions = db.query(Subscriptions).filter_by(subscriptions_id=subscriptions_id, my_id=user).first()
    db.delete(subscriptions)

    subscribers = db.query(Subscribers).filter_by(subscribers_id=user, my_id=subscriptions_id).first()
    db.delete(subscribers)
    db.commit()

    return {'result': True}


# Фукция получения информации о текущем пользователе
@router.get('/api/users/me')
async def user_info(api_key: str = Header('test'), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.api_key == api_key).first()

    if user is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    subscriptions = db.query(Subscriptions).filter_by(my_id=user.id).all()
    subscribers = db.query(Subscribers).filter_by(my_id=user.id).all()

    user_response = {
        "id": user.id,
        "name": user.username,
        "followers": [{"id": subscriber.subscribers_id,
                       "name": subscriber.subscribers_name}
                      for subscriber in subscribers],
        "following": [{"id": subscription.subscriptions_id,
                       "name": subscription.subscriptions_name}
                      for subscription in subscriptions]
    }

    return {"result": True, "user": user_response}


# Функция получения информации о другом пользователе
@router.get('/api/users/{user_id}')
async def user_info_by_id(user_id: int, db: Session = Depends(get_db)) -> dict:
    another_user = db.get(User, user_id)

    if another_user is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    subscriptions = db.query(Subscriptions).filter_by(my_id=user_id).all()
    subscribers = db.query(Subscribers).filter_by(my_id=user_id).all()

    return {
        "result": True,
        "user": {
            "id": another_user.id,
            "name": another_user.username,
            "followers": [{"id": subscriber.subscribers_id,
                           "name": subscriber.subscribers_name}
                          for subscriber in subscribers],
            "following": [{"id": subscription.subscriptions_id,
                           "name": subscription.subscriptions_name}
                          for subscription in subscriptions],
        }
    }
