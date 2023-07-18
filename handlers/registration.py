from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from keyboards.inline import language
from keyboards.reply import register_cancel, remove, contact
from database.postgre_user import add_user, status, update_user, lang
from database.postgre_statistic import start_register_stat, finish_register_stat
from decouple import config
from oauth2client.service_account import ServiceAccountCredentials


import gspread
import datetime


class Registration(StatesGroup):
    # first_name = State()
    # contact = State()
    lang = State()
    # phone = State()


sheet_url = config("SHEET_URL")
credentials_path = "json/villabot-382008-e3b439d175c9.json"
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
credentials = ServiceAccountCredentials.from_json_keyfile_name(credentials_path, scope)
gc = gspread.authorize(credentials)
sh = gc.open_by_url(sheet_url)
worksheet = sh.worksheet('Users')


# async def registration_step_1(call: types.CallbackQuery):
#     start_register_stat()
#     await call.message.delete()
#     await call.message.answer(f'Enter your Name:', reply_markup=register_cancel())
#     await Registration.first_name.set()


# async def registration_step_1_2(message: types.Message):
#     start_register_stat()
#     await message.delete()
#     await message.answer(f'Enter your Name:', reply_markup=register_cancel())
#     await Registration.first_name.set()


# async def registration_step_3(msg: types.Message, state: FSMContext):
#     async with state.proxy() as data:
#         data['first_name'] = msg.text
#     await msg.answer(f'Please send your contact or write your phone number', reply_markup=contact())
#     await Registration.next()


async def registration_step_4(msg: types.Message, state: FSMContext):
    # text = msg.text
    # async with state.proxy() as data:
    #     if text is None:
    #         data['contact'] = msg.contact.phone_number
    start_register_stat()
    await msg.answer(f'Choose a language for the bot.',
                     reply_markup=language())
    await Registration.lang.set()


async def registration_step_4_2(call: types.CallbackQuery, state: FSMContext):
    # text = msg.text
    # async with state.proxy() as data:
    #     if text is None:
    #         data['contact'] = msg.contact.phone_number
    start_register_stat()
    await call.message.edit_text(f'Choose a language for the bot.',
                                 reply_markup=language())
    await Registration.lang.set()


# elif text.startswith("+"):
#     text = text.replace("+", "")
#     if text.isdigit():
#         data['contact'] = msg.text
#         await msg.answer(f'Choose a language for the bot.',
#                          reply_markup=language())
#         await Registration.next()
#     else:
#         await msg.answer('Wrong data, try again')
# elif text.isdigit():
#     data['contact'] = msg.text
#     await msg.answer(f'Choose a language for the bot.',
#                      reply_markup=language())
#     await Registration.next()
# else:
#     await msg.answer('Wrong data, try again')


async def registration_finish(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup()
    async with state.proxy() as data:
        data['lang'] = call.data
    username = call.from_user.username
    if username is None:
        username = 'No username'
    full_name = call.from_user.full_name
    if full_name is None:
        full_name = 'No full name'
    tg_id = int(call.from_user.id)
    start_register = datetime.datetime.now()
    last_activity = start_register
    stat = await status(tg_id)
    cell_list = worksheet.findall(str(tg_id), in_column=1)
    first_name = " "
    contact_data = " "
    if stat:
        await state.finish()
        await call.message.answer(f'Update profile complete! Please, press command /start', reply_markup=remove)
        await update_user(username, tg_id, start_register, last_activity, data, full_name)
        row_index = cell_list[0].row
        user_data = [tg_id,
                     username,
                     # str(data.get("first_name")),
                     first_name,
                     full_name,
                     contact_data,
                     # data.get("contact"),
                     data.get('lang'),
                     start_register.strftime("%Y-%m-%d %H:%M:%S"),
                     last_activity.strftime("%Y-%m-%d %H:%M:%S")]
        for i in range(len(user_data)):
            worksheet.update_cell(row_index, i + 1, user_data[i])
    else:
        await add_user(username, tg_id, start_register, last_activity, data, full_name)
        await state.finish()
        finish_register_stat()
        await call.message.answer(f'Registration complete! Please, press command /start', reply_markup=remove)
        user_data = [tg_id,
                     username,
                     first_name,
                     # str(data.get("first_name")),
                     full_name,
                     contact_data,
                     # data.get("contact"),
                     data.get('lang'),
                     start_register.strftime("%Y-%m-%d %H:%M:%S"),
                     last_activity.strftime("%Y-%m-%d %H:%M:%S")]
        worksheet.append_row(user_data)


async def cmd_cancel(msg: types.Message, state: FSMContext):
    await msg.delete()
    await state.finish()
    await msg.answer('Action Canceled!', reply_markup=remove)


async def sh_update_last_activity(tg_id):
    cell_list = worksheet.findall(str(tg_id), in_column=1)
    row_index = cell_list[0].row
    activity = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    worksheet.update_cell(row_index, 8, activity)


def register(dp: Dispatcher):
    # dp.register_callback_query_handler(registration_step_1, text='register')
    # dp.register_message_handler(registration_step_1_2, commands='profile', state="*")
    dp.register_message_handler(cmd_cancel, text=['Cancel', 'Отмена'], state='*')
    # dp.register_message_handler(registration_step_3, state=Registration.first_name)
    dp.register_callback_query_handler(registration_step_4_2, text="register")
    dp.register_message_handler(registration_step_4,
                                # content_types=[types.ContentType.TEXT, types.ContentType.CONTACT],
                                # state=Registration.contact
                                state="*",
                                commands='language')
    dp.register_callback_query_handler(registration_finish, state=Registration.lang)
