from fastapi import FastAPI

from starlette.staticfiles import StaticFiles

from api.endpoints import routes
from db.database import Base, engine

app = FastAPI(title='FakeTwitter')
app.include_router(routes.router)
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.on_event("startup")
def startup_db():
    Base.metadata.create_all(bind=engine)
