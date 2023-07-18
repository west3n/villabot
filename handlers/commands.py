import datetime

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from database.postgre_user import status, update_activity
from keyboards import inline
from database.postgre_user import lang
from texts.text import get_text
from database.postgre_statistic import cmd_start_stat, link_stat
from handlers.registration import sh_update_last_activity
from google_analytics import analytics
from handlers.searching import rental_period_2


async def bot_start(msg: types.Message, state: FSMContext):
    await state.finish()
    tg_id = int(msg.from_id)
    user = await status(tg_id)
    name = msg.from_user.first_name
    if user:
        cmd_start_stat()
        await sh_update_last_activity(tg_id)
        last_activity = datetime.datetime.now()
        await update_activity(last_activity, tg_id)
        action = 1
        language = await lang(tg_id)
        text = await get_text(action, language)
        await msg.answer(text=f'{name}, {text}', reply_markup=inline.get_started(language))
    else:
        link_stat()
        await msg.answer(f'{name}, you are not registered, you need to login to start using the bot',
                         reply_markup=inline.register())


def register(dp: Dispatcher):
    dp.register_message_handler(bot_start, commands='start', state='*')
