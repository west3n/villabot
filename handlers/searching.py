import asyncio
import locale
import os
import io

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import InlineKeyboardButton
from database.postgre_find import get_apart, get_location_name, get_image

from keyboards import inline


class Searching(StatesGroup):
    rental_period = State()
    currency = State()
    budget = State()
    location = State()
    accommodation_type = State()
    amenities = State()
    searching = State()


async def cmd_cancel(call: types.CallbackQuery, state: FSMContext):
    await call.message.delete()
    await state.finish()
    await call.message.answer('Action Canceled!')


async def rental_period(call: types.CallbackQuery):
    await call.message.edit_reply_markup()
    await call.bot.edit_message_text(chat_id=call.message.chat.id,
                                     message_id=call.message.message_id,
                                     text="Please, answer the following questions about your future villa 🏠\n\n"
                                          "Rental period:",
                                     reply_markup=inline.rental_period())
    await Searching.rental_period.set()


async def currency(call: types.CallbackQuery, state: FSMContext):
    if call.data == 'back':
        await state.reset_state()
        await call.message.delete()
        name = call.from_user.first_name
        await call.message.answer(f"Hello, {name}! Happy to see you in VillaBot! 🙌\n"
                                  f"Let's find awesome villa!", reply_markup=inline.get_started())
    else:
        async with state.proxy() as data:
            data['rental_period'] = call.data
        await call.bot.edit_message_text(chat_id=call.message.chat.id,
                                         message_id=call.message.message_id,
                                         text='Choose your currency:',
                                         reply_markup=inline.currency())
        await Searching.next()


async def budget(call: types.CallbackQuery, state: FSMContext):
    state_data = await state.get_data()
    print(state_data)
    if call.data == 'back':
        await state.reset_state()
        await call.message.edit_reply_markup()
        await call.bot.edit_message_text(chat_id=call.message.chat.id,
                                         message_id=call.message.message_id,
                                         text="Please, answer the following questions about your future villa 🏠\n\n"
                                              "Rental period:",
                                         reply_markup=inline.rental_period())
        await Searching.rental_period.set()
    else:
        keyboard = inline.show_budget_options(call)
        async with state.proxy() as data:
            data['currency'] = call.data
        await Searching.next()
        await call.bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text='Choose your budget:\n(You can choose several answers)',
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
    print(state_data)
    if call.data == 'back':
        await state.set_state(Searching.rental_period.state)
        await call.bot.edit_message_text(chat_id=call.message.chat.id,
                                         message_id=call.message.message_id,
                                         text='Choose your currency:',
                                         reply_markup=inline.currency())
        await Searching.next()
    else:
        async with state.proxy() as data:
            selected_options = data.get('selected_options', [])
            await state.update_data(selected_options=selected_options)
            await state.update_data({'selected_options': []})
            async with state.proxy() as data:
                data['budget'] = selected_options
            await call.bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text='Accommodation location:\n(You can choose several answers)',
                reply_markup=inline.show_location_options())
            await Searching.next()


async def location_handler(call: types.CallbackQuery, state: FSMContext):
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
    print(state_data)
    async with state.proxy() as data:
        data['currency'] = call.data
        state_data = await state.get_data()
        currency_data = state_data['currency']
        print(currency_data)
    if call.data == 'back':
        await state.set_state(Searching.currency.state)
        await Searching.next()
        await call.bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text='Choose your budget:\n(You can choose several answers)',
            reply_markup=inline.show_budget_options_state(currency_data))
    else:
        async with state.proxy() as data:
            selected_options = data.get('selected_options', [])
            if selected_options:
                await state.update_data(selected_options=selected_options)
                await state.update_data({'selected_options': []})
                async with state.proxy() as data:
                    data['location'] = selected_options
                await call.bot.edit_message_text(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    text="Accommodation type:\n(You can choose several answers)",
                    reply_markup=inline.show_accommodation_type_options())
                await Searching.next()
            else:
                await call.answer(text="No location selected", show_alert=True)


async def accommodation_type_handler(call: types.CallbackQuery, state: FSMContext):
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


async def accommodation_type_done_handler(call: types.CallbackQuery, state: FSMContext):
    state_data = await state.get_data()
    print(state_data)
    if call.data == 'back':
        await state.set_state(Searching.budget.state)
        async with state.proxy() as data:
            selected_options = data.get('selected_options', [])
            await state.update_data(selected_options=selected_options)
            await state.update_data({'selected_options': []})
            async with state.proxy() as data:
                data['location'] = selected_options
            await call.bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text="Accommodation type:\n(You can choose several answers)",
                reply_markup=inline.show_accommodation_type_options())
            await Searching.next()
    else:
        async with state.proxy() as data:
            selected_options = data.get('selected_options', [])
            await state.update_data(selected_options=selected_options)
            await state.update_data({'selected_options': []})
            async with state.proxy() as data:
                data['accommodation_type'] = selected_options
            await call.bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text="Additional requests:\n(You can choose several answers)",
                reply_markup=inline.show_amenities_options())
            await Searching.next()


async def amenities_handler(call: types.CallbackQuery, state: FSMContext):
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


async def amenities_done_handler(call: types.CallbackQuery, state: FSMContext):
    state_data = await state.get_data()
    print(state_data)
    if call.data == 'back':
        await state.set_state(Searching.location.state)
        async with state.proxy() as data:
            selected_options = data.get('selected_options', [])
            await state.update_data(selected_options=selected_options)
            await state.update_data({'selected_options': []})
            async with state.proxy() as data:
                data['accommodation_type'] = selected_options
            await call.bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text="Additional requests:\n(You can choose several answers)",
                reply_markup=inline.show_amenities_options())
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
            await call.bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=f"Please, check your request:\n\n"
                     f"<b>Rental period:</b> <em>{data.get('rental_period')}</em>\n"
                     f"<b>Budget:</b> <em>{budget_str}</em>\n"
                     f"<b>Locations:</b> <em>{location_str}</em>\n"
                     f"<b>Accommodation type:</b> <em>{accommodation_type_str}</em>\n"
                     f"<b>Amenities:</b> <em>{amenities_str}</em>\n",
                reply_markup=inline.searching())
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
    state_data = await state.get_data()
    print(state_data)
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
    elif call.data == 'searching':
        await call.bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text='Searching...')
        await asyncio.sleep(3)
        await call.message.delete()
        await state.finish()
        aps = get_apart(rental_period_str, currency_str, budget_str,
                        location_str, accommodation_type_str, amenities_str)
        if not aps:
            await call.message.answer(text='Nothing found.')
        for ap in aps:
            ap_type = ''
            if ap[4] == 'VI':
                ap_type = 'Villa Entirely'
            if ap[4] == 'RO':
                ap_type = 'Room in shared villa'
            if ap[4] == 'AP':
                ap_type = 'Apartment'
            if ap[4] == 'GH':
                ap_type = 'Guesthouse'
            location_id = ap[11]
            location = get_location_name(location_id)[0]
            image = get_image(ap[0])
            photo_files = [os.path.join('/Users/caramba/PycharmProject/BaliAdmin', f) for f in image]
            media = []
            with open(photo_files[0], "rb") as f:
                photo = types.InputFile(io.BytesIO(f.read()), filename=photo_files[0])
                caption = f'<b>Type:</b> {ap_type}\n' \
                          f'<b>Location</b>: {location}\n' \
                          f'<b>Amenities:</b> {ap[6]}\n' \
                          f'<b>Rent period:</b> {ap[7]}\n' \
                          f'<b>Price Rupee:</b> {ap[8]}\n' \
                          f'<b>Price USD:</b> {ap[9]}\n' \
                          f'<b>Description:</b> {ap[10]}'
                media.append(types.InputMediaPhoto(media=photo, caption=caption))
            for file in photo_files[1:]:
                with open(file, "rb") as f:
                    photo = types.InputFile(io.BytesIO(f.read()), filename=file)
                    media.append(types.InputMediaPhoto(media=photo, caption=caption))
            text_message = await call.bot.send_media_group(chat_id=call.message.chat.id,
                                                           media=media)
            await call.bot.send_message(chat_id=call.message.chat.id,
                                        text=f'<b>Type:</b> {ap_type}\n' 
                                             f'<b>Location</b>: {location}\n' 
                                             f'<b>Amenities:</b> {ap[6]}\n' 
                                             f'<b>Rent period:</b> {ap[7]}\n' 
                                             f'<b>Price Rupee:</b> {format_number(ap[8])}\n'
                                             f'<b>Price USD:</b> {ap[9]}$\n' 
                                             f'<b>Description:</b> {ap[10]}',
                                        reply_to_message_id=text_message[0].message_id,
                                        reply_markup=inline.apartment_contacts(str(ap[0])))


def register(dp: Dispatcher):
    dp.register_callback_query_handler(rental_period, lambda c: c.data == "get_started")
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
