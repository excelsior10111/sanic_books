from sanic import Blueprint
from sanic.response import text
from .login import Login
from .signup import Signup
from .logout import Logout

auth = Blueprint('auth', url_prefix='/')

auth.add_route(Login.as_view(), '/login')
auth.add_route(Signup.as_view(), '/signup')
auth.add_route(Logout.as_view(), '/logout')
