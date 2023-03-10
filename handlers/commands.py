import datetime

from aiogram import Dispatcher, types
from database.postgre_user import status, update_activity
from keyboards import inline


async def bot_start(msg: types.Message):
    tg_id = int(msg.from_id)
    user = await status(tg_id)
    name = msg.from_user.first_name
    if user:
        last_activity = datetime.datetime.now()
        await update_activity(last_activity, tg_id)
        await msg.answer(f"Hello, {name}!")

    else:
        await msg.answer(f'{name}, you are not registered, you need to login to start using the bot',
                         reply_markup=inline.register())


def register(dp: Dispatcher):
    dp.register_message_handler(bot_start, commands='start', state='*')
