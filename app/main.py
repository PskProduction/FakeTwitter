from fastapi import FastAPI, Header
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from starlette.responses import JSONResponse
from starlette.staticfiles import StaticFiles

from models.models import Base, User

engine = create_engine("postgresql://admin:admin@0.0.0.0:5434/twitter", echo=True)
Session = sessionmaker(bind=engine)
session = Session()

Base.metadata.create_all(engine)

app = FastAPI(title='FakeTwitter')
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get('/api/tweets')
def get_tweets(api_key: str = Header('test')):
    if api_key is None:
        return {"error": "Не указан api-key"}

    tweets = []
    return tweets


@app.post("/api/tweets")
async def create_tweet(api_key: str = Header('test')):
    return {"result": True, "tweet_id": 1}


@app.post("/api/medias")
async def upload_media(api_key: str = Header('test')):
    media_id = 123
    return JSONResponse(content={"result": True, "media_id": media_id})


@app.delete('/api/tweets/{tweet_id}')
async def delete_tweet(api_key: str = Header('test')):
    return {'result': True}


@app.post('/api/tweets/{tweet_id}/likes')
async def like_tweet(api_key: str = Header('test')):
    return {'result': True}


@app.delete('/api/tweets/{tweet_id}/likes')
async def unlike_tweet(api_key: str = Header('test')):
    return {'result': True}


@app.post('/api/users/{user_id}/follow')
async def follow_user(api_key: str = Header('test')):
    return {'result': True}


@app.delete('/api/users/{user_id}/follow')
async def unfollow_user(api_key: str = Header('test')):
    return {'result': True}


@app.get('/api/users/me')
async def user_info(api_key: str = Header('test')):
    if api_key is None:
        return {"error": "Не указан api-key"}
    user = session.query(User).filter(User.api_key == api_key).first()

    if user is None:
        return {"result": False, "message": "Пользователь не найден"}

    user_response = {
        "id": user.id,
        "name": user.username,
        "followers": [{
            "id": "int",
            "name": "str"
        }],
        "following": [{
            "id": "int",
            "name": "str"
        }]
    }

    return {"result": True, "user": user_response}


@app.get('/api/users/{user_id}')
async def user_info_by_id(user_id: int) -> dict:
    another_user = session.get(User, user_id)

    if another_user:
        return {
            "result": True,
            "user": {
                "id": another_user.id,
                "name": another_user.username,
                "followers": [{}],
                "following": [{}],
            }
        }
