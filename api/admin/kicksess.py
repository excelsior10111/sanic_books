from sanic.views import HTTPMethodView
from sanic import text,json
from internal.models.session import session_db
from somex import cache
from ..middleware.middleware import authorized

class KickSess(HTTPMethodView):

    decorators = [authorized()]
    
    async def put(self,request, user, userid):
        userid = int(userid)
        if user['role'] == 'admin':
            exist = False
            ssi = await session_db.del_sess(userid) # removing session from db
            if ssi:
                exist = True
            if await cache.delete(f'sessions:{ssi}'): # clear cache
                exist = True
            if exist:
                return json({f'{userid}': "was terminated"})
            return json({"error": f"there is no such session"})
        else:
            return json({'error':'Access denied'})


