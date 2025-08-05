from fastapi import APIRouter,HTTPException,Depends, Header,status
from fastapi.responses import JSONResponse
from app.database_handler import db
import os
from dotenv import load_dotenv
router = APIRouter()

MASTER_API_KEY = os.getenv("MASTER_API_KEY")


@router.get('/setcredits')
async def set_credits(email: str, credits: int, api_key: str):
    if not api_key == MASTER_API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorised")
    try:
        new_credits = await db.update_credits_db(email, credits)
        return JSONResponse(content={'status': f"Credits for {email} set to {new_credits}"})
    except ValueError:
        raise HTTPException(status_code=400, detail="Wrong request params")

