from sanic import Sanic, json, response
from jinja2 import Environment, FileSystemLoader, select_autoescape
from api import routes
from somex import db, cache
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from internal.models.session import session_db

template_path = 'templates'  #Setting path to folder with templates

env = Environment( 
    loader=FileSystemLoader(template_path),
    autoescape= select_autoescape(['html', 'xml'])
)

app = Sanic(__name__) 

@app.before_server_start
async def before_server_start(_app, _loop):
    db_settings = {
        'host': '127.0.0.1',
        'database': 'my_db',
        'password': 'postgres',
        'user': 'postgres'
    }
    await db.initialize(_loop, **db_settings)
    await cache.initialize()

@app.before_server_stop
async def before_server_stop(_app, _loop):
    await db.close()
    await cache.close()

@app.on_request
def log_request_info(request):
    path = request.path
    session = request.cookies.get('session')
    print(f"REQUEST PATH ----- {path}\nSESSION ------ {session}")
    if (path == '/login' or path == '/signup') and session != None:
        return json({"status":"you are already logged in"})

@app.get('/')
async def test(request):
    data = await db.fetch('select * from books limit 10')
    d = await cache.get('one')
    print('DATA in cache : ', d)
    res = [dict(d) for d in data]
    return json({'res': res})

app.blueprint(routes)

if __name__ == '__main__':
    app.run()