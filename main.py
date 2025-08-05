from fastapi import FastAPI
from app.api.v1 import interview
from app.api.v1 import session
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.api.v1 import credits
from app.api.v1 import auth
from app.database_handler import db
import os


app = FastAPI()
@app.on_event("startup")
async def on_startup():
    await db.connect()
@app.on_event("shutdown")
async def on_shutdown():
    await db.disconnect()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(interview.router, prefix="/api/v1")
app.include_router(session.router, prefix="/api/v1")
app.include_router(credits.router,prefix="/api/v1")
app.include_router(auth.router,prefix="/api/v1")

@app.get('/')
async def start():
    return {'message':'API is live master.'}

