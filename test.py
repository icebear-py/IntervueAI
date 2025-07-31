from app.llm_handler import get_history
from app.session_handler import get_session_data
import base64


history = get_history('124cdbb5-21c3-4c18-afb4-850d7a81d655')
print(history)
history.append({"role": "system", "content": "I am gay"})
print(history)