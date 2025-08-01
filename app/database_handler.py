import asyncpg
import os,json
from dotenv import load_dotenv
import ssl

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE
#print(DATABASE_URL)

class DatabaseHandler:
    def __init__(self):
        self.pool = None

    async def connect(self):
        if self.pool is None:
            self.pool = await asyncpg.create_pool(DATABASE_URL, ssl=ssl_context, statement_cache_size=0)

    async def disconnect(self):
        if self.pool is not None:
            await self.pool.close()

    async def create_user_db(self,email:str,name:str,credits:int):
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                INSERT INTO users (email, name, credits) 
                VALUES ($1, $2, $3)
                ON CONFLICT (email) DO NOTHING
                RETURNING email
                """,
                email,
                name,
                credits
            )
            return True if row else False

    async def user_exits(self,email:str):
        async with self.pool.acquire() as conn:
            await conn.execute()

    async def create_session_db(self,session_id:str,email:str,scenario:str,company:str,role:str,language:str):
        async with self.pool.acquire() as conn:
            session_id = await conn.fetchval(
                """
                INSERT INTO sessions (session_id,user_email, scenario, company, role, language, created_at) 
                VALUES ($1, $2, $3, $4, $5, $6,NOW())
                RETURNING session_id
                """,
                session_id,
                email,
                scenario,
                company,
                role,
                language,
            )
            return session_id

    async def get_session_info(self, session_id:str):
        async with self.pool.acquire() as conn:
            session = await conn.fetchrow(
                "SELECT * FROM sessions where session_id = $1",session_id
            )
            return dict(session) if session else None

    async def get_sessions_by_user(self, email):
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT * FROM sessions WHERE user_email = $1",
                email
            )
            return [dict(row) for row in rows]

    async def save_history_db(self,session_id:str, user_email:str, conversation:dict, results:dict):
        async with self.pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO history (session_id, user_email, history, results)
                VALUES ($1, $2, $3::jsonb, $4::jsonb)
                """,
                session_id,
                user_email,
                json.dumps(conversation),
                json.dumps(results)
            )

    async def get_session_results(self, session_id):
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT results FROM history WHERE session_id = $1", session_id
            )
            return dict(row) if row else None

    async def get_session_history(self, session_id):
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT history FROM history WHERE session_id = $1",
                session_id
            )
            return dict(row) if row else None


    async def get_credits_db(self,email:str):
        async with self.pool.acquire() as conn:
            credits = await conn.fetchval(
                """
                SELECT credits from users where email = $1
                """,email
            )
            return credits

    async def update_credits_db(self, user_email: str, credits: int):
        async with self.pool.acquire() as conn:
            updated = await conn.fetchval(
                """
                UPDATE users SET credits = $1 WHERE email = $2
                RETURNING credits
                """,
                credits,
                user_email
            )
            return updated


db = DatabaseHandler()

