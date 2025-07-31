import os,json
from pathlib import Path
import shutil

BASE_DIR = Path(__file__).parent.resolve() / "sessions"
def get_meta_path(session_id):
    meta_dir = BASE_DIR / session_id / "metainfo"
    meta_dir.mkdir(parents=True, exist_ok=True)
    return meta_dir


def get_session_data(session_id):
    path = os.path.join(get_meta_path(session_id), f"metadata.json")
    if not os.path.exists(path):
        return None
    with open(path, "r") as f:
        return json.load(f)

def save_session_data(session_id, data):
    os.makedirs(get_meta_path(session_id), exist_ok=True)
    path = os.path.join(get_meta_path(session_id), f"metadata.json")
    data["session_id"] = session_id
    with open(path, "w") as f:
        json.dump(data, f)

def delete_chunk(session_id, chunk_num):
    chunk_path = BASE_DIR / session_id / "audio" / f"chunk{chunk_num}.webm"
    print(chunk_path)
    if chunk_path.exists():
        chunk_path.unlink()

def delete_chunk_opus(path):
    path = Path(path)
    if path.exists():
        path.unlink()

def delete_session(session_id):
    chunk_path = BASE_DIR / session_id
    if chunk_path.exists():
        shutil.rmtree(chunk_path)
