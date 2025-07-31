from fastapi import APIRouter,HTTPException,Request
from fastapi.responses import JSONResponse
from app.database_handler import db
router = APIRouter()


@router.get('/hello')
async def start():
    return {'message':'API is live master.'}

@router.get('/setcredits')
async def setcredits(email:str,credits:int):
    if not email:
        raise HTTPException(status_code=400, detail="Missing email or credits parameter")
    try:
        newcredits = await db.update_credits_db(email, credits)
    except ValueError:
        raise HTTPException(status_code=400, detail="Wrong request params")
    return JSONResponse(content={'status': f"Credits for {email} set to {newcredits}"})
