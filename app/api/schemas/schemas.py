from pydantic import BaseModel


class TweetData(BaseModel):
    content: str
