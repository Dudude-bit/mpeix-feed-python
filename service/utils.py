import asyncio
from typing import Optional

import markdown
from bs4 import BeautifulSoup
from datetime import datetime
from fastapi_cache import FastAPICache
from starlette.requests import Request
from starlette.responses import Response


def get_plain_text_from_markdown(markdown_text):
    markdown_obj = markdown.markdown(markdown_text)
    soup = BeautifulSoup(markdown_obj)
    return ''.join(soup.find_all(text=True))


def generate_link_from_post(owner_id, post_id):
    return f'https://vk.com/wall{owner_id}_{post_id}'


def get_datetime_from_timestamp(timestamp):
    datetime_obj = datetime.fromtimestamp(timestamp)
    return datetime_obj


async def get_institute_id_from_group(group, req: Request):
    pool = req.scope['pg_pool']
    conn = await pool.acquire()
    literal = group.split('-')[0].upper()
    query = 'select faculty_id from faculty_info where literas=$1'
    record = await conn.fetchrow(query, literal)
    if not record:
        return None
    return str(record['faculty_id'])


def build_key(func,
              namespace: Optional[str] = "",
              request: Request = None,
              response: Response = None,
              *args,
              **kwargs):
    faculty_id = kwargs['kwargs']['faculty_id']
    return str(faculty_id)
