from sanic import Blueprint
from sanic.response import text
from .item import BooksByID
from .list import Books

books = Blueprint('books', url_prefix='/books')

# books.add_route(Books.as_view(), '/')
books.add_route(BooksByID.as_view(), '/<id>')
books.add_route(Books.as_view(), '/')
