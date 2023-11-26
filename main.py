from fastapi import FastAPI

from starlette.responses import FileResponse
from starlette.staticfiles import StaticFiles

from app.api.endpoints import routes
from app.db.database import Base, engine

app = FastAPI(title='FakeTwitter')
app.include_router(routes.router)
app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.on_event("startup")
def startup_db():
    Base.metadata.create_all(bind=engine)


@app.get("/")
def index():
    return FileResponse("app/templates/index.html")



