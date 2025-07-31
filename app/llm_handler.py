import os,re
import json
from app.tts_handler import generate_audio,is_speakable
from app.prompts import system_prompt,results_prompt
from dotenv import load_dotenv
from openai import OpenAI
from pathlib import Path
load_dotenv()

DEEPINFRA_API_KEY = os.getenv("DEEPINFRA_API_KEY")
DEEPINFRA_URL = "https://api.deepinfra.com/v1/openai/chat/completions"
MODEL_NAME = "mistralai/Mistral-7B-Instruct-v0.3"

BASE_DIR = Path(__file__).parent.resolve() / "sessions"

def get_memory_path(session_id):
    memory_dir = BASE_DIR / session_id / "memory"
    memory_dir.mkdir(parents=True, exist_ok=True)
    return memory_dir

def get_history(session_id):
    path = os.path.join(get_memory_path(session_id), f"conversation.txt")
    if not os.path.exists(path):
        return []
    with open(path, "r") as f:
        try:
            if os.path.getsize(path) != 0:
                return json.load(f)
            else:
                return []
        except json.JSONDecodeError:
            return []


def update_history(session_id, history):
    os.makedirs(get_memory_path(session_id), exist_ok=True)
    path = os.path.join(get_memory_path(session_id), f"conversation.txt")
    with open(path, "w") as f:
        json.dump(history, f, indent=2)

def interview_continue(session_id: str,user_input:str):
    #print(session_id, user_input)
    history = get_history(session_id)
    history.append({"role": "user", "content": user_input})
    update_history(session_id, history)
    openai = OpenAI(
        api_key=f"{DEEPINFRA_API_KEY}",
        base_url="https://api.deepinfra.com/v1/openai",
    )
    try:
        stream = openai.chat.completions.create(
            model=MODEL_NAME,
            messages=history,
            stream=True
        )
        collected,buffered = "",""
        chunk_num = 0
        for chunk in stream:
            content = chunk.choices[0].delta.content
            if content:
                if content != 'DONE':
                    collected += content
                    buffered += content
                    if is_speakable(content):
                        audio = generate_audio(session_id,chunk_num,buffered)
                        yield json.dumps({"text":buffered,"audio":audio}) + "\n"
                        chunk_num += 1
                        buffered = ""

        history.append({"role": "assistant", "content": collected})
        update_history(session_id, history)
    except Exception as e:
        yield f"# Error: {str(e)}"


def interview_start(session_id, scenario, company, role, language, resume_content, user_input):
    history = get_history(session_id)
    if not history or history[0].get("role") != "system":
        system_prmpt = system_prompt(scenario, company, role, language, resume_content)
        history.append({"role": "system", "content": system_prmpt})
        update_history(session_id, history)
    #history.append({"role": "user", "content": user_input}
    for chunk in interview_continue(session_id,user_input):
        yield chunk


def interview_end(session_id):
    history = get_history(session_id)
    res_prompt = results_prompt()
    history.append({"role": "system", "content": res_prompt})
    if not history:
        return {"message":"session is not created yet"}
    openai = OpenAI(
        api_key=f"{DEEPINFRA_API_KEY}",
        base_url="https://api.deepinfra.com/v1/openai",
    )
    try:
        result = openai.chat.completions.create(
            model=MODEL_NAME,
            messages=history
        )
        content = result.choices[0].message.content
        return content
    except Exception as e:
        return {"error":str(e)}


if __name__ == "__main__":
    #generate_audio('21095ab9-05c5-47d2-b965-c23aee6fd23e',0,'Hello my name is nothing, how are you?')
    print(interview_end('124cdbb5-21c3-4c18-afb4-850d7a81d655'))

'''    reply = interview_continue(
        session_id='test-1234',
        user_input='heye',
    )
    for chunk in reply:
        print(chunk, end="", flush=True)'''

'''    reply = interview_start(
        session_id="test-1234",
        scenario="1:1 technical interview",
        company="OpenAI",
        role="ML Engineer",
        language="English",
        resume_content="Experience with Python, Transformers, FastAPI.",
        user_input="Hello!"
    )'''


