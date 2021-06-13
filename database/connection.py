
import ujson

from asyncpg.pool import create_pool


async def create_pg_pool(dsn, password, user):
    pool = await create_pool(
        dsn,
        password=password,
        user=user,
        init=init,
        min_size=10
    )
    return pool


async def init(conn):
    await conn.set_type_codec(
        'json',
        encoder=ujson.dumps,
        decoder=ujson.loads,
        schema='pg_catalog'
    )