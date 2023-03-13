from aiogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton

remove = ReplyKeyboardRemove()


def cancel() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton('Cancel')]
    ], resize_keyboard=True)
    return kb


def contact() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton('Send contact', request_contact=True)],
        [KeyboardButton('Cancel')]
    ], resize_keyboard=True, one_time_keyboard=True)
    return kb
