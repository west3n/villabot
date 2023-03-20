import os
import io

from aiogram import Dispatcher, types
from database.postge_favorite import get_favorite
from database.postgre_find import get_image, get_location_name
from handlers.searching import format_number
from keyboards.inline import contacts_favorites


async def show_favorite(call: types.CallbackQuery):
    await call.message.delete()
    await call.message.answer("Your favorite apartments:")
    tg_id = call.from_user.id
    aps = await get_favorite(tg_id)
    if aps is not None:
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
                                        reply_markup=contacts_favorites(str(ap[0])))

    if not aps:
        await call.message.answer(text='Nothing found.')


def register(dp: Dispatcher):
    dp.register_callback_query_handler(show_favorite, text='show_favorite')
