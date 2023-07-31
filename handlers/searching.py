import asyncio
import locale
import os
import io

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import InlineKeyboardButton
from database.postgre_find import get_apart, get_location_name, get_image, save_request
from database.postgre_user import lang
from texts.text import get_text
from database.postgre_statistic import find_stat, search_stat, apartment_views_amount
from keyboards import inline
from google_analytics import analytics


class Searching(StatesGroup):
    rental_period = State()
    currency = State()
    budget = State()
    location = State()
    accommodation_type = State()
    amenities = State()
    searching = State()


async def cmd_cancel(call: types.CallbackQuery, state: FSMContext):
    await analytics.send_analytics(call.from_user.id, call.from_user.language_code, "Searching_Cancel")
    tg_id = call.from_user.id
    await call.message.delete()
    await state.finish()
    action = 4
    language = await lang(tg_id)
    text = await get_text(action, language)
    await call.message.answer(text)


async def rental_period(call: types.CallbackQuery):
    find_stat()
    await call.message.edit_reply_markup()
    await analytics.send_analytics(call.from_user.id, call.from_user.language_code, "Searching_Rental_Period")
    language = await lang(call.from_user.id)
    action = 10
    text = await get_text(action, language)
    await call.bot.edit_message_text(chat_id=call.message.chat.id,
                                     message_id=call.message.message_id,
                                     text=text,
                                     reply_markup=inline.rental_period(language))
    await Searching.rental_period.set()


async def rental_period_2(message: types.Message):
    find_stat()
    await analytics.send_analytics(message.from_user.id, message.from_user.language_code, "Searching_Rental_Period")
    language = await lang(message.from_user.id)
    action = 10
    text = await get_text(action, language)
    await message.answer(text, reply_markup=inline.rental_period(language))
    await Searching.rental_period.set()


async def currency(call: types.CallbackQuery, state: FSMContext):
    if call.data == 'back':
        await state.reset_state()
        await call.message.delete()
        await state.update_data({'selected_options': []})
        name = call.from_user.first_name
        language = await lang(call.from_user.id)
        action = 1
        text = await get_text(action, language)
        await call.message.answer(text=f'{name}, {text}', reply_markup=inline.get_started(language))
    else:
        await analytics.send_analytics(call.from_user.id, call.from_user.language_code, "Searching_Currency")
        async with state.proxy() as data:
            data['rental_period'] = call.data
        language = await lang(call.from_user.id)
        action = 11
        text = await get_text(action, language)
        await call.bot.edit_message_text(chat_id=call.message.chat.id,
                                         message_id=call.message.message_id,
                                         text=text,
                                         reply_markup=inline.currency(language))
        await Searching.next()


async def budget(call: types.CallbackQuery, state: FSMContext):
    if call.data == 'back':
        await state.reset_state()
        await call.message.edit_reply_markup()
        await state.update_data({'selected_options': []})
        language = await lang(call.from_user.id)
        action = 10
        text = await get_text(action, language)
        await call.bot.edit_message_text(chat_id=call.message.chat.id,
                                         message_id=call.message.message_id,
                                         text=text,
                                         reply_markup=inline.rental_period(language))
        await Searching.rental_period.set()
    else:
        language = await lang(call.from_user.id)
        async with state.proxy() as data:
            data['currency'] = call.data
        rent = data.get('rental_period')
        print(rent)
        keyboard = inline.show_budget_options(call, rent, language)
        await Searching.next()
        action = 12
        text = await get_text(action, language)
        await analytics.send_analytics(call.from_user.id, call.from_user.language_code, "Searching_Budget")
        await call.bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=text,
            reply_markup=keyboard)


async def budget_handler(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    selected_option = call.data.replace("select_option:", "")
    message_id = call.message.message_id
    inline_message_id = call.inline_message_id
    keyboard = call.message.reply_markup
    for row in keyboard.inline_keyboard:
        for button in row:
            if button.callback_data == call.data:
                if "✅" not in button.text:
                    button.text = f"{selected_option} ✅"
                    async with state.proxy() as data:
                        selected_options = data.get('selected_options', [])
                        selected_options.append(selected_option)
                        await state.update_data(selected_options=selected_options)
                elif "✅" in button.text:
                    button.text = selected_option
                    async with state.proxy() as data:
                        selected_options = data.get('selected_options', [])
                        selected_options.remove(selected_option)
                        await state.update_data(selected_options=selected_options)
    done_button_added = False
    for row in keyboard.inline_keyboard:
        for button in row:
            if button.callback_data == "done":
                done_button_added = True
    if not done_button_added:
        done_button = InlineKeyboardButton("Next", callback_data="done")
        keyboard.add(done_button)
    if selected_option not in call.message.text:
        await call.bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=message_id,
                                                 inline_message_id=inline_message_id, reply_markup=keyboard)
    else:
        await call.bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=message_id,
                                                 inline_message_id=inline_message_id, reply_markup=keyboard)


async def budget_done_handler(call: types.CallbackQuery, state: FSMContext):
    state_data = await state.get_data()

    if call.data == 'back':
        await state.set_state(Searching.rental_period.state)
        language = await lang(call.from_user.id)
        action = 11
        text = await get_text(action, language)
        await state.update_data({'selected_options': []})
        await call.bot.edit_message_text(chat_id=call.message.chat.id,
                                         message_id=call.message.message_id,
                                         text=text,
                                         reply_markup=inline.currency(language))
        await Searching.next()
    else:
        async with state.proxy() as data:
            selected_options = data.get('selected_options', [])
            await state.update_data(selected_options=selected_options)
            await state.update_data({'selected_options': []})
            async with state.proxy() as data:
                data['budget'] = selected_options
            language = await lang(call.from_user.id)
            action = 13
            text = await get_text(action, language)
            await call.bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=text,
                reply_markup=inline.show_location_options(language))
            await Searching.next()


async def location_handler(call: types.CallbackQuery, state: FSMContext):
    await analytics.send_analytics(call.from_user.id, call.from_user.language_code, "Searching_Location")
    await call.answer()
    selected_option = call.data.replace("select_option:", "")
    message_id = call.message.message_id
    inline_message_id = call.inline_message_id
    keyboard = call.message.reply_markup
    for row in keyboard.inline_keyboard:
        for button in row:
            if button.callback_data == call.data:
                if "✅" not in button.text:
                    button.text = f"{selected_option} ✅"
                    async with state.proxy() as data:
                        selected_options = data.get('selected_options', [])
                        selected_options.append(selected_option)
                        await state.update_data(selected_options=selected_options)
                elif "✅" in button.text:
                    button.text = selected_option
                    async with state.proxy() as data:
                        selected_options = data.get('selected_options', [])
                        selected_options.remove(selected_option)
                        await state.update_data(selected_options=selected_options)
    done_button_added = False
    for row in keyboard.inline_keyboard:
        for button in row:
            if button.callback_data == "done":
                done_button_added = True
    if not done_button_added:
        done_button = InlineKeyboardButton("Next", callback_data="done")
        keyboard.add(done_button)
    if selected_option not in call.message.text:
        await call.bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=message_id,
                                                 inline_message_id=inline_message_id, reply_markup=keyboard)
    else:
        await call.bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=message_id,
                                                 inline_message_id=inline_message_id, reply_markup=keyboard)


async def location_done_handler(call: types.CallbackQuery, state: FSMContext):
    state_data = await state.get_data()

    async with state.proxy() as data:
        currency_data = data['currency']

    if call.data == 'back':
        await state.update_data({'selected_options': []})
        await state.set_state(Searching.currency.state)
        await Searching.next()
        language = await lang(call.from_user.id)
        action = 12
        text = await get_text(action, language)
        rent = data.get('rental_period')
        await call.bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=text,
            reply_markup=inline.show_budget_options_state(currency_data, rent, language))
    else:
        async with state.proxy() as data:
            selected_options = data.get('selected_options', [])
            if selected_options:
                await state.update_data(selected_options=selected_options)
                await state.update_data({'selected_options': []})
                async with state.proxy() as data:
                    data['location'] = selected_options
                language = await lang(call.from_user.id)
                action = 14
                text = await get_text(action, language)
                await call.bot.edit_message_text(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    text=text,
                    reply_markup=inline.show_accommodation_type_options(language))
                await Searching.next()
            else:
                language = await lang(call.from_user.id)
                action = 15
                text = await get_text(action, language)
                await call.answer(text=text, show_alert=True)


async def accommodation_type_handler(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    await analytics.send_analytics(call.from_user.id, call.from_user.language_code, "Searching_Type")
    selected_option = call.data.replace("select_option:", "")
    message_id = call.message.message_id
    inline_message_id = call.inline_message_id
    keyboard = call.message.reply_markup
    for row in keyboard.inline_keyboard:
        for button in row:
            if button.callback_data == call.data:
                if "✅" not in button.text:
                    button.text = f"{selected_option} ✅"
                    async with state.proxy() as data:
                        selected_options = data.get('selected_options', [])
                        selected_options.append(selected_option)
                        await state.update_data(selected_options=selected_options)
                elif "✅" in button.text:
                    button.text = selected_option
                    async with state.proxy() as data:
                        selected_options = data.get('selected_options', [])
                        selected_options.remove(selected_option)
                        await state.update_data(selected_options=selected_options)
    done_button_added = False
    for row in keyboard.inline_keyboard:
        for button in row:
            if button.callback_data == "done":
                done_button_added = True
    if not done_button_added:
        done_button = InlineKeyboardButton("Next", callback_data="done")
        keyboard.add(done_button)
    if selected_option not in call.message.text:
        await call.bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=message_id,
                                                 inline_message_id=inline_message_id, reply_markup=keyboard)
    else:
        await call.bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=message_id,
                                                 inline_message_id=inline_message_id, reply_markup=keyboard)


async def accommodation_type_done_handler(call: types.CallbackQuery, state: FSMContext):
    state_data = await state.get_data()
    if call.data == 'back':
        await state.set_state(Searching.budget.state)
        await state.update_data({'selected_options': []})
        language = await lang(call.from_user.id)
        action = 13
        text = await get_text(action, language)
        await call.bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=text,
            reply_markup=inline.show_location_options(language))
        await Searching.next()
    else:
        async with state.proxy() as data:
            selected_options = data.get('selected_options', [])
            await state.update_data(selected_options=selected_options)
            await state.update_data({'selected_options': []})
            async with state.proxy() as data:
                data['accommodation_type'] = selected_options
            language = await lang(call.from_user.id)
            action = 16
            text = await get_text(action, language)
            await call.bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=text,
                reply_markup=inline.show_amenities_options(language))
            await Searching.next()


async def amenities_handler(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    await analytics.send_analytics(call.from_user.id, call.from_user.language_code, "Searching_Amenities")
    selected_option = call.data.replace("select_option:", "")
    message_id = call.message.message_id
    inline_message_id = call.inline_message_id
    keyboard = call.message.reply_markup
    for row in keyboard.inline_keyboard:
        for button in row:
            if button.callback_data == call.data:
                if "✅" not in button.text:
                    button.text = f"{selected_option} ✅"
                    async with state.proxy() as data:
                        selected_options = data.get('selected_options', [])
                        selected_options.append(selected_option)
                        await state.update_data(selected_options=selected_options)
                elif "✅" in button.text:
                    button.text = selected_option
                    async with state.proxy() as data:
                        selected_options = data.get('selected_options', [])
                        selected_options.remove(selected_option)
                        await state.update_data(selected_options=selected_options)
    done_button_added = False
    for row in keyboard.inline_keyboard:
        for button in row:
            if button.callback_data == "done":
                done_button_added = True
    if not done_button_added:
        done_button = InlineKeyboardButton("Next", callback_data="done")
        keyboard.add(done_button)
    if selected_option not in call.message.text:
        await call.bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=message_id,
                                                 inline_message_id=inline_message_id, reply_markup=keyboard)
    else:
        await call.bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=message_id,
                                                 inline_message_id=inline_message_id, reply_markup=keyboard)


async def amenities_done_handler(call: types.CallbackQuery, state: FSMContext):
    state_data = await state.get_data()
    if call.data == 'back':
        await state.set_state(Searching.location.state)
        await state.update_data({'selected_options': []})
        language = await lang(call.from_user.id)
        action = 14
        text = await get_text(action, language)
        await call.bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=text,
            reply_markup=inline.show_accommodation_type_options(language))
        await Searching.next()
    else:
        async with state.proxy() as data:
            selected_options = data.get('selected_options', [])
            await state.update_data(selected_options=selected_options)
            await state.update_data({'selected_options': []})
            async with state.proxy() as data:
                data['amenities'] = selected_options
            budget_str = ", ".join(data.get('budget'))
            location_str = ", ".join(data.get('location'))
            accommodation_type_str = ", ".join(data.get('accommodation_type'))
            amenities_str = ", ".join(data.get('amenities'))
            if not budget_str:
                budget_str = budget_str.replace("", "Whatever")
            if not accommodation_type_str:
                accommodation_type_str = accommodation_type_str.replace("", "Whatever")
            if not amenities_str:
                amenities_str = amenities_str.replace("", "Whatever")
            language = await lang(call.from_user.id)

            if language in ['EN', 'IN']:
                await call.bot.edit_message_text(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    text=f"Please, check your request:\n\n"
                         f"<b>Rental period:</b> <em>{data.get('rental_period')}</em>\n"
                         f"<b>Budget:</b> <em>{budget_str}</em>\n"
                         f"<b>Locations:</b> <em>{location_str}</em>\n"
                         f"<b>Accommodation types:</b> <em>{accommodation_type_str}</em>\n"
                         f"<b>Amenities:</b> <em>{amenities_str}</em>\n",
                    reply_markup=inline.searching(language))
            if language == 'RU':
                await call.bot.edit_message_text(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    text=f"Пожалуйста, проверьте ваш запрос:\n\n"
                         f"<b>Период:</b> <em>{data.get('rental_period')}</em>\n"
                         f"<b>Бюджет:</b> <em>{budget_str}</em>\n"
                         f"<b>Локация:</b> <em>{location_str}</em>\n"
                         f"<b>Тип недвижимости:</b> <em>{accommodation_type_str}</em>\n"
                         f"<b>Удобства:</b> <em>{amenities_str}</em>\n",
                    reply_markup=inline.searching(language))
            await Searching.next()


def format_number(num: float):
    locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
    if num >= 10 ** 9:
        result = f"{locale.format_string('%.1f', num / 10 ** 9, grouping=True).rstrip('0').rstrip('.')} billion rupiah"
        return result.replace(', ', ' ')
    elif num >= 10 ** 6:
        result = f"{locale.format_string('%.1f', num / 10 ** 6, grouping=True).rstrip('0').rstrip('.')} million rupiah"
        return result.replace(', ', ' ')
    elif num >= 10 ** 3:
        result = f"{locale.format_string('%.1f', num / 10 ** 3, grouping=True).rstrip('0').rstrip('.')} thousand rupiah"
        return result.replace(', ', ' ')
    else:
        result = f"{locale.format_string('%.0f', num, grouping=True)} rupiah"
        return result.replace(', ', ' ')


async def searching_finish(call: types.CallbackQuery, state: FSMContext):
    if call.data == 'back':
        await state.set_state(Searching.accommodation_type.state)
        await state.update_data({'selected_options': []})
        language = await lang(call.from_user.id)
        action = 16
        text = await get_text(action, language)
        await call.bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=text,
            reply_markup=inline.show_amenities_options(language))
        await Searching.next()
    else:
        state_data = await state.get_data()
        async with state.proxy() as data:
            rental_period_str = data.get('rental_period')
            currency_str = data.get('currency')
            budget_str = ", ".join(data.get('budget'))
            location_str = ", ".join(data.get('location'))
            accommodation_type_str = ", ".join(data.get('accommodation_type'))
            amenities_str = ", ".join(data.get('amenities'))
        if call.data == 'get_started':
            await state.finish()
            await rental_period(call)
        elif call.data == 'save':
            await analytics.send_analytics(call.from_user.id, call.from_user.language_code, "Searching_Save_Request")
            language = await lang(call.from_user.id)
            await call.message.edit_reply_markup(reply_markup=inline.searching_2(language))
            await save_request(call.from_user.id, rental_period_str, currency_str, budget_str,
                               location_str, accommodation_type_str, amenities_str)

            action = 17
            text = await get_text(action, language)
            await call.answer(text=text,
                              show_alert=True)
        elif call.data == 'searching':
            await analytics.send_analytics(call.from_user.id, call.from_user.language_code, "Searching_Searching")
            search_stat()
            language = await lang(call.from_user.id)
            action = 18
            text = await get_text(action, language)
            await call.bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=text)
            await asyncio.sleep(3)
            await call.message.delete()
            await state.finish()
            aps = get_apart(rental_period_str, currency_str, budget_str,
                            location_str, accommodation_type_str, amenities_str)
            if not aps:
                language = await lang(call.from_user.id)
                text = await get_text(3, language)
                await call.message.answer(text=text)
            for ap in aps:
                ap_type = ''
                if ap[5] == 'VI':
                    ap_type = 'Villa Entirely'
                if ap[5] == 'RO':
                    ap_type = 'Room in shared villa'
                if ap[5] == 'AP':
                    ap_type = 'Apartment'
                if ap[5] == 'GH':
                    ap_type = 'Guesthouse'
                location_id = ap[13]
                location = get_location_name(location_id)[0]
                image = get_image(ap[1])
                #photo_files = [os.path.join('/projects/Django/BaliAdmin', f) for f in image]
                #media = []
                #with open(photo_files[0], "rb") as f:
                    #photo = types.InputFile(io.BytesIO(f.read()), filename=photo_files[0])
                    # caption = f'<b>Type:</b> {ap_type}\n' \
                    #           f'<b>Location</b>: {location}\n' \
                    #           f'<b>Amenities:</b> {ap[7]}\n' \
                    #           f'<b>Rent period:</b> {ap[8]}\n' \
                    #           f'<b>Price Rupee:</b> {format_number(ap[9])}\n' \
                    #           f'<b>Price USD:</b> {ap[10]}\n' \
                    #           f'<b>Description:</b> {ap[11]}'
                #     media.append(types.InputMediaPhoto(media=photo, caption=caption))
                # for file in photo_files[1:]:
                #     with open(file, "rb") as f:
                #         photo = types.InputFile(io.BytesIO(f.read()), filename=file)
                #         media.append(types.InputMediaPhoto(media=photo, caption=caption))
                # text_message = await call.bot.send_media_group(chat_id=call.message.chat.id,
                #                                                media=media)
                language = await lang(call.from_user.id)
                apartment_views_amount(int(ap[1]))
                if language in ['EN', 'IN']:
                    await call.bot.send_message(chat_id=call.message.chat.id,
                                                text=f'<b>Unique ID:</b> {ap[1]}\n'
                                                     f'<b>Type:</b> {ap_type}\n'
                                                     f'<b>Location</b>: {location}\n'
                                                     f'<b>Amenities:</b> {ap[7]}\n'
                                                     f'<b>Rent period:</b> {ap[8]}\n'
                                                     f'<b>Price Rupee:</b> {format_number(ap[9])}\n'
                                                     f'<b>Price USD:</b> {ap[10]}$\n'
                                                     f'<b>Description:</b> {ap[11]}',
                                                reply_to_message_id=text_message[0].message_id,
                                                reply_markup=inline.apartment_contacts(str(ap[1]), language))
                elif language == 'RU':
                    await call.bot.send_message(chat_id=call.message.chat.id,
                                                text=f'<b>Уникальный ID:</b> {ap[1]}\n'
                                                     f'<b>Тип недвижимости:</b> {ap_type}\n'
                                                     f'<b>Локация</b>: {location}\n'
                                                     f'<b>Удобства:</b> {ap[7]}\n'
                                                     f'<b>Период:</b> {ap[8]}\n'
                                                     f'<b>Цена в рупиях:</b> {format_number(ap[9])}\n'
                                                     f'<b>Цена в долларах:</b> {ap[10]}$\n'
                                                     f'<b>Описание:</b> {ap[11]}',
                                                reply_to_message_id=text_message[0].message_id,
                                                reply_markup=inline.apartment_contacts(str(ap[1]), language))


def register(dp: Dispatcher):
    dp.register_callback_query_handler(rental_period, lambda c: c.data == "get_started")
    dp.register_message_handler(rental_period_2, commands="find", state="*")
    dp.register_callback_query_handler(cmd_cancel, text='cancel', state='*')
    dp.register_callback_query_handler(currency, lambda c: c.data in ('DAY', 'MONTH', 'YEAR', 'back'),
                                       state=Searching.rental_period)
    dp.register_callback_query_handler(budget, lambda c: c.data in ('usd', 'rupiah', 'back'),
                                       state=Searching.currency)
    dp.register_callback_query_handler(budget_handler, lambda c: c.data.startswith("select_option"),
                                       state=Searching.budget)
    dp.register_callback_query_handler(budget_done_handler, lambda c: c.data in ("done", 'back'),
                                       state=Searching.budget)
    dp.register_callback_query_handler(location_handler, lambda c: c.data.startswith("select_option"),
                                       state=Searching.location)
    dp.register_callback_query_handler(location_done_handler, lambda c: c.data in ("done", 'back'),
                                       state=Searching.location)
    dp.register_callback_query_handler(accommodation_type_handler, lambda c: c.data.startswith("select_option"),
                                       state=Searching.accommodation_type)
    dp.register_callback_query_handler(accommodation_type_done_handler, lambda c: c.data in ("done", 'back'),
                                       state=Searching.accommodation_type)
    dp.register_callback_query_handler(amenities_handler, lambda c: c.data.startswith("select_option"),
                                       state=Searching.amenities)
    dp.register_callback_query_handler(amenities_done_handler, lambda c: c.data in ("done", 'back'),
                                       state=Searching.amenities)
    dp.register_callback_query_handler(searching_finish, state=Searching.searching)
