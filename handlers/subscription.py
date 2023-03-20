from aiogram import Dispatcher, types

import database.postgre_user
from database.postgre import db, cur
from database.postgre_user import status
from psycopg2.errors import UniqueViolation, InFailedSqlTransaction
from keyboards import inline


async def apartment_contacts(call: types.CallbackQuery):
    tg_id = call.from_user.id
    subscription_status = await database.postgre_user.check_subscribe_status(tg_id)
    if subscription_status[0]:
        unique_id = int(call.data.split("_")[1])
        cur.execute(f"SELECT agent_name, agent_whats_up FROM appart_apartment WHERE id=%s", (unique_id,))
        contact = cur.fetchone()
        await call.message.answer(
            f"<b>Unique ID:</b> {unique_id}\n"
            f"<b>Agent name:</b> {contact[0]}\n"
            f"<b>Link to WhatsApp:</b> {contact[1]}"
        )
    else:
        await call.message.answer("Do you like this variant? If you want to contact the renter please turn on "
                                  "the subscription for our service for one month",
                                  reply_markup=inline.subscribe())


async def save_to_favorites(call: types.CallbackQuery):
    unique_id = call.data
    id_data = int(unique_id.split("_")[1])
    await call.message.edit_reply_markup(reply_markup=inline.contacts(str(id_data)))
    tg_id = call.from_user.id
    try:
        user_id = await status(tg_id)
        cur.execute("INSERT INTO appart_saveaps (apart_id, user_id) VALUES (%s, %s)", (id_data, user_id,))
        db.commit()
        await call.answer(f"Apartment saved to favorite!")
    except UniqueViolation:
        db.rollback()
        await call.answer(f"Apartment already in your favorites!")
    except InFailedSqlTransaction:
        db.rollback()
        await call.answer(f"Apartment already in your favorites!")


async def turn_on_subscription(call: types.CallbackQuery):
    await call.message.edit_reply_markup()
    tg_id = call.from_user.id
    await database.postgre_user.subscribe_activity(tg_id)
    await call.message.answer("Subscription activated!")


def register(dp: Dispatcher):
    try:
        cur.execute("SELECT id FROM appart_apartment")
        count = cur.fetchone()[0]
        for n in range(0, int(count) + 10):
            dp.register_callback_query_handler(apartment_contacts, text=f'contact_{n}')
            dp.register_callback_query_handler(save_to_favorites, text=f"save_{n}")
            dp.register_callback_query_handler(turn_on_subscription, text='subscription_on')
    except TypeError as e:
        print(f'Error in register function: {e}')
