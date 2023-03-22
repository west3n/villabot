from aiogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton

remove = ReplyKeyboardRemove()


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


def contact(lang) -> ReplyKeyboardMarkup:
    if lang in ['EN', 'IN']:
        kb = ReplyKeyboardMarkup(keyboard=[
            [KeyboardButton('Send contact', request_contact=True)],
            [KeyboardButton('Cancel')]
        ], resize_keyboard=True, one_time_keyboard=True)
        return kb
    elif lang == 'RU':
        kb = ReplyKeyboardMarkup(keyboard=[
            [KeyboardButton('Отправить контакт', request_contact=True)],
            [KeyboardButton('Отмена')]
        ], resize_keyboard=True, one_time_keyboard=True)
        return kb
