import decouple
from aiohttp import ClientSession

MEASUREMENT_ID = decouple.config("MEASUREMENT_ID")
API_SECRET = decouple.config("API_SECRET")


async def send_analytics(user_id, user_lang_code, action_name):
    params = {
        'client_id': str(user_id),
        'user_id': str(user_id),
        'events': [{
            'name': action_name,
            'params': {
                'language': user_lang_code,
                'engagement_time_msec': '1',
            }
        }],
    }
    async with ClientSession() as session:
        await session.post(
                f'https://www.google-analytics.com/'
                f'mp/collect?measurement_id={MEASUREMENT_ID}&api_secret={API_SECRET}',
                json=params)
