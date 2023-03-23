from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from keyboards.inline import language
from keyboards.reply import register_cancel, remove, contact
from database.postgre_user import add_user, status, update_user, lang
import datetime


class Registration(StatesGroup):
    first_name = State()
    contact = State()
    lang = State()
    phone = State()


async def registration_step_1(call: types.CallbackQuery):
    await call.message.delete()
    await call.message.answer(f'Enter your Name:', reply_markup=register_cancel())
    await Registration.first_name.set()


async def registration_step_3(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['first_name'] = msg.text
    await msg.answer(f'Please send your contact or write your phone number', reply_markup=contact())
    await Registration.next()


async def registration_step_4(msg: types.Message, state: FSMContext):
    text = msg.text
    async with state.proxy() as data:
        if text is None:
            data['contact'] = msg.contact.phone_number
            await msg.answer(f'Choose a language for the bot.',
                             reply_markup=language())
            await Registration.next()
        elif text.startswith("+"):
            text = text.replace("+", "")
            if text.isdigit():
                data['contact'] = msg.text
                await msg.answer(f'Choose a language for the bot.',
                                 reply_markup=language())
                await Registration.next()
            else:
                await msg.answer('Wrong data, try again')
        elif text.isdigit():
            data['contact'] = msg.text
            await msg.answer(f'Choose a language for the bot.',
                             reply_markup=language())
            await Registration.next()
        else:
            await msg.answer('Wrong data, try again')


async def registration_finish(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup()
    async with state.proxy() as data:
        data['lang'] = call.data
    username = call.from_user.username
    if username is None:
        username = 'No username'
    last_name = call.from_user.last_name
    if last_name is None:
        last_name = 'No surname in Telegram'
    tg_id = int(call.from_user.id)
    start_register = datetime.datetime.now()
    last_activity = start_register
    stat = await status(tg_id)
    if stat:
        await state.finish()
        await call.message.answer(f'Update profile complete! Please, press command /start', reply_markup=remove)
        await update_user(username, tg_id, start_register, last_activity, data, last_name)
    else:
        await add_user(username, tg_id, start_register, last_activity, data, last_name)
        await state.finish()
        await call.message.answer(f'Registration complete! Please, press command /start', reply_markup=remove)


async def cmd_cancel(msg: types.Message, state: FSMContext):
    await msg.delete()
    await state.finish()
    await msg.answer('Action Canceled!', reply_markup=remove)


def register(dp: Dispatcher):
    dp.register_callback_query_handler(registration_step_1, text='register')
    dp.register_message_handler(cmd_cancel, text=['Cancel', 'Отмена'], state='*')
    dp.register_message_handler(registration_step_3, state=Registration.first_name)
    dp.register_message_handler(registration_step_4, content_types=[types.ContentType.TEXT, types.ContentType.CONTACT],
                                state=Registration.contact)
    dp.register_callback_query_handler(registration_finish, state=Registration.lang)
