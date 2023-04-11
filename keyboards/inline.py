from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram import types

from aiogram.utils.callback_data import CallbackData
from database.postgre_location import get_location

location_callback = CallbackData("location", "name")


def register() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(inline_keyboard=[
        # [InlineKeyboardButton('Start registration', callback_data='register')]
        [InlineKeyboardButton('Select language', callback_data='register')]
    ])
    return kb


def language() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton('English', callback_data='EN')],
        [InlineKeyboardButton('Русский', callback_data='RU')],
        [InlineKeyboardButton('Bahasa Indonesia', callback_data='IN')]
    ])
    return kb


def get_started(lang) -> InlineKeyboardMarkup:
    if lang in ['EN', 'IN']:
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton('Find apartments', callback_data='get_started')],
            [InlineKeyboardButton('Show favorites', callback_data='show_favorite'),
             InlineKeyboardButton('Last saved request', callback_data='last_request')],
            # [InlineKeyboardButton('Edit profile', callback_data='register'),
            [InlineKeyboardButton('Change language', callback_data='register'),
             InlineKeyboardButton('Send feedback', callback_data='feedback')],
            [InlineKeyboardButton('I am a real estate agent', callback_data='Real estate agent')]
        ])
        return kb
    elif lang == 'RU':
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton('Найти апартаменты', callback_data='get_started')],
            [InlineKeyboardButton('Показать избранное', callback_data='show_favorite')],
            [InlineKeyboardButton('Последний сохраненный запрос', callback_data='last_request')],
            # [InlineKeyboardButton('Изменить профиль', callback_data='register'),
            [InlineKeyboardButton('Изменить язык', callback_data='register'),
             InlineKeyboardButton('Отправить отзыв', callback_data='feedback')],
            [InlineKeyboardButton('Я агент недвижимости', callback_data='Real estate agent')]
        ])
        return kb


def rental_period(lang) -> InlineKeyboardMarkup:
    if lang in ['EN', 'IN']:
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton('Daily', callback_data='DAY')],
            [InlineKeyboardButton('Monthly', callback_data='MONTH')],
            [InlineKeyboardButton('Yearly', callback_data='YEAR')],
            [InlineKeyboardButton('Back', callback_data='back'),
             InlineKeyboardButton('Cancel', callback_data='cancel')]
        ])
        return kb
    elif lang == 'RU':
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton('День', callback_data='DAY')],
            [InlineKeyboardButton('Месяц', callback_data='MONTH')],
            [InlineKeyboardButton('Год', callback_data='YEAR')],
            [InlineKeyboardButton('Назад', callback_data='back'),
             InlineKeyboardButton('Отмена', callback_data='cancel')]
        ])
        return kb


def currency(lang) -> InlineKeyboardMarkup:
    if lang in ['EN', 'IN']:
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton('USD', callback_data='usd')],
            [InlineKeyboardButton('Rupiah', callback_data='rupiah')],
            [InlineKeyboardButton('Back', callback_data='back'),
             InlineKeyboardButton('Cancel', callback_data='cancel')]
        ])
        return kb
    elif lang == 'RU':
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton('Доллары', callback_data='usd')],
            [InlineKeyboardButton('Рупии', callback_data='rupiah')],
            [InlineKeyboardButton('Назад', callback_data='back'),
             InlineKeyboardButton('Отмена', callback_data='cancel')]
        ])
        return kb


def kb_location(lang) -> InlineKeyboardMarkup:
    locations = get_location()
    kb = InlineKeyboardMarkup()
    if lang in ['EN', 'IN']:
        button_cancel = InlineKeyboardButton(text='Cancel', callback_data='cancel')
        for location in locations:
            button = InlineKeyboardButton(text=location[0], callback_data=location_callback.new(name=location[0]))
            kb.add(button)
        kb.add(button_cancel)
        return kb
    elif lang == 'RU':
        button_cancel = InlineKeyboardButton(text='Отмена', callback_data='cancel')
        for location in locations:
            button = InlineKeyboardButton(text=location[0], callback_data=location_callback.new(name=location[0]))
            kb.add(button)
        kb.add(button_cancel)
        return kb


def show_budget_options(call: types.CallbackQuery, rent, lang) -> InlineKeyboardMarkup:
    if call.data == 'usd':
        options = []
        if rent == 'MONTH':
            options = ['less than 650$', '650 - 1300$', '1300 - 1950$',
                       '1950 - 2600$', '2600 - 3250$', 'more than 3250$']
        elif rent == 'DAY':
            options = ['less than 20$', '20 - 50$', '50 - 70$',
                       '70 - 100$', '100 - 140$', 'more than 140$']
        elif rent == 'YEAR':
            options = ['less than 8000$', '8000 - 16000$',
                       '16000 - 24000$', '24000 - 32000$', '32000 - 40000$', 'more than 40000$']
        keyboard = InlineKeyboardMarkup()
        for option in options:
            button = InlineKeyboardButton(option, callback_data=f"select_option:{option}")
            keyboard.add(button)
        if lang in ['EN', 'IN']:
            keyboard.add(InlineKeyboardButton("Back", callback_data='back'),
                         InlineKeyboardButton("Next", callback_data="done"))
            keyboard.add(InlineKeyboardButton("Cancel", callback_data="cancel"))
        elif lang == 'RU':
            keyboard.add(InlineKeyboardButton("Назад", callback_data='back'),
                         InlineKeyboardButton("Дальше", callback_data="done"))
            keyboard.add(InlineKeyboardButton("Отмена", callback_data="cancel"))
        for row in keyboard.inline_keyboard:
            for button in row:
                if button.callback_data == "done":
                    row.remove(button)
            return keyboard
    elif call.data or call == 'rupiah':
        options = []
        if rent == 'MONTH':
            options = ["less than 10 mln", "10 mln - 20 mln", "20 mln - 30 mln",
                       "30 mln - 40 mln", "40 mln - 50 mln", "more than 50 mln"]
        elif rent == 'DAY':
            options = ["less than 300k", "300k - 700k", "700k - 1 mln",
                       "1 mln - 1,5 mln", "1,5 mln - 2 mln", "more than 2 mln"]
        elif rent == 'YEAR':
            options = ["less than 120 mln", "120 mln - 240 mln", "240 mln - 360 mln",
                       "360 mln - 480 mln", "480 mln - 600 mln", "More than 600 mln"]
        keyboard = InlineKeyboardMarkup()
        for option in options:
            button = InlineKeyboardButton(option, callback_data=f"select_option:{option}")
            keyboard.add(button)
        if lang in ['EN', 'IN']:
            keyboard.add(InlineKeyboardButton("Back", callback_data='back'),
                         InlineKeyboardButton("Next", callback_data="done"))
            keyboard.add(InlineKeyboardButton("Cancel", callback_data="cancel"))
        elif lang == 'RU':
            keyboard.add(InlineKeyboardButton("Назад", callback_data='back'),
                         InlineKeyboardButton("Дальше", callback_data="done"))
            keyboard.add(InlineKeyboardButton("Отмена", callback_data="cancel"))
        for row in keyboard.inline_keyboard:
            for button in row:
                if button.callback_data == "done":
                    row.remove(button)
            return keyboard


def show_budget_options_state(state_data, rent, lang) -> InlineKeyboardMarkup:
    if state_data == 'usd':
        options = []
        if rent == 'MONTH':
            options = ['less than 650$', '650 - 1300$', '1300 - 1950$',
                       '1950 - 2600$', '2600 - 3250$', 'more than 3250$']
        elif rent == 'DAY':
            options = ['less than 20$', '20 - 50$', '50 - 70$',
                       '70 - 100$', '100 - 140$', 'more than 140$']
        elif rent == 'YEAR':
            options = ['less than 8000$', '8000 - 16000$',
                       '16000 - 24000$', '24000 - 32000$', '32000 - 40000$', 'more than 40000$']

        keyboard = InlineKeyboardMarkup()
        for option in options:
            button = InlineKeyboardButton(option, callback_data=f"select_option:{option}")
            keyboard.add(button)
        if lang in ['EN', 'IN']:
            keyboard.add(InlineKeyboardButton("Back", callback_data='back'),
                         InlineKeyboardButton("Next", callback_data="done"))
            keyboard.add(InlineKeyboardButton("Cancel", callback_data="cancel"))
        elif lang == 'RU':
            keyboard.add(InlineKeyboardButton("Назад", callback_data='back'),
                         InlineKeyboardButton("Дальше", callback_data="done"))
            keyboard.add(InlineKeyboardButton("Отмена", callback_data="cancel"))
        for row in keyboard.inline_keyboard:
            for button in row:
                if button.callback_data == "done":
                    row.remove(button)
            return keyboard
    elif state_data == 'rupiah':
        options = []
        if rent == 'MONTH':
            options = ["less than 10 mln", "10 mln - 20 mln", "20 mln - 30 mln",
                       "30 mln - 40 mln", "40 mln - 50 mln", "more than 50 mln"]
        elif rent == 'DAY':
            options = ["less than 300k", "300k - 700k", "700k - 1 mln",
                       "1 mln - 1,5 mln", "1,5 mln - 2 mln", "more than 2 mln"]
        elif rent == 'YEAR':
            options = ["less than 120 mln", "120 mln - 240 mln", "240 mln - 360 mln",
                       "360 mln - 480 mln", "480 mln - 600 mln", "More than 600 mln"]
        keyboard = InlineKeyboardMarkup()
        for option in options:
            button = InlineKeyboardButton(option, callback_data=f"select_option:{option}")
            keyboard.add(button)
        if lang in ['EN', 'IN']:
            keyboard.add(InlineKeyboardButton("Back", callback_data='back'),
                         InlineKeyboardButton("Next", callback_data="done"))
            keyboard.add(InlineKeyboardButton("Cancel", callback_data="cancel"))
        elif lang == 'RU':
            keyboard.add(InlineKeyboardButton("Назад", callback_data='back'),
                         InlineKeyboardButton("Дальше", callback_data="done"))
            keyboard.add(InlineKeyboardButton("Отмена", callback_data="cancel"))
        for row in keyboard.inline_keyboard:
            for button in row:
                if button.callback_data == "done":
                    row.remove(button)
            return keyboard


def show_location_options(lang) -> InlineKeyboardMarkup:
    if lang in ['EN', 'IN']:
        keyboard = InlineKeyboardMarkup()
        locations = get_location()
        for location in locations:
            button = InlineKeyboardButton(location[0], callback_data=f"select_option:{location[0]}")
            keyboard.add(button)
        keyboard.add(InlineKeyboardButton("Back", callback_data='back'),
                     InlineKeyboardButton("Next", callback_data="done"))
        keyboard.add(InlineKeyboardButton("Cancel", callback_data="cancel"))
        for row in keyboard.inline_keyboard:
            for button in row:
                if button.callback_data == "done":
                    row.remove(button)
            return keyboard
    elif lang == 'RU':
        keyboard = InlineKeyboardMarkup()
        locations = get_location()
        for location in locations:
            button = InlineKeyboardButton(location[0], callback_data=f"select_option:{location[0]}")
            keyboard.add(button)
        keyboard.add(InlineKeyboardButton("Назад", callback_data='back'),
                     InlineKeyboardButton("Дальше", callback_data="done"))
        keyboard.add(InlineKeyboardButton("Отмена", callback_data="cancel"))
        for row in keyboard.inline_keyboard:
            for button in row:
                if button.callback_data == "done":
                    row.remove(button)
            return keyboard


def show_accommodation_type_options(lang) -> InlineKeyboardMarkup:
    options = ['Villa Entirely', 'Room in a shared villa', 'Apartments',
               'Guesthouse']
    keyboard = InlineKeyboardMarkup()
    for option in options:
        button = InlineKeyboardButton(option, callback_data=f"select_option:{option}")
        keyboard.add(button)
    if lang in ['EN', 'IN']:
        keyboard.add(InlineKeyboardButton("Back", callback_data='back'),
                     InlineKeyboardButton("Next", callback_data="done"))
        keyboard.add(InlineKeyboardButton("Cancel", callback_data="cancel"))
    elif lang == 'RU':
        keyboard.add(InlineKeyboardButton("Назад", callback_data='back'),
                     InlineKeyboardButton("Дальше", callback_data="done"))
        keyboard.add(InlineKeyboardButton("Отмена", callback_data="cancel"))
    for row in keyboard.inline_keyboard:
        for button in row:
            if button.callback_data == "done":
                row.remove(button)
        return keyboard


def show_amenities_options(lang) -> InlineKeyboardMarkup:
    options = ['Kitchen', 'AC', 'Private pool', 'Shared pool', 'Wi-Fi', 'Shower', 'Bathtub', 'Cleaning service', 'TV',
               'Parking area']
    keyboard = InlineKeyboardMarkup()
    for option in options:
        button = InlineKeyboardButton(option, callback_data=f"select_option:{option}")
        keyboard.add(button)
    if lang in ['EN', 'IN']:
        keyboard.add(InlineKeyboardButton("Back", callback_data='back'),
                     InlineKeyboardButton("Next", callback_data="done"))
        keyboard.add(InlineKeyboardButton("Cancel", callback_data="cancel"))
    elif lang == 'RU':
        keyboard.add(InlineKeyboardButton("Назад", callback_data='back'),
                     InlineKeyboardButton("Дальше", callback_data="done"))
        keyboard.add(InlineKeyboardButton("Отмена", callback_data="cancel"))
    for row in keyboard.inline_keyboard:
        for button in row:
            if button.callback_data == "done":
                row.remove(button)
        return keyboard


def searching(lang) -> InlineKeyboardMarkup:
    if lang in ['EN', 'IN']:
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton('Back', callback_data='back'),
             InlineKeyboardButton('Save this request', callback_data='save')],
            [InlineKeyboardButton('Search', callback_data='searching')],
            [InlineKeyboardButton('Cancel', callback_data='cancel')]
        ])
        return kb
    elif lang == 'RU':
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton('Назад', callback_data='back'),
             InlineKeyboardButton('Сохранить запрос', callback_data='save')],
            [InlineKeyboardButton('Поиск', callback_data='searching')],
            [InlineKeyboardButton('Отмена', callback_data='cancel')]
        ])
        return kb


def searching_2(lang) -> InlineKeyboardMarkup:
    if lang in ['EN', 'IN']:
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton('Back', callback_data='back')],
            [InlineKeyboardButton('Search', callback_data='searching')],
            [InlineKeyboardButton('Cancel', callback_data='cancel')]
        ])
        return kb
    elif lang == 'RU':
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton('Назад', callback_data='back')],
            [InlineKeyboardButton('Поиск', callback_data='searching')],
            [InlineKeyboardButton('Отмена', callback_data='cancel')]
        ])
        return kb


def apartment_contacts(ap, lang) -> InlineKeyboardMarkup:
    if lang in ['EN', 'IN']:
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton('See contacts', callback_data=f'contact_{ap}'),
             InlineKeyboardButton('Save to favourites', callback_data=f'save_{ap}')]
        ])
        return kb
    elif lang == 'RU':
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton('Посмотреть контакты', callback_data=f'contact_{ap}'),
             InlineKeyboardButton('Сохранить в избранное', callback_data=f'save_{ap}')]
        ])
        return kb


def contacts(ap, lang) -> InlineKeyboardMarkup:
    if lang in ['EN', 'IN']:
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton('See contacts', callback_data=f'contact_{ap}')]
        ])
        return kb
    elif lang == 'RU':
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton('Посмотреть контакты', callback_data=f'contact_{ap}')]
        ])
        return kb


def contacts_favorites(ap, lang) -> InlineKeyboardMarkup:
    if lang in ['EN', 'IN']:
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton('See contacts', callback_data=f'contact_favorites_{ap}'),
             InlineKeyboardButton('Remove from favorites', callback_data=f'remove_{ap}')]
        ])
        return kb
    elif lang == 'RU':
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton('Посмотреть контакты', callback_data=f'contact_favorites_{ap}'),
             InlineKeyboardButton('Убрать из избранного', callback_data=f'remove_{ap}')]
        ])
        return kb


def favorites(ap, lang) -> InlineKeyboardMarkup:
    if lang in ['EN', 'IN']:
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton('Save to favourites', callback_data=f'save_{ap}')]
        ])
        return kb
    elif lang == 'RU':
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton('Сохранить в избранное', callback_data=f'save_{ap}')]
        ])
        return kb


def subscribe(lang) -> InlineKeyboardMarkup:
    if lang in ['EN', 'IN']:
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton('Take subscription for one month', callback_data='subscription_on')],
            [InlineKeyboardButton('Maybe later', callback_data='cancel')]
        ])
        return kb
    elif lang == 'RU':
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton('Приобрести месячную подписку', callback_data='subscription_on')],
            [InlineKeyboardButton('Возможно позже', callback_data='cancel')]
        ])
        return kb


def feedback(lang) -> InlineKeyboardMarkup:
    if lang in ['EN', 'IN']:
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton('Problems with the bot', callback_data='Problems with the bot')],
            [InlineKeyboardButton('False information in offers', callback_data='False information in offers')],
            [InlineKeyboardButton('Communication with offer owner',
                                  callback_data='Communication with the owner of the ad')],
            [InlineKeyboardButton('Other', callback_data='Other')],
            [InlineKeyboardButton('Cancel', callback_data='cancel')]
        ])
        return kb
    elif lang == 'RU':
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton('Проблемы в работе бота', callback_data='Problems with the bot')],
            [InlineKeyboardButton('Недостоверная информация в предложениях',
                                  callback_data='False information in offers')],
            [InlineKeyboardButton('Связь с владельцем объявления',
                                  callback_data='Communication with the owner of the ad')],
            [InlineKeyboardButton('Другое', callback_data='Other')],
            [InlineKeyboardButton('Отмена', callback_data='cancel')]
        ])
        return kb


def request(lang) -> InlineKeyboardMarkup:
    if lang in ['EN', 'IN']:
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton('Change request', callback_data='get_started')],
            [InlineKeyboardButton('Get updates', callback_data='request_searching')]
        ])
        return kb
    elif lang == 'RU':
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton('Изменить запрос', callback_data='get_started')],
            [InlineKeyboardButton('Загрузить объявления', callback_data='request_searching')]
        ])
        return kb


def agent_link(url, lang) -> InlineKeyboardMarkup:
    if lang in ['EN', 'IN']:
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(f'Go to WhatsApp link', url=url)]
        ])
        return kb
    elif lang == 'RU':
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(f'Перейти по ссылке WhatsApp', url=url)]
        ])
        return kb
