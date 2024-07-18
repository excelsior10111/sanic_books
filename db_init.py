# import asyncio
# import asyncpg
# from asyncio import sleep
# from models.models import books_db

# # class psql_db:
#     # def __init__

# QUERY = """INSERT INTO books (book_name, author, published, book_descr) VALUES($1, $2, $3, $4)"""


# async def make_request(db_pool):
#     await db_pool.fetch(QUERY, "The Legacy of Barack Obama","Obama",  2022, "The Legacy of Barack Obama stands as a monumental anthology that dives into the significant era of Barack Obama's presidency, featuring an array of essays that encapsulate the diversity and complexity of his eight years in office.")
#     print("Added new req")
#     await sleep(.1)

# async def run():
#     db_pool = await asyncpg.create_pool(database="my_db", user="postgres", password="postgres", host="127.0.0.1", port="5432")
#     chunk = 200
#     l = []
#     pended = 0

#     for i in range(1000):
#         l.append(asyncio.create_task(make_request(db_pool)))
#         pended+=1

#         if len(l) == chunk or pended == 10000:
#             await asyncio.gather(*l)
#             l = []
#             print(pended)

    

# loop = asyncio.get_event_loop()
# loop.run_until_complete(run())

# async def start():
#     try: 
#         pconn =  await psycopg2.connect(dbname="my_db", user="postgres", password="postgres", host="127.0.0.1", port="5432")
#     except:
#         print("Can't establish connection to database")

#     db2 = books_db(pconn) #creating an instance of class Books 
#     return db2
#     # pconn.close()

# db2 = start()

# import psycopg2

# def db_init():
#     from models.models import books_db

#     try: 
        # pconn = psycopg2.connect(dbname="my_db",  user="postgres", password="postgres", host="127.0.0.1", port="5432")
#     except:
#         print("Can't establish connection to database")

#     db2 = books_db(pconn) #creating an instance of class Books
#     pconn.close()
#     return db2 