from functools import wraps
from somex import cache
from sanic import json
from internal.models.session import session_db
from internal.models.user import user_db
from datetime import datetime, timedelta
from somex import db
import pickle

def authorized():
    def decorator(f):
        @wraps(f)
        async def decorated_function(request, *args, **kwargs):
            resp,user_id = await check_request_for_authorization_status(request) # this func checks if session id in db or redis
            if user_id:
                user_data = await cache.get(f'users:{user_id}') #if userdata in cache, return it 
                if user_data:
                    newdata = pickle.loads(user_data) #formats bytes to map with user data 
                    kwargs['user'] = newdata 
                else:                    # if user data not found in redis, check db 
                    user_data, sts = await user_db.fetchall(user_id) #this func returns user data or error that it's not exist
                    if sts != 'ok': 
                        return json({'status': 'user not auth'}, 403)
                    newdata = pickle.dumps(dict(user_data)) 
                    await cache.setex(f'users:{user_id}', newdata, 9000) 
                    kwargs['user'] = dict(user_data)
                response = await f(request, *args, **kwargs)
                return response
            else:
                return resp
        return decorated_function
    return decorator

async def check_request_for_authorization_status(request): #searches session in cache or db
    session = request.cookies.get("session")
    if session == None:
        return json({"status": "not_authorized, goodbye"}, 403), False

    data_from_cache = await cache.get(f'sessions:{session}')

    if data_from_cache:
        data = pickle.loads(data_from_cache)
        return None, data['userid']
    else:
        data, exist = await session_db.fetchall(session)
        if exist == "ok":
            time_remaining = int((data['expiry'] - datetime.now()).total_seconds())
            newdata = pickle.dumps(data)
            key = f"sessions:{data['ssi']}"
            await cache.setex(key, newdata, time_remaining)
            return None, int(data['userid'])
    response = json({"status": "not_authorized, goodbye"}, 403) # Deleting cookie if session is not in db and redis
    response.delete_cookie("session")
    return response, False


