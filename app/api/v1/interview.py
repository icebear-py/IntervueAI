from fastapi import APIRouter, UploadFile, File, Form, HTTPException,Request
from fastapi.responses import JSONResponse,StreamingResponse
import base64,json
from app.database_handler import db
from app.llm_handler import interview_start,interview_continue,interview_end,get_history
from app.session_handler import get_session_data,save_session_data,delete_session
router = APIRouter()


@router.get("/")
def check():
    return {'message':'live'}


@router.post("/start_interview")
async def start_interview(session_id: str, user_input: str):
    try:
        session = get_session_data(session_id)
        if not session:
            raise HTTPException(status_code=400, detail="Session is not created yet.")

        def stream_response():
            yield from interview_start(
                session_id=session_id,
                scenario=session["scenario"],
                company=session["company"],
                role=session["role"],
                language=session["language"],
                resume_content=base64.b64encode(session["resume_content"]),
                user_input=user_input
            )
            session.pop("resume_content", None)
            save_session_data(session_id, session)
        return StreamingResponse(stream_response(), media_type="text/plain")
    except Exception as e:
        print("Error in /start_interview:", e)
        raise HTTPException(status_code=500, detail="Interview start failed.")

@router.post("/continue_interview")
async def continue_interview(session_id: str, user_input: str):
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
async def end_interview(session_id: str, email:str):
    try:
        content = interview_end(session_id)
        convo = {"chat_history":get_history(session_id)}
        results = {"results":content}
        await db.save_history_db(session_id,email,convo,results)
        delete_session(session_id)
        return {'status':True,'message':'Show results now.'}
    except:
        raise HTTPException(status_code=500, detail="Interview ending failed.")


@router.post("/show_results")
async def show_results(session_id: str,ema):
    try:
        delete_session(session_id)
        return {'status':True,'message':'Show results now.'}
    except:
        raise HTTPException(status_code=500, detail="Showing results failed.")