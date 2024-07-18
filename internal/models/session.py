import asyncpg
from somex import db

class Session_db:
    def  __init__(self, conn):
        self.conn = conn

    async def insert(self, ssi, id, expiry):
        cursor = self.conn
        try:
            data = await cursor.fetchrow("INSERT INTO sessions (ssi, userid, expiry) VALUES($1, $2, $3) RETURNING *", ssi, id, expiry)
            print("new session init in db")
            return data, statusOK
        
        except asyncpg.PostgresError as e:
            print(f"error inserting new session: {e}")
            return  None, e
        
    async def fetch(self, ssi):
        cursor = self.conn
        try:
            data = await cursor.fetchrow("SELECT userid, expiry FROM sessions WHERE ssi = $1 AND expiry > NOW()", ssi)
            # TODO session id is valid or not 
            if data is None:
                return 0,0,False
            else:
                return data['userid'], data['expiry'], True
        except asyncpg.PostgresError as e:
            print(f"Database error: {e}")
            return 0, 0, False
        
    async def del_sess(self, id):
        cursor = self.conn
        try:
            data = await cursor.fetchval("DELETE FROM sessions WHERE userid = $1 RETURNING ssi", id)
            if data:
                return data
            return None
        except asyncpg.PostgresError as e:
            print(f"Database error: {e}")
            return None
        
    async def fetchall(self, ssi):
        cursor = self.conn
        try:
            data = await cursor.fetchrow("SELECT * FROM sessions WHERE ssi = $1 AND expiry > NOW()", ssi)
            # TODO session id is valid or not 
            if data is None:
                return None,"no data"
            else:
                return data, statusOK
        except asyncpg.PostgresError as e:
            print(f"Database error: {e}")
            return None, e
        

session_db = Session_db(db)
statusOK = "ok"
