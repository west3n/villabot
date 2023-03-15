from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from keyboards import inline, reply


class Searching(StatesGroup):
    rental_period = State()
    currency = State()
    budget = State()
    location = State()
    accommodation_type = State()
    amenities = State()


async def cmd_cancel(call: types.CallbackQuery, state: FSMContext):
    await call.message.delete()
    await state.finish()
    await call.message.answer('Action Canceled!')


async def rental_period(call: types.CallbackQuery):
    await call.message.edit_reply_markup()
    await call.message.answer("Please, answer the following questions about your future villa 🏠\n\n"
                              "Rental period:", reply_markup=inline.rental_period())
    await Searching.rental_period.set()


async def currency(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['rental_period'] = call.data
    await call.bot.edit_message_text(chat_id=call.message.chat.id,
                                     message_id=call.message.message_id,
                                     text='Choose your currency:',
                                     reply_markup=inline.currency())
    await Searching.next()


async def budget(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['currency'] = call.data
    currency_data = data.get('currency')
    if currency_data == 'usd':
        await call.bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text='Choose your budget\n(You can choose several answers)',
            reply_markup=inline.budget_usd())
        await Searching.next()
    elif currency_data == 'rupiah':
        await call.bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text='Choose your budget\n(You can choose several answers)',
            reply_markup=inline.budget_rupiah())
        await Searching.next()


async def budget_callback_changer(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['budget'] = call.data
        budget_button = data.get('budget')
        if budget_button == '650$':
            kb = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton('✓<650$', callback_data='✓650$')],
                [InlineKeyboardButton('650 - 1300$', callback_data='650_1300$')],
                [InlineKeyboardButton('1300 - 1950$', callback_data='1300_1950$')],
                [InlineKeyboardButton('1950 - 2600$', callback_data='1950_2600$')],
                [InlineKeyboardButton('2600 - 3250$', callback_data='2600_3250$')],
                [InlineKeyboardButton('>3250$', callback_data='3250$')],
                [InlineKeyboardButton('Done', callback_data='done'),
                 InlineKeyboardButton('Cancel', callback_data='cancel')]
            ])
            await call.bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text='Choose your budget\n(You can choose several answers)',
                reply_markup=kb)
        elif budget_button == '650_1300$':
            kb = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton('<650$', callback_data='650$')],
                [InlineKeyboardButton('✓650 - 1300$', callback_data='✓650_1300$')],
                [InlineKeyboardButton('1300 - 1950$', callback_data='1300_1950$')],
                [InlineKeyboardButton('1950 - 2600$', callback_data='1950_2600$')],
                [InlineKeyboardButton('2600 - 3250$', callback_data='2600_3250$')],
                [InlineKeyboardButton('>3250$', callback_data='3250$')],
                [InlineKeyboardButton('Done', callback_data='done'),
                 InlineKeyboardButton('Cancel', callback_data='cancel')]
            ])
            await call.bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text='Choose your budget\n(You can choose several answers)',
                reply_markup=kb)
        elif budget_button == '1300_1950$':
            kb = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton('<650$', callback_data='650$')],
                [InlineKeyboardButton('650 - 1300$', callback_data='650_1300$')],
                [InlineKeyboardButton('✓1300 - 1950$', callback_data='✓1300_1950$')],
                [InlineKeyboardButton('1950 - 2600$', callback_data='1950_2600$')],
                [InlineKeyboardButton('2600 - 3250$', callback_data='2600_3250$')],
                [InlineKeyboardButton('>3250$', callback_data='3250$')],
                [InlineKeyboardButton('Done', callback_data='done'),
                 InlineKeyboardButton('Cancel', callback_data='cancel')]
            ])
            await call.bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text='Choose your budget\n(You can choose several answers)',
                reply_markup=kb)
        elif budget_button == '1950_2600$':
            kb = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton('<650$', callback_data='650$')],
                [InlineKeyboardButton('650 - 1300$', callback_data='650_1300$')],
                [InlineKeyboardButton('1300 - 1950$', callback_data='1300_1950$')],
                [InlineKeyboardButton('✓1950 - 2600$', callback_data='✓1950_2600$')],
                [InlineKeyboardButton('2600 - 3250$', callback_data='2600_3250$')],
                [InlineKeyboardButton('>3250$', callback_data='3250$')],
                [InlineKeyboardButton('Done', callback_data='done'),
                 InlineKeyboardButton('Cancel', callback_data='cancel')]
            ])
            await call.bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text='Choose your budget\n(You can choose several answers)',
                reply_markup=kb)
        await Searching.next()


def register(dp: Dispatcher):
    dp.register_callback_query_handler(rental_period, lambda c: c.data == "get_started")
    dp.register_callback_query_handler(cmd_cancel, text='cancel', state='*')
    dp.register_callback_query_handler(currency, lambda c: c.data in ('DAY', 'MONTH', 'YEAR'),
                                       state=Searching.rental_period)
    dp.register_callback_query_handler(budget, lambda c: c.data in ('usd', 'rupiah'),
                                       state=Searching.currency)
    dp.register_callback_query_handler(budget_callback_changer,
                                       lambda c: c.data in ('650$', '650_1300$', '1300_1950$', '1950_2600$',
                                                            '2600_3250$', '650_1300$', '3250$', '10mln',
                                                            '10mln_20mln', '20mln_30mln', '30mln_40mln',
                                                            '40mln_50mln', '50mln'),
                                       state=Searching.budget)
