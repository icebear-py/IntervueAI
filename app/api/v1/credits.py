from fastapi import APIRouter,HTTPException,Depends, Header,status
from fastapi.responses import JSONResponse
from app.database_handler import db
import os
from dotenv import load_dotenv
router = APIRouter()

MASTER_API_KEY = os.getenv("MASTER_API_KEY")

async def get_api_key(x_api_key: str = Header(...)):
    if not MASTER_API_KEY or x_api_key != MASTER_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or Missing API Key"
        )

@router.get('/setcredits')
async def setcredits(email: str, credits: int, master_api_key: str = Depends(get_api_key)):
    if not email:
        raise HTTPException(status_code=400, detail="Missing email or credits parameter")
    try:
        newcredits = await db.update_credits_db(email, credits)
    except ValueError:
        raise HTTPException(status_code=400, detail="Wrong request params")
    return JSONResponse(content={'status': f"Credits for {email} set to {newcredits}"})
