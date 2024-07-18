from sanic.views import HTTPMethodView
from sanic.response import  redirect, text
from sanic import json
import asyncpg
from somex import db, row_exists
from sanic.exceptions import MethodNotAllowed, ServerError, BadRequest, NotFound
from internal.validator.validator import Validator, Validations
from functools import wraps
from urllib.parse import urlparse, parse_qs
from ..middleware.middleware import authorized


def check_valid_id():
    def decorator(f):
        @wraps(f)
        async def decorated_function(request, *args, **kwargs):
            id = kwargs['id']
            try:
                id = int(id)
                kwargs['id'] = id
            except ValueError:
                raise BadRequest("ID must be an INTEGER")
            return await f(request, *args, **kwargs)
        
        return decorated_function
    return decorator

class BooksByID(HTTPMethodView):

  decorators = [check_valid_id(),
                authorized()]

  async def get(self, request, user, id):
    print('User: ', user)

    url = request.url
    parsed_url = urlparse(url)
    params = parse_qs(parsed_url.query)

    cond = ['is_active', 'id = $1']
    cond_vars = [id]

    if 'query' in params:
      query = params['query'][0]
      cond.append('book_name ILIKE $2')
      cond_vars.append(f'%{query}%')
      print(cond_vars)

    condition = ' AND '.join(cond)

    row = await db.fetchrow('SELECT * FROM books WHERE {condition}'.format(condition=condition), *cond_vars)
    if row:
      # l = list(row)
      return json(dict(row))
    else:
      raise NotFound(f"No book found with ID {id}")
  
  # async def post(self, request, id):
    # book_name = request.form.get("book_name")
    # book_author = request.form.get("book_author")
    # book_descr = request.form.get("book_descr")
    # published = request.form.get("description")

  async def delete(self, request, user, id):
    if not await row_exists(id):
      raise NotFound(f"No book found with ID {id}")
    try:
      stmt =  "UPDATE books SET is_active = false  WHERE id = $1 RETURNING *"
      result = await db.fetchrow(stmt, id)
      if result == None:
         return json ({"error": "such user not found"})
      return json(dict(result))
    except asyncpg.exceptions.PostgresError as e:
        return json({"error": str(e)})


  async def put(self, request, user, id):
    v = Validator()
    book_name = request.form.get("book_name")
    book_author = request.form.get("book_author")
    book_descr = request.form.get("book_descr")
    published = request.form.get("published")

    v.CheckField(Validations.is_not_blank(book_name),'book_name', "This field cannot be blank")
    v.CheckField(Validations.is_valid_str(book_name, 1, 30), 'book_name', "This field cannot be more than 30 characters long")
    v.CheckField(Validations.is_not_blank(book_author),'book_author', "This field cannot be blank")
    v.CheckField(Validations.is_valid_str(book_author, 1, 20), 'book_author', "This field cannot be more than 20 characters long")
    v.CheckField(Validations.is_not_blank(book_descr),'book_descr', "This field cannot be blank")
    v.CheckField(Validations.is_valid_str(book_descr, 1, 700), 'book_descr', "This field cannot be more than 700 characters long")
    v.CheckField(Validations.is_integer(published), "published", "This field must be an integer")

    if not v.Valid():
      return text(str(v.FieldErrors))
    
    stmt = "UPDATE books SET author = $1, book_descr = $2, published = $3, book_name = $4 WHERE id = $5 RETURNING *"
    try:
        result = await db.fetchrow(stmt, book_author, book_descr, int(published), book_name, int(id))
        # Check for error

        result = dict(result)
    
        if result == 'UPDATE 0':
            return json({'error': f"No book found with name '{book_name}' to update."})
        else:
            print(f"Book '{book_name}' updated successfully.")

    except asyncpg.exceptions.PostgresError as e:
        return json({"error": str(e)})

    return json(result)

