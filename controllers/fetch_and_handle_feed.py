import asyncio
import aiohttp

from service.utils import generate_link_from_post, get_datetime_from_timestamp


async def fetch_and_handle_feed(BASE_URL, params, recourses, pool, answer_keys):
    data = dict()
    tasks = []

    for el in recourses['vk']:
        if el in answer_keys:
            tasks.append(asyncio.create_task(fetch_vk_and_handle_vk_feed(recourses['vk'][el]['id'], params,
                                                                         BASE_URL, pool, el,
                                                                         recourses['vk'][el]['meta'])))
    data['vk'] = []
    for task in asyncio.as_completed(tasks):
        data['vk'].append(await task)
    return data


async def fetch_vk_and_handle_vk_feed(id, params, BASE_URL, pool, recourse_id, meta):
    """
    Vk API return posts from the earliest to latest
    """
    params.update(
        {
            'owner_id': id
        }
    )
    async with aiohttp.ClientSession() as session:
        async with session.get(BASE_URL, params=params) as response:
            data = (await response.json())['response']
    """
    reverse to get the latest post as first item
    """
    posts = data['items'][::-1]
    tasks = []
    for post in posts:
        tasks.append(asyncio.create_task(save_vk_post_if_not_exists(post, pool, recourse_id)))
    saved_posts = await asyncio.gather(*tasks)

    return {'meta': meta, 'posts': saved_posts}


async def save_vk_post_if_not_exists(post, pool, recourse_id):
    conn = await pool.acquire()
    query = """insert into feed_data(created_at, updated_at, source, source_id, source_link, text, post_created, recourse_id)
            values
            (now(), now(), 'vk', $1, $2, $3, $4, $5)
            on conflict do nothing
            returning
            source_id, source_link, text, post_created
            """
    post['source_link'] = generate_link_from_post(post['owner_id'], post['id'])
    post['post_created'] = get_datetime_from_timestamp(post['date'])
    data = (post['id'],
            post['source_link'],
            post['text'],
            post['post_created'],
            recourse_id)
    await conn.execute(query, *data)
    await pool.release(conn)
    return {
        'source_id': post['id'],
        'source_link': post['source_link'],
        'text': post['text'],
        'post_created': post['post_created']
    }
