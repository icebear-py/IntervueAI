from fastapi import APIRouter,File,UploadFile, Form, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException
from app.database_handler import db
import uuid
from app.session_handler import save_session_data,delete_chunk
import base64
router = APIRouter()


@router.post("/acknowledge_chunk")
async def acknowledge_chunk(request: Request):
    try:
        data = await request.json()
        session_id = data.get("session_id")
        chunk_id = data.get("chunk")
        #print(session_id,chunk_id)
        if not session_id:
            #print('error')
            raise HTTPException(status_code=400, detail="Missing session_id or chunk")
        delete_chunk(session_id, chunk_id)
        return {"message": "chunk deleted from buffer."}
    except Exception as e:
        print(str(e))
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/create_session")
async def create_session(
    email : str = Form(...),
    scenario: str = Form(...),
    company: str = Form(...),
    role: str = Form(...),
    language: str = Form(...),
    resume: UploadFile = File(...)
):
    try:
        session_id = str(uuid.uuid4())
        resume_content = (await resume.read())
        resume_b64 = base64.b64encode(resume_content).decode('utf-8')
        data = {
            "session_id": session_id,
            "email": email,
            "scenario": scenario,
            "company": company,
            "role": role,
            "language": language,
            "resume_content": resume_b64,
        }

        save_session_data(session_id, data)
        await db.create_session_db(session_id,email,scenario,company,role,language)
        return JSONResponse({
            "message": "Session created successfully",
            "session_id": session_id
        })
    except Exception as e:
        print('Exception occurred:', e)
        raise HTTPException(status_code=500, detail="Internal Server Error")
