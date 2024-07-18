import asyncio
import traceback
import asyncpg  # noqa
import redis.asyncio as redis
import ujson  # noqa


class PSQL:
    pool = None

    @staticmethod
    async def pool_connection_init(connection):
        for json_type in ['json', 'jsonb']:
            await connection.set_type_codec(
                json_type,
                encoder=ujson.dumps,
                decoder=ujson.loads,
                schema='pg_catalog'
            )

    async def initialize(self, loop, **kwargs):
        if not kwargs:
            return

        settings = dict(  # default
            # database
            # host
            # port
            # user
            # password
            min_size=1,
            max_size=5,
            command_timeout=300
        )
        settings.update(kwargs)

        print(self.pool, 'Connectio start')
        self.pool = await asyncpg.create_pool(
            init=self.pool_connection_init,
            loop=loop,
            **settings
        )
        print(self.pool)

    async def close(self):
        try:
            await asyncio.wait_for(self.pool.close(), 5)
        except (Exception,):
            traceback.print_exc()

    async def execute(self, *args, **kwargs):
        async with self.pool.acquire() as connection:
            return await connection.execute(*args, **kwargs)

    async def executemany(self, *args, **kwargs):
        async with self.pool.acquire() as db:
            return await db.executemany(*args, **kwargs)

    async def fetch(self, *args, **kwargs):
        async with self.pool.acquire() as connection:
            return await connection.fetch(*args, **kwargs)

    async def fetchrow(self, *args, **kwargs):
        async with self.pool.acquire() as connection:
            return await connection.fetchrow(*args, **kwargs)

    async def fetchval(self, *args, **kwargs):
        async with self.pool.acquire() as connection:
            return await connection.fetchval(*args, **kwargs)

    async def transaction(self, *args, **kwargs):
        async with self.pool._connection_class as connection:
            return await connection.transaction(*args, **kwargs)

    @staticmethod
    def log(method, *args, **kwargs):

        query = ' '.join(filter(lambda item: item and item != '\n', args[0].replace('\n', ' ').split(' ')))
        params = args[1:]
        log_text = f'DBProxy#{method}({query})'
        if params:
            log_text += f' | {params}'
        if kwargs:
            log_text += f' | {kwargs}'

db = PSQL()

class Cache:
    client = None
    async def initialize(self) -> None:
        print(self.client, 'redis connection start')
        self.pool = redis.ConnectionPool.from_url('redis://localhost:6379')
        self.client = redis.Redis.from_pool(self.pool)
        print("Ping: ", await self.client.ping())
        print(self.pool)

    async def setex(self, key, value, ttl=3600):
        return await self.client.setex(key, ttl, value)

    async def get(self, key):
        return await self.client.get(key)
        
    async def delete(self, key):
        return await self.client.delete(key)

    async def close(self):
        if self.client:
            await self.client.aclose()
            print("Redis connection pool closed")

cache = Cache()

async def row_exists(id):
    query = "SELECT EXISTS (SELECT 1 FROM books WHERE id = $1);"
    res = await db.fetchval(query, id)
    return res

async def table_exists(table_name):
    query = "SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = $1)"
    res = await db.fetchval(query, table_name)
    return res

async def get_column_names(table_name):
    query= f"SELECT column_name FROM information_schema.columns WHERE table_schema = 'public' AND table_name = '{table_name}'"
    rows = await db.fetch(query)
    column_names = [row[0] for row in rows]
    return column_names