import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app=app, base_url='http://127.0.0.1:8000')


@pytest.mark.tweets
def test_get_tweets():
    response = client.get("/api/tweets", headers={'api-key': 'test'})
    assert response.status_code == 200

    result = response.json()

    assert result["result"] is True
    assert result['tweets'] == []


@pytest.mark.tweets
def test_add_tweet_without_media():
    tweet_data = {"tweet_data": "Test tweet", "tweet_media_ids": []}
    response = client.post("/api/tweets", json=tweet_data, headers={'api-key': 'test'})

    assert response.status_code == 200

    result = response.json()

    assert result["result"] is True
    assert "tweet_id" in result


@pytest.mark.tweets
def test_add_tweet_with_media():
    tweet_data = {"tweet_data": "Test tweet data", "tweet_media_ids": [1, 2, 3]}
    response = client.post("/api/tweets", json=tweet_data, headers={'api-key': 'test'})
    assert response.status_code == 200
    result = response.json()
    assert result["result"] is True
    assert "tweet_id" in result


@pytest.mark.users
def test_another_user_info():
    user_id = 1
    response = client.get(f"/api/users/{user_id}")
    assert response.status_code == 200

    result = response.json()

    assert result["result"] is True
    assert "user" in result

    user_data = result["user"]

    assert user_data["id"] == user_id


@pytest.mark.users
def test_user_info():
    user_id = 1
    response = client.get("/api/users/me", headers={'api-key': 'test'})
    assert response.status_code == 200

    result = response.json()
    assert result["result"] is True
    assert "user" in result

    user_data = result["user"]

    assert user_data["id"] == user_id


@pytest.mark.users
def test_follow_user():
    response = client.post("/api/users/2/follow", headers={'api-key': 'test'})
    assert response.status_code == 200
    result = response.json()
    assert result["result"] is True


@pytest.mark.users
def test_unfollow_user():
    response = client.delete("/api/users/2/follow", headers={'api-key': 'test'})
    assert response.status_code == 200
    result = response.json()
    assert result["result"] is True


@pytest.mark.likes
def test_like_tweet():
    response = client.post("/api/tweets/1/likes", headers={'api-key': 'test'})
    assert response.status_code == 200
    result = response.json()
    assert result["result"] is True


@pytest.mark.likes
def test_unlike_tweet():
    response = client.delete("/api/tweets/1/likes", headers={'api-key': 'test'})
    assert response.status_code == 200
    result = response.json()
    assert result["result"] is True
