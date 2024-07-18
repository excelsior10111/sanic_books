from sanic import text,json, response
from sanic.views import HTTPMethodView
from internal.validator.validator import Validator, Validations
from internal.validator.rx import EmailRX, PassRX, passFilt
from internal.models.user import user_db
from somex import cache
from datetime import datetime
import pickle
from ..middleware.middleware import authorized

class Logdata(Validator):
    def __init__(self, email, password):
        self.email = email
        self.password = password
    def __str__(self):
        return f"Book: {self.author} (Name: {self.book_name}) (Published: {self.published}) (Description: {self.book_descr})"

class Login(HTTPMethodView):
    async def get(self,request, user):
        return text("Login form")
    
    async def post(self,request):
        v = Validator()
        logdata = Logdata(request.form.get("email"), request.form.get("password"))
        v.CheckField(Validations.is_not_blank(logdata.email), "email", "This Field cannot be blank")
        v.CheckField(Validations.matches(logdata.email, EmailRX), "email", "This field must be a valid email adress")
        v.CheckField(Validations.is_not_blank(logdata.password), "password", "This field cannot be blank")
        v.CheckField(Validations.matches(logdata.password, PassRX), "password", passFilt)

        if not v.Valid():
            return json(v.FieldErrors)
        
        data, status = await user_db.auth(logdata.email, logdata.password)
        if status != 'ok':
            return json({
                'error': status
            })
        resp = response.text('Setting a cookie!')
        time_remaining = int((data['expiry'] - datetime.now()).total_seconds())
        resp.add_cookie('session', data['ssi'], max_age=time_remaining)

        key = f"sessions:{data['ssi']}"
        data = pickle.dumps(dict(data))
        await cache.setex(key, data, time_remaining)
        return resp


