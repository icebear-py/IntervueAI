from fastapi import APIRouter, UploadFile, File, Form, HTTPException,Request
from fastapi.responses import JSONResponse,StreamingResponse
import base64,json
from app.database_handler import db
from app.llm_handler import interview_start,interview_continue,interview_end,get_history
from app.session_handler import get_session_data,save_session_data,delete_session
import PyPDF2
from io import BytesIO

router = APIRouter()


@router.get("/")
def check():
    return {'message':'live'}


@router.post("/start_interview")
async def start_interview(request: Request):
    data = await request.json()
    session_id = data.get("session_id")
    user_input = data.get("user_input")
    if not session_id:
        return JSONResponse({"message":"session_id is missing"})
    try:
        session = get_session_data(session_id)
        resume_bytes = base64.b64decode(session["resume_content"])
        pdf_reader = PyPDF2.PdfReader(BytesIO(resume_bytes))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() or ""
        if not session:
            raise HTTPException(status_code=400, detail="Session is not created yet.")

        def stream_response():
            yield from interview_start(
                session_id=session_id,
                scenario=session["scenario"],
                company=session["company"],
                role=session["role"],
                language=session["language"],
                resume_content=text,
                user_input=user_input
            )
            #session.pop("resume_content", None)
            save_session_data(session_id, session)
        return StreamingResponse(stream_response(), media_type="text/plain")
    except Exception as e:
        print("Error in /start_interview:", e)
        raise HTTPException(status_code=500, detail="Interview start failed.")

@router.post("/continue_interview")
async def continue_interview(request: Request):
    data = await request.json()
    session_id = data.get("session_id")
    user_input = data.get("user_input")
    if not session_id:
        return JSONResponse({"message":"session_id is missing"})
    #print(session_id, user_input)
    try:
        def stream_response():
            yield from interview_continue(
                session_id=session_id,
                user_input=user_input
            )
        return StreamingResponse(stream_response(), media_type="text/plain")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Interview continuation failed.")


@router.post("/end_interview")
async def end_interview(request:Request):
    data = await request.json()
    session_id = data.get("session_id")
    email = data.get("email")
    #print(session_id,email)
    if not session_id:
        return JSONResponse({"message":"session_id is missing"})
    try:
        content = str(interview_end(session_id))
        history = get_history(session_id)
        history = [i for i in history if i.get('role') != "system"]
        conversation = {"chat_history":history}
        results = {"results":content}
        #print(conversation,'\n\n\n',results)
        await db.save_history_db(session_id,email,conversation,results)
        current_credits = await db.get_credits_db(email)
        await db.update_credits_db(email,current_credits-1)
        delete_session(session_id)
        return {'status':True,'message':'Show results now.'}
    except:
        raise HTTPException(status_code=500, detail="Interview ending failed.")


@router.post("/show_results")
async def show_results(request: Request):
    data = await request.json()
    try:
        session_id = data.get("session_id")
    except:
        session_id = None
    email = data.get("email")

    try:
        delete_session(session_id)
        return {'status':True,'message':'Show results now.'}
    except:
        raise HTTPException(status_code=500, detail="Showing results failed.")

