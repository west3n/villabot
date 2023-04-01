import os
import io

from aiogram import Dispatcher, types
from database.postge_favorite import get_favorite
from database.postgre_find import get_image, get_location_name
from handlers.searching import format_number
from keyboards.inline import contacts_favorites
from database.postgre_user import lang
from texts.text import get_text


async def show_favorite(call: types.CallbackQuery):
    await call.message.delete()
    tg_id = call.from_user.id
    action = 2
    language = await lang(tg_id)
    text = await get_text(action, language)
    await call.message.answer(text=text)
    tg_id = call.from_user.id
    aps = await get_favorite(tg_id)
    if aps is not None:
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
            location_id = ap[12]
            location = get_location_name(location_id)[0]
            image = get_image(ap[1])
            photo_files = [os.path.join('/Users/caramba/PycharmProject/BaliAdmin', f) for f in image]
            media = []
            with open(photo_files[0], "rb") as f:
                photo = types.InputFile(io.BytesIO(f.read()), filename=photo_files[0])
                caption = f'<b>Type:</b> {ap_type}\n' \
                          f'<b>Location</b>: {location}\n' \
                          f'<b>Amenities:</b> {ap[7]}\n' \
                          f'<b>Rent period:</b> {ap[8]}\n' \
                          f'<b>Price Rupee:</b> {ap[9]}\n' \
                          f'<b>Price USD:</b> {ap[10]}\n' \
                          f'<b>Description:</b> {ap[11]}'
                media.append(types.InputMediaPhoto(media=photo, caption=caption))
            for file in photo_files[1:]:
                with open(file, "rb") as f:
                    photo = types.InputFile(io.BytesIO(f.read()), filename=file)
                    media.append(types.InputMediaPhoto(media=photo, caption=caption))
            text_message = await call.bot.send_media_group(chat_id=call.message.chat.id,
                                                           media=media)
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
                                            reply_markup=contacts_favorites(str(ap[1]), language))
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
                                            reply_markup=contacts_favorites(str(ap[1]), language))

    if not aps:
        action = 3
        language = await lang(tg_id)
        text = await get_text(action, language)
        await call.message.answer(text=text)


def register(dp: Dispatcher):
    dp.register_callback_query_handler(show_favorite, text='show_favorite')
