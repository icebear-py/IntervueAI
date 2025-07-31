from pathlib import Path
import os,re,base64,subprocess,pydub
from pydub import AudioSegment
from openai import OpenAI
from session_handler import delete_chunk_opus
from dotenv import load_dotenv
load_dotenv()


BASE_DIR = Path(__file__).parent.resolve() / "sessions"

def convert_to_webm(input_path: Path, output_path: Path):
    command = [
        'ffmpeg',
        '-loglevel', 'quiet',  # or 'warning', or 'quiet'
        '-y',
        '-i', str(input_path),
        '-c:a', 'libopus',
        '-f', 'webm',
        str(output_path)
    ]
    subprocess.run(command, check=True)
    delete_chunk_opus(input_path)



DEEPINFRA_API_KEY = os.getenv("DEEPINFRA_API_KEY")


def is_speakable(text):
    return bool(re.search(r"[.!?]$", text.strip()))

def get_chunk_path(session_id: str, chunk_num: int) -> Path:
    session_audio_dir = BASE_DIR / session_id / "audio"
    session_audio_dir.mkdir(parents=True, exist_ok=True)
    return session_audio_dir / f"chunk{chunk_num}.opus"

def get_webm_chunk_path(session_id: str, chunk_num: int) -> Path:
    session_audio_dir = BASE_DIR / session_id / "audio"
    session_audio_dir.mkdir(parents=True, exist_ok=True)
    return session_audio_dir / f"chunk{chunk_num}.webm"



def encode_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def generate_audio(session_id, chunk_num, text):
    try:
        # Generate .opus/.mp3 chunk from DeepInfra
        client = OpenAI(base_url="https://api.deepinfra.com/v1/openai", api_key=DEEPINFRA_API_KEY)
        opus_path = get_chunk_path(session_id, chunk_num)
        with client.audio.speech.with_streaming_response.create(
            model="hexgrad/Kokoro-82M",
            voice="af_bella",
            input=text,
            response_format="mp3",
        ) as response:
            response.stream_to_file(opus_path)
        webm_path = get_webm_chunk_path(session_id, chunk_num)
        convert_to_webm(opus_path, webm_path)
        with open(webm_path, "rb") as f:
            audio_base64 = base64.b64encode(f.read()).decode("utf-8")
        return {
            "text": text,
            "audio": audio_base64,
        }
    except Exception as e:
        return {"error": str(e)}


#print(generate_audio('124cdbb5-21c3-4c18-afb4-850d7a81d655',69,'hi how are you'))