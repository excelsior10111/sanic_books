from sanic.views import HTTPMethodView
from sanic import text,json
from internal.models.session import session_db
from internal.models.user import user_db
from somex import cache
from ..middleware.middleware import authorized

# from redis_server.redis import get_cached_data

class Logout(HTTPMethodView):
    decorators = [authorized()]
    
    async def post(self,request, user):
        session = request.cookies.get('session') 
        await session_db.del_sess(user['id']) # removing session from db
        await cache.delete(f'sessions:{session}') # clear cache
        response = text('logged out') # Deleting cookie
        response.delete_cookie("session")
        return response


