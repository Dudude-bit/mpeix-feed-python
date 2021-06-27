import os
import ujson
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from fastapi_cache.decorator import cache
from fastapi.responses import UJSONResponse
from fastapi import Request, Depends
from fastapi import FastAPI

from controllers.fetch_and_handle_feed import fetch_and_handle_feed
from database.connection import create_pg_pool
from service.exception import MpeixException
from service.utils import get_institute_id_from_group, build_key

app = FastAPI(
    title='Feed MicroService',
    description='Feed MicroService For Mpeix',
    default_response_class=UJSONResponse

)


@app.exception_handler(500)
async def handle_exception(req: Request, exc: Exception):
    return UJSONResponse({
        'data': None,
        'error': str(exc)
    }, status_code=500)


@app.on_event('startup')
async def on_startup():
    global pool, recourses
    dsn = os.getenv('DB_URL')
    port = os.getenv('PORT')
    user = os.getenv('DB_USER')
    password = os.getenv('DB_PASSWORD')
    pool = await create_pg_pool(dsn, password, user)
    FastAPICache.init(InMemoryBackend())
    with open('static/json/recourses.json') as f:
        recourses = ujson.load(f)


@app.middleware('http')
async def add_pool_to_request_scope(req: Request, call_next):
    req.scope['pg_pool'] = pool
    response = await call_next(req)
    return response


@app.get('/v1/feed/{group}/')
@cache(expire=3600, key_builder=build_key)
async def get_feed(faculty_id: str = Depends(get_institute_id_from_group)):
    answer_keys = ['profcom_mpei', 'studsovet_mpei', faculty_id]
    API_VERSION = '5.131'
    TOKEN = os.getenv('VK_TOKEN', None)
    if TOKEN is None:
        raise MpeixException('define vk api token in system variables')
    params = {
        'v': API_VERSION,
        'access_token': TOKEN,
        'extended': 0,
        'count': 10

    }
    BASE_URL = 'https://api.vk.com/method/wall.get'
    data = await fetch_and_handle_feed(BASE_URL, params, recourses, pool, answer_keys)
    return {
        'feed': data
    }


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app)