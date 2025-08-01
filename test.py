from app.llm_handler import get_history
from app.database_handler import db


async def test():
    sess = await db.get_sessions_by_user('testuser@example.com')
    return sess

test()