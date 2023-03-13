from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from keyboards.inline import language
from keyboards.reply import cancel, remove
from database.postgre_user import add_user
import datetime


class Registration(StatesGroup):
    first_name = State()
    last_name = State()
    lang = State()
    phone = State()


async def registration_step_1(call: types.CallbackQuery):
    await call.message.delete()
    await call.message.answer(f'Enter your Name:', reply_markup=cancel())
    await Registration.first_name.set()


async def registration_step_2(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['first_name'] = msg.text
    await msg.answer(f'Enter your Surname:')
    await Registration.next()


async def registration_step_3(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['last_name'] = msg.text
    await msg.answer(f'Choose a language for the bot.',
                     reply_markup=language())
    await Registration.next()


async def registration_finish(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup()
    async with state.proxy() as data:
        data['lang'] = call.data
    username = call.from_user.username
    tg_id = int(call.from_user.id)
    start_register = datetime.datetime.now()
    last_activity = start_register
    await add_user(username, tg_id, start_register, last_activity, data)
    await state.finish()
    await call.message.answer(f'Registration complete!', reply_markup=remove)


async def cmd_cancel(msg: types.Message, state: FSMContext):
    await msg.delete()
    await state.finish()
    await msg.answer('Action Canceled!', reply_markup=remove)


def register(dp: Dispatcher):
    dp.register_callback_query_handler(registration_step_1, text='register')
    dp.register_message_handler(cmd_cancel, text='Cancel', state='*')
    dp.register_message_handler(registration_step_2, state=Registration.first_name)
    dp.register_message_handler(registration_step_3, state=Registration.last_name)
    dp.register_callback_query_handler(registration_finish, state=Registration.lang)