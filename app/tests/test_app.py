from io import BytesIO

import pytest

from db.models import Tweet, User, Subscribers, Media


@pytest.mark.tweets
def test_get_tweets(test_app, test_users):
    response = test_app.get("/api/tweets", headers={'api-key': 'test'})
    assert response.status_code == 200

    result = response.json()

    assert result["result"] is True
    assert result['tweets'] == []


@pytest.mark.tweets
def test_add_tweet_without_media(test_app, test_db, test_users):
    tweet_data = {"tweet_data": "Test tweet", "tweet_media_ids": []}
    response = test_app.post("/api/tweets", json=tweet_data, headers={'api-key': 'test'})

    assert response.status_code == 200

    result = response.json()

    assert result["result"] is True
    assert "tweet_id" in result

    tweet = test_db.query(Tweet).filter_by(id=1).first()
    assert tweet is not None


@pytest.mark.likes
def test_like_tweet(test_app, test_db, test_users):
    response = test_app.post("/api/tweets/1/likes", headers={'api-key': 'test'})
    assert response.status_code == 200

    result = response.json()

    assert result["result"] is True

    tweet = test_db.query(Tweet).filter_by(id=1).first()
    assert tweet is not None
    assert tweet.count_likes == 1


@pytest.mark.likes
def test_unlike_tweet(test_app, test_db, test_users):
    response = test_app.delete("/api/tweets/1/likes", headers={'api-key': 'test'})
    assert response.status_code == 200

    result = response.json()

    assert result["result"] is True

    tweet = test_db.query(Tweet).filter_by(id=1).first()
    assert tweet.count_likes == 0


@pytest.mark.tweets
def test_delete_tweet_with_media(test_app, test_db, test_users):
    response = test_app.delete("/api/tweets/1", headers={'api-key': 'test'})
    assert response.status_code == 200

    result = response.json()

    assert result["result"] is True

    tweets_count = test_db.query(Tweet).count()
    assert tweets_count == 0


def test_upload_media(test_app, test_users):
    fake_image_data = b'\x89JPG\00\x18e\xd1\t\x00\x00\x00\xd6'

    response = test_app.post("/api/medias", headers={'api-key': 'test'},
                             files={"file": ("fake_image.jpg", BytesIO(fake_image_data), "image/jpg")})
    assert response.status_code == 200

    result = response.json()

    assert result["result"] is True
    assert "media_id" in result


@pytest.mark.tweets
def test_add_tweet_with_media(test_app, test_db, test_users):
    tweet_data = {"tweet_data": "Test tweet data", "tweet_media_ids": [1]}
    response = test_app.post("/api/tweets", json=tweet_data, headers={'api-key': 'test'})
    assert response.status_code == 200

    result = response.json()

    assert result["result"] is True
    assert "tweet_id" in result

    media = test_db.query(Media).filter_by(id=1).first()
    assert media.tweet_id == 1


@pytest.mark.tweets
def test_delete_tweet(test_app, test_db, test_users):
    response = test_app.delete("/api/tweets/1", headers={'api-key': 'test'})
    assert response.status_code == 200

    result = response.json()

    assert result["result"] is True

    tweets_count = test_db.query(Tweet).count()
    assert tweets_count == 0


@pytest.mark.users
def test_another_user_info(test_app, test_users):
    response = test_app.get(f"/api/users/2")
    assert response.status_code == 200

    result = response.json()

    assert result["result"] is True
    assert "user" in result

    user_data = result["user"]

    assert user_data["id"] == 2
    assert user_data["name"] == 'user2'


@pytest.mark.users
def test_user_info(test_app, test_users):
    response = test_app.get("/api/users/me", headers={'api-key': 'test'})
    assert response.status_code == 200

    result = response.json()

    assert result["result"] is True
    assert "user" in result

    user_data = result["user"]

    assert user_data["id"] == 1
    assert user_data["name"] == 'user1'


@pytest.mark.users
def test_follow_user(test_app, test_db, test_users):
    response = test_app.post("/api/users/2/follow", headers={'api-key': 'test'})
    assert response.status_code == 200

    result = response.json()

    assert result["result"] is True

    user = test_db.query(User).filter(User.id == 1).first()
    followers_count = test_db.query(Subscribers).filter(Subscribers.subscribers_id == user.id).count()
    assert followers_count == 1


@pytest.mark.users
def test_unfollow_user(test_app, test_db, test_users):
    response = test_app.delete("/api/users/2/follow", headers={'api-key': 'test'})
    assert response.status_code == 200

    result = response.json()

    assert result["result"] is True

    user = test_db.query(User).filter(User.id == 1).first()
    followers_count = test_db.query(Subscribers).filter(Subscribers.subscribers_id == user.id).count()
    assert followers_count == 0
