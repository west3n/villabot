from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from typing import List

from aiogram.utils.callback_data import CallbackData

from database.postgre_location import get_location

location_callback = CallbackData("location", "name")


def register() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton('Start registration', callback_data='register')]
    ])
    return kb


def language() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton('English', callback_data='EN')],
        [InlineKeyboardButton('Русский', callback_data='RU')],
        [InlineKeyboardButton('Bahasa Indonesia', callback_data='IN')]
    ])
    return kb


def get_started() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton('Get started', callback_data='get_started')]
    ])
    return kb


def rental_period() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton('Daily', callback_data='DAY')],
        [InlineKeyboardButton('Monthly', callback_data='MONTH')],
        [InlineKeyboardButton('Yearly', callback_data='YEAR')],
        [InlineKeyboardButton('Cancel', callback_data='cancel')]
    ])
    return kb


def currency() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton('USD', callback_data='usd')],
        [InlineKeyboardButton('Rupiah', callback_data='rupiah')],
        [InlineKeyboardButton('Cancel', callback_data='cancel')]
    ])
    return kb


def budget_usd() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton('<650$', callback_data='650$')],
        [InlineKeyboardButton('650 - 1300$', callback_data='650_1300$')],
        [InlineKeyboardButton('1300 - 1950$', callback_data='1300_1950$')],
        [InlineKeyboardButton('1950 - 2600$', callback_data='1950_2600$')],
        [InlineKeyboardButton('2600 - 3250$', callback_data='2600_3250$')],
        [InlineKeyboardButton('>3250$', callback_data='3250$')],
        [InlineKeyboardButton('Done', callback_data='done'),
         InlineKeyboardButton('Cancel', callback_data='cancel')]
    ])
    return kb


def budget_rupiah() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton('< 10 mln', callback_data='10mln')],
        [InlineKeyboardButton('10 mln - 20 mln', callback_data='10mln_20mln')],
        [InlineKeyboardButton('20 mln - 30 mln', callback_data='20mln_30mln')],
        [InlineKeyboardButton('30 mln - 40 mln', callback_data='30mln_40mln')],
        [InlineKeyboardButton('40 mln - 50 mln', callback_data='40mln_50mln')],
        [InlineKeyboardButton('> 50 mln', callback_data='50mln')],
        [InlineKeyboardButton('Done', callback_data='done'),
         InlineKeyboardButton('Cancel', callback_data='cancel')]
    ])
    return kb


def kb_location() -> InlineKeyboardMarkup:
    locations = get_location()
    kb = InlineKeyboardMarkup()
    button_cancel = InlineKeyboardButton(text='Cancel', callback_data='cancel')
    for location in locations:
        button = InlineKeyboardButton(text=location[0], callback_data=location_callback.new(name=location[0]))
        kb.add(button)
    kb.add(button_cancel)
    return kb


async def show_budget_options(call: types.CallbackQuery):
    if call.data == 'usd':
        options = ['less than 650$', '650 - 1300$', '1300 - 1950$',
                   '1950 - 2600$', '2600 - 3250$', 'more than 3250$']
        keyboard = InlineKeyboardMarkup()
        for option in options:
            button = InlineKeyboardButton(option, callback_data=f"select_option:{option}")
            keyboard.add(button)
        keyboard.add(InlineKeyboardButton("Done", callback_data="done"),
                     InlineKeyboardButton("Cancel", callback_data="cancel"))
        for row in keyboard.inline_keyboard:
            for button in row:
                if button.callback_data == "done":
                    row.remove(button)
            return keyboard
    elif call.data == 'rupiah':
        options = ["less than 10 mln", "10 mln - 20 mln", "20 mln - 30 mln",
                   "30 mln - 40 mln", "40 mln - 50 mln", "more than 50 mln"]
        keyboard = InlineKeyboardMarkup()
        for option in options:
            button = InlineKeyboardButton(option, callback_data=f"select_option:{option}")
            keyboard.add(button)
        keyboard.add(InlineKeyboardButton("Done", callback_data="done"),
                     InlineKeyboardButton("Cancel", callback_data="cancel"))
        for row in keyboard.inline_keyboard:
            for button in row:
                if button.callback_data == "done":
                    row.remove(button)
            return keyboard


def show_location_options():
    keyboard = InlineKeyboardMarkup()
    locations = get_location()
    for location in locations:
        button = InlineKeyboardButton(location[0], callback_data=f"select_option:{location[0]}")
        keyboard.add(button)
    keyboard.add(InlineKeyboardButton("Done", callback_data="done"),
                 InlineKeyboardButton("Cancel", callback_data="cancel"))
    for row in keyboard.inline_keyboard:
        for button in row:
            if button.callback_data == "done":
                row.remove(button)
        return keyboard


def show_accommodation_type_options():
    options = ['Villa Entirely', 'Room in a shared villa', 'Apartments',
               'Guesthouse']
    keyboard = InlineKeyboardMarkup()
    for option in options:
        button = InlineKeyboardButton(option, callback_data=f"select_option:{option}")
        keyboard.add(button)
    keyboard.add(InlineKeyboardButton("Done", callback_data="done"),
                 InlineKeyboardButton("Cancel", callback_data="cancel"))
    for row in keyboard.inline_keyboard:
        for button in row:
            if button.callback_data == "done":
                row.remove(button)
        return keyboard


def show_amenities_options():
    options = ['Kitchen', 'AC', 'Private pool', 'Shared pool', 'Wi-Fi', 'Shower', 'Bathtub', 'Cleaning service', 'TV',
               'Parking area']
    keyboard = InlineKeyboardMarkup()
    for option in options:
        button = InlineKeyboardButton(option, callback_data=f"select_option:{option}")
        keyboard.add(button)
    keyboard.add(InlineKeyboardButton("Done", callback_data="done"),
                 InlineKeyboardButton("Cancel", callback_data="cancel"))
    for row in keyboard.inline_keyboard:
        for button in row:
            if button.callback_data == "done":
                row.remove(button)
        return keyboard
