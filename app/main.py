from fastapi import FastAPI
from . import models, database
from .routes import router

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Book Review Service", version="1.0")
app.include_router(router)
