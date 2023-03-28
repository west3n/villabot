import asyncio
import io
import os

from aiogram import Dispatcher, types
from database.postgre_find import get_request, get_apart, get_location_name, get_image
from handlers.searching import format_number
from keyboards import inline
from database.postgre_user import lang
from texts.text import get_text
from database.postgre_statistic import apartment_views_amount


async def get_request_(call: types.CallbackQuery):
    await call.message.delete()
    tg_id = call.from_user.id
    request = await get_request(tg_id)
    rental_period = request.split("/")[0]
    budget = request.split("/")[2]
    locations = request.split("/")[3]
    accommodation_types = request.split("/")[4]
    amenities = request.split("/")[5]
    language = await lang(tg_id)

    if not budget:
        budget = budget.replace("", "Whatever")
    if not accommodation_types:
        accommodation_types = accommodation_types.replace("", "Whatever")
    if not amenities:
        amenities = amenities.replace("", "Whatever")
    if language == "RU":
        await call.message.answer(f"Ваш последний запрос:\n\n"
                                  f"<b>Период:</b> <em>{rental_period}</em>\n"
                                  f"<b>Бюджет:</b> <em>{budget}</em>\n"
                                  f"<b>Локация:</b> <em>{locations}</em>\n"
                                  f"<b>Тип недвижимости:</b> <em>{accommodation_types}</em>\n"
                                  f"<b>Удобства:</b> <em>{amenities}</em>\n",
                                  reply_markup=inline.request(language))
    elif language == 'EN':
        await call.message.answer(f"You last request:\n\n"
                                  f"<b>Rental period:</b> <em>{rental_period}</em>\n"
                                  f"<b>Budget:</b> <em>{budget}</em>\n"
                                  f"<b>Locations:</b> <em>{locations}</em>\n"
                                  f"<b>Accommodation types:</b> <em>{accommodation_types}</em>\n"
                                  f"<b>Amenities:</b> <em>{amenities}</em>\n",
                                  reply_markup=inline.request(language))


async def request_searching(call: types.CallbackQuery):
    language = await lang(call.from_user.id)
    text = 'Researching...'
    if language == 'RU':
        text = 'Повторный поиск...'
    await call.bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=text)
    await asyncio.sleep(3)
    await call.message.delete()
    tg_id = call.from_user.id
    request = await get_request(tg_id)
    aps = get_apart(request.split("/")[0], request.split("/")[1], request.split("/")[2],
                    request.split("/")[3], request.split("/")[4], request.split("/")[5])
    if not aps:
        action = 3
        text = await get_text(action, language)
        await call.message.answer(text=text)
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
        apartment_views_amount(int(ap[0]))
        if language in ['EN', 'IN']:
            await call.bot.send_message(chat_id=call.message.chat.id,
                                        text=f'<b>Unique ID:</b> {ap[0]}\n'
                                             f'<b>Type:</b> {ap_type}\n'
                                             f'<b>Location</b>: {location}\n'
                                             f'<b>Amenities:</b> {ap[6]}\n'
                                             f'<b>Rent period:</b> {ap[7]}\n'
                                             f'<b>Price Rupee:</b> {format_number(ap[8])}\n'
                                             f'<b>Price USD:</b> {ap[9]}$\n'
                                             f'<b>Description:</b> {ap[10]}',
                                        reply_to_message_id=text_message[0].message_id,
                                        reply_markup=inline.apartment_contacts(str(ap[0]), language))
        elif language == 'RU':
            await call.bot.send_message(chat_id=call.message.chat.id,
                                        text=f'<b>Уникальный ID:</b> {ap[0]}\n'
                                             f'<b>Тип недвижимости:</b> {ap_type}\n'
                                             f'<b>Локация</b>: {location}\n'
                                             f'<b>Удобства:</b> {ap[6]}\n'
                                             f'<b>Период:</b> {ap[7]}\n'
                                             f'<b>Цена в рупиях:</b> {format_number(ap[8])}\n'
                                             f'<b>Цена в долларах:</b> {ap[9]}$\n'
                                             f'<b>Описание:</b> {ap[10]}',
                                        reply_to_message_id=text_message[0].message_id,
                                        reply_markup=inline.apartment_contacts(str(ap[0]), language))


def register(dp: Dispatcher):
    dp.register_callback_query_handler(get_request_, text='last_request')
    dp.register_callback_query_handler(request_searching, text='request_searching')
