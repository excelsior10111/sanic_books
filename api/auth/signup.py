from sanic import text, json
from sanic.views import HTTPMethodView
from internal.validator.validator import Validator, Validations
from internal.models.user import user_db
from internal.validator.rx import EmailRX, PassRX, passFilt

 
class Regdata(Validator):
    def __init__(self, email, password, username):
        self.email = email
        self.password = password
        self.username = username

class Signup(HTTPMethodView):
    async def post(self,request):
        v = Validator()
        regdata = Regdata(request.form.get("email"), request.form.get("password"), request.form.get("username"))   
        if not regdata:
           return json({'error': "Fields are empty"})
             
        v.CheckField(Validations.is_not_blank(regdata.email), "email", "This field cannot be blank")
        v.CheckField(Validations.is_not_blank(regdata.username), "name", "This field cannot be blank")
        v.CheckField(Validations.is_not_blank(regdata.password), "password", "This field cannot be blank")
        v.CheckField(Validations.matches(regdata.email, EmailRX), "email", "This field must be a valid email address")
        v.CheckField(Validations.matches(regdata.password, PassRX), "password", passFilt)
        v.CheckField(Validations.is_not_blank(regdata.password), "password", "This field cannot be blank")
        v.CheckField(Validations.minsymb(regdata.password, 8), "password", "This field must be at least 8 characters long")
        v.CheckField(Validations.maxsymb(regdata.password, 25), "password", "This field must not be longer than 25 characters")

        if not v.Valid():
            return json(v.FieldErrors)
        
        insertedata, status = await user_db.insert(regdata)
        if status != 'ok':
            return json(
                {'json': status})
        return json(insertedata)
    
