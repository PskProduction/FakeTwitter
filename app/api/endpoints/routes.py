from fastapi import Header, Depends, HTTPException, APIRouter
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from ...db.database import get_db
from ...db.db_structure import User

router = APIRouter()


@router.get('/api/tweets')
def get_tweets(api_key: str = Header('test')):
    if api_key is None:
        return {"error": "Не указан api-key"}

    tweets = []
    return tweets


@router.post("/api/tweets")
async def create_tweet(api_key: str = Header('test')):
    return {"result": True, "tweet_id": 1}


@router.post("/api/medias")
async def upload_media(api_key: str = Header('test')):
    media_id = 123
    return JSONResponse(content={"result": True, "media_id": media_id})


@router.delete('/api/tweets/{tweet_id}')
async def delete_tweet(api_key: str = Header('test')):
    return {'result': True}


@router.post('/api/tweets/{tweet_id}/likes')
async def like_tweet(api_key: str = Header('test')):
    return {'result': True}


@router.delete('/api/tweets/{tweet_id}/likes')
async def unlike_tweet(api_key: str = Header('test')):
    return {'result': True}


@router.post('/api/users/{user_id}/follow')
async def follow_user(api_key: str = Header('test')):
    return {'result': True}


@router.delete('/api/users/{user_id}/follow')
async def unfollow_user(api_key: str = Header('test')):
    return {'result': True}


@router.get('/api/users/me')
async def user_info(api_key: str = Header('test'), db: Session = Depends(get_db)):
    if api_key is None:
        return {"error": "Не указан api-key"}
    user = db.query(User).filter(User.api_key == api_key).first()

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

# @router.get('/api/users/{user_id}')
# async def user_info_by_id(user_id: int) -> dict:
#     another_user = db.get(User, user_id)
#
#     if another_user:
#         return {
#             "result": True,
#             "user": {
#                 "id": another_user.id,
#                 "name": another_user.username,
#                 "followers": [{}],
#                 "following": [{}],
#             }
#         }
