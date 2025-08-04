import os
from app.database_handler import db
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from google.oauth2 import id_token
from google.auth.transport import requests as grequests
from dotenv import load_dotenv
load_dotenv()

CLIENT_ID = os.getenv('GOOGLE_OAUTH_CLIENT_ID')
DEFAULT_CREDITS = os.getenv('DEFAULT_CREDITS')
router = APIRouter()


@router.post('/gauth')
async def auth(request: Request):
    data = await request.json()
    token = data.get("token")
    if not token:
        raise HTTPException(status_code=401, detail="Token is missing")
    try:
        idinfo = id_token.verify_oauth2_token(token, grequests.Request(), CLIENT_ID)
        name = idinfo.get("name") or ""
        email = idinfo['email']
        created = await db.create_user_db(email,name,credits=DEFAULT_CREDITS)
        mssg = "Registered successfully" if created else "Logged in successfully"
        creds = await db.get_credits_db(email)
        return JSONResponse({'name':name,'email':email,'credits':creds,'mssg':mssg})
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/get_credits")
async def get_credits(request: Request):
    data = await request.json()
    email = data.get("email")
    try:
        credits = await db.get_credits_db(email)
        return {'email':email,'credits':credits}
    except:
        raise HTTPException(status_code=500, detail="Failed to fetch credits.")