from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from starlette.staticfiles import StaticFiles

from api.endpoints import routes
from db.database import Base, engine, get_db
from db.models import User

app = FastAPI(title='FakeTwitter')
app.include_router(routes.router)
app.mount("/static", StaticFiles(directory="static"), name="static")


def initialize_database(db: Session):
    existing_users = db.query(User.id).count()

    if existing_users == 0:
        db.add(User(username='Admin', api_key='test'))
        db.add(User(username='Vasiliy Pupkin', api_key='test2'))
        db.add(User(username='Elon Musk', api_key='Elon'))

        db.commit()


def startup_db():
    Base.metadata.create_all(bind=engine)
    db = next(get_db())
    initialize_database(db)


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse({"result": False, "error_type": "HTTPException", "error_message": str(exc.detail)})


@app.exception_handler(Exception)
async def generic_exception_handler(request, exc):
    return JSONResponse({"result": False, "error_type": "InternalServerError", "error_message": str(exc)})


app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)
app.add_event_handler("startup", startup_db)