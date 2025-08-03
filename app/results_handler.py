import json
from app.database_handler import db


async def show_results(email:str,session_id):
    try:
        if session_id != '':
            session = await db.get_session_info(session_id)
            if not session:
                return None
            history = await db.get_session_history(session_id)
            results = await db.get_session_results(session_id)
            his = json.loads(history["history"])
            res = json.loads(results["results"])
            #print(history,results)
            return [{
                "session": dict(session),
                "history": his["chat_history"],
                "results": res["results"]
            }]
        else:
            sessions = await db.get_sessions_by_user(email)
            #print(sessions)
            all_results = []
            for s in sessions:
                sid = s["session_id"]
                history = await db.get_session_history(sid)
                results = await db.get_session_results(sid)
                #print(history,results)
                his = json.loads(history["history"])
                res = json.loads(results["results"])
                #print(history,'\n\n\n', results)
                all_results.append({
                    "session": dict(s),
                    "history": his["chat_history"],
                    "results": res["results"]
                })
                print(all_results)
            return all_results
    except Exception as e:
        print(f"Error in show_results: {str(e)}")
        raise e
