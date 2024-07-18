from sanic import Blueprint
from .kicksess import KickSess
from .deluser import DelUser

admin = Blueprint('admin', url_prefix='/')

admin.add_route(KickSess.as_view(), "/terminate/<userid>")
admin.add_route(DelUser.as_view(), "/delete/<userid>")
