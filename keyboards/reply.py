from aiogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton

remove = ReplyKeyboardRemove()


def register_cancel() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton('Cancel')]
    ], resize_keyboard=True)
    return kb


def cancel(lang) -> ReplyKeyboardMarkup:
    if lang in ['EN', 'IN']:
        kb = ReplyKeyboardMarkup(keyboard=[
            [KeyboardButton('Cancel')]
        ], resize_keyboard=True)
        return kb
    elif lang == 'RU':
        kb = ReplyKeyboardMarkup(keyboard=[
            [KeyboardButton('Отмена')]
        ], resize_keyboard=True)
        return kb


def contact() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton('Send contact', request_contact=True)],
        [KeyboardButton('Cancel')]
    ], resize_keyboard=True, one_time_keyboard=True)
    return kb
