import asyncpg
from ..validator.validator import Validator
from somex import db
from ..utils.hash import h
from ..errors import errors
import uuid
from datetime import datetime, timedelta
from .session import session_db
from somex import cache

class User_db:
    def __init__(self, conn):
        self.conn = conn
        
    async def insert(self,user):
        hashpass = h.hash(user.password)
        cursor = self.conn
        try:
            sql = "INSERT INTO users (email, username, password_hash) VALUES ($1, $2, $3) RETURNING email, username"
            data = await cursor.fetchrow(sql, user.email, user.username, hashpass)
            print("Book inserted successfully!")
            return dict(data), statusOK
    
        except asyncpg.UniqueViolationError as e:
            if "users_email_key" in e.constraint_name: 
                return 0, errors.ErrDuplicateEmail
            else:
                print(f"Database error: {e}")
                return 0, errors.ErrInternalError

        except asyncpg.PostgresError as e:
            print(f"Error inserting user: {e}")
            return 0, errors.ErrInternalError

    async def fetchall(self, id):
        cursor = self.conn
        try:
            data = await cursor.fetchrow("SELECT * FROM users WHERE id = $1", id)
            if data is None:
                return None, errors.ErrInvalidCredentials
            else:
                return data, statusOK
        except asyncpg.PostgresError as e:
            print(f"Database error: {e}")
            return None, errors.ErrInternalError

    async def auth(self, email, input_pass):
        cursor = self.conn
        try:
            data = await cursor.fetchrow("SELECT password_hash, id FROM users WHERE email = $1", email)
            if data is None:
                return None, errors.ErrInvalidCredentials
            else:
                id = data['id']
                real_pass = data['password_hash']
        except asyncpg.PostgresError as e:
            print(f"Database error: {e}")
            return None, errors.ErrInternalError

        if not h.checkPass(real_pass, input_pass):
            return None, errors.ErrInvalidCredentials
        
        ssi = await session_db.del_sess(id) #if there is active session from that user, delete it. it will terminate their session
        await cache.delete(f'sessions:{ssi}')

        expiry_time = datetime.now() + timedelta(hours=1)
        ssi = str(uuid.uuid4())
        return await session_db.insert(ssi, id, expiry_time)

    async def del_user(self, userid):
        cursor = self.conn
        try:
            data = await cursor.fetchrow("UPDATE users SET is_active = false WHERE id = $1 RETURNING 1", userid)
            if data:
                return "deleted"
            return "not in users"
        except asyncpg.PostgresError as e:
            return f"Database error: {e}"

user_db = User_db(db)
statusOK = "ok"
