from sanic.views import HTTPMethodView
from sanic import text,json
from internal.models.session import session_db
from internal.models.user import user_db
from somex import cache
from ..middleware.middleware import authorized


class DelUser(HTTPMethodView):
    decorators = [authorized()]

    async def delete(self,request, user, userid):
        userid = int(userid)
        print(user)
        if user['role'] == 'admin':
            ssi = await session_db.del_sess(userid) # removing session from db
            if not ssi:
                return json({f'{userid}': "doesnt exist"})
            await user_db.del_user(userid)
            await cache.delete(f'sessions:{ssi}')
            await cache.delete(f'users:{userid}')
            return json({f'{userid}': "was deleted"})
        else:
            return json({'error':'Access denied'})


