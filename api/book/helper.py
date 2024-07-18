from somex import db, table_exists, get_column_names
from urllib.parse import urlparse, parse_qs

class helpers():
    @staticmethod
    async def get_num_pages(table, rows_per_page, column='', text=''):
        if not await table_exists(table):
            return 0
        
        if len(text) > 0:
            stmt = f"SELECT COUNT(*) FROM {table} WHERE {column} ILIKE '%{text}%'"
        else:
            stmt = f"SELECT COUNT(*) FROM {table}"
        
        total_rows = await db.fetchval(stmt)

        total_pages = int(total_rows) // int(rows_per_page)
        if total_rows % int(rows_per_page) != 0:
            total_pages += 1
        return total_pages
    
    @staticmethod
    def get_query(request):
        url = request.url
        parsed_url = urlparse(url)
        return parse_qs(parsed_url.query)
    
    @staticmethod
    def fetch_prm(arg, params):
        if arg in params:
            return params[arg]
        else:
            return False
        
    
    @staticmethod
    async def sort_by(arg):
        order = 'ASC'
        if ':' in arg:
            splitter = arg.split(':')
            column = splitter[0]

            if len(splitter) != 2:
                return column, order, "Too much args in 'sort_by'"
            order = splitter[1].upper() if splitter[1].upper() == 'DESC' else 'ASC'
        else:
            column = arg

        column_names = await get_column_names('books')
        if column not in column_names:
            return column, order, f'{column} is not valid. Accepted args: {column_names}'
        
        return column, order, 'ok'
    
    @staticmethod
    def checkNoneVal(val, defVal):
        if val == None:
            return defVal
        else:
            return val
        
    @staticmethod 
    async def fetch_txt_column(arg):
        column, pattern = 'book_name', ''
        if ':' in arg:
            splitter = arg.split(':')
            if len(splitter) != 2:
                return column, pattern, "only two arg allowed"
            column = splitter[0]
            pattern = splitter[1]
        else:
            pattern = arg
        column_names = await get_column_names('books')
        if column not in column_names:
            return column, pattern, f'{column} is not valid. Accepted args: {column_names}'
        
        return column, pattern, 'ok'
    
    