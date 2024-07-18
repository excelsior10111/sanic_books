from sanic.views import HTTPMethodView
from sanic.response import text, json
from somex import db
from .helper import helpers as h
from sanic.exceptions import BadRequest
from internal.validator.validator import Validator, Validations
from api.middleware.middleware import authorized
import asyncpg

class Pager:
    def __init__(self, page=1, limit=10) -> None:
        self.page = int(page) if page else 1
        self.limit = int(limit) if limit else 10
    
    def as_query(self):
        return f'LIMIT {self.limit} OFFSET {self.limit*(self.page-1)}'
    
class Sorter:
    def __init__(self, column='id', order='ASC') -> None:
        self.column = column
        self.order = order
    def as_query(self):
        return f'ORDER BY {self.column} {self.order}'


class Books(HTTPMethodView):
    decorators = [authorized()]
    async def get(self, request, user):
        v = Validator()
        limit = h.checkNoneVal(request.args.get('limit'), 15)
        page = h.checkNoneVal(request.args.get('page'), 1)
        sort_args = h.checkNoneVal(request.args.get('sort_by'), 'id')
        column, order, status = await h.sort_by(sort_args)
        if status != 'ok':
            v.AddFieldError('sort_by', status)

        query = h.checkNoneVal(request.args.get('query'), "book_name:")
        qcolumn, qtext, status = await h.fetch_txt_column(query)
        if status != 'ok':
            v.AddFieldError('query', status)

        total_pages = await h.get_num_pages('books', limit, qcolumn, qtext)

        v.CheckField(Validations.is_integer(limit), "Limit", "Page value must hold integer")
        v.CheckField(Validations.is_integer(page), "Page", "Page value must hold integer")

        if not v.Valid():
            return json(v.FieldErrors)

        if not 1 <= int(page) <= total_pages:
            raise BadRequest("This page doesn't exist")
        
        cond = ['is_active', f"{qcolumn} ILIKE '%{qtext}%'"]
        condition = ' AND '.join(cond)

        pager = Pager(page, limit)
        order = Sorter(column, order)
        try:
            data = await db.fetch("SELECT * FROM books WHERE {condition} {order} {pagination}".format(condition=condition, order=order.as_query(),pagination=pager.as_query()))
        except asyncpg.PostgresError as e:
            print(f"Database error: {e}")
        return json([dict(d) for d in data])

        
    async def post(self, request, user):
        v = Validator()
        book_name = request.form.get("book_name")
        book_author = request.form.get("book_author")
        book_descr = request.form.get("book_descr")
        published = request.form.get("published")

        v.CheckField(Validations.is_not_blank(book_name),'Book Name', "This field cannot be blank")
        v.CheckField(Validations.is_valid_str(book_name, 1, 30), 'Book Name', "This field cannot be more than 30 characters long")
        v.CheckField(Validations.is_not_blank(book_author),'Author', "This field cannot be blank")
        v.CheckField(Validations.is_valid_str(book_author, 1, 20), 'Author', "This field cannot be more than 20 characters long")
        v.CheckField(Validations.is_valid_str(book_descr, 0, 700), 'Description', "This field cannot be more than 700 characters long")
        v.CheckField(Validations.is_integer(published), "Published_Year", "This field must be an integer")
        v.CheckField(Validations.is_not_blank(published), "Published_Year", "This field cannot be blank")

        if not v.Valid():
            return text(str(v.FieldErrors))
        if book_descr == None:
            stmt = "INSERT INTO books(author, published, book_name) VALUES($1, $2, $3 RETURNING *"
            result = await db.fetchrow(stmt, book_author, int(published), book_name)
        else:
            stmt = "INSERT INTO books(author, book_descr, published, book_name) VALUES($1, $2, $3, $4) RETURNING *"
            result = await db.fetchrow(stmt, book_author, book_descr, int(published), book_name)
      
        if result:
            result_dict = dict(result)
        else:
            return None

        return json(result_dict)




