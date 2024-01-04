from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse

from starlette.staticfiles import StaticFiles

from api.endpoints import routes
from db.database import Base, engine

app = FastAPI(title='FakeTwitter')
app.include_router(routes.router)
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.on_event("startup")
def startup_db():
    Base.metadata.create_all(bind=engine)


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse({"result": False, "error_type": "HTTPException", "error_message": str(exc.detail)})


@app.exception_handler(Exception)
async def generic_exception_handler(request, exc):
    return JSONResponse({"result": False, "error_type": "InternalServerError", "error_message": str(exc)})


app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)
