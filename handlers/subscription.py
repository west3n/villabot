from aiogram import Dispatcher, types

from database.postgre import db, cur
from database.postgre_find import get_last_id
from database.postgre_user import status, lang, check_subscribe_status, subscribe_activity
from database.postgre_statistic import command_contact_stat, command_payment_stat
from psycopg2.errors import UniqueViolation, InFailedSqlTransaction
from keyboards import inline
from texts.text import get_text


async def apartment_contacts(call: types.CallbackQuery):
    command_contact_stat()
    tg_id = call.from_user.id
    subscription_status = await check_subscribe_status(tg_id)
    language = await lang(call.from_user.id)
    if subscription_status[0]:
        unique_id = int(call.data.split("_")[1])
        cur.execute(f"SELECT agent_name, agent_whats_up FROM appart_apartment WHERE id=%s", (unique_id,))
        contact = cur.fetchone()
        if language in ["EN", "IN"]:
            await call.message.reply(
                f"<b>Agent name:</b> {contact[0]}\n"
                f"<b>Link to WhatsApp:</b> {contact[1]}"
            )
        elif language == "RU":
            await call.message.reply(
                f"<b>Имя агента:</b> {contact[0]}\n"
                f"<b>Ссылка в WhatsApp:</b> {contact[1]}"
            )
    else:
        text = await get_text(19, language)
        await call.message.reply(text,
                                 reply_markup=inline.subscribe(language))


async def apartment_contacts_favorites(call: types.CallbackQuery):
    command_contact_stat()
    await call.message.edit_reply_markup()
    tg_id = call.from_user.id
    subscription_status = await check_subscribe_status(tg_id)
    language = await lang(call.from_user.id)
    if subscription_status[0]:
        unique_id = int(call.data.split("_")[2])
        cur.execute(f"SELECT agent_name, agent_whats_up FROM appart_apartment WHERE id=%s", (unique_id,))
        contact = cur.fetchone()
        if language in ["EN", "IN"]:
            await call.message.reply(
                f"<b>Agent name:</b> {contact[0]}\n"
                f"<b>Link to WhatsApp:</b> {contact[1]}"
            )
        elif language == "RU":
            await call.message.reply(
                f"<b>Имя агента:</b> {contact[0]}\n"
                f"<b>Ссылка в WhatsApp:</b> {contact[1]}"
            )
    else:
        text = await get_text(19, language)
        await call.message.reply(text=text,
                                 reply_markup=inline.subscribe(language))


async def save_to_favorites(call: types.CallbackQuery):
    unique_id = call.data
    id_data = int(unique_id.split("_")[1])
    language = await lang(call.from_user.id)
    await call.message.edit_reply_markup(reply_markup=inline.contacts(str(id_data), language))
    tg_id = call.from_user.id
    try:
        user_id = await status(tg_id)
        cur.execute("INSERT INTO appart_saveaps (apart_id, user_id) VALUES (%s, %s)", (id_data, user_id,))
        db.commit()
        text = await get_text(20, language)
        await call.answer(text)
    except UniqueViolation:
        db.rollback()
        text = await get_text(21, language)
        await call.answer(text=text)
    except InFailedSqlTransaction:
        db.rollback()
        text = await get_text(21, language)
        await call.answer(text=text)


async def turn_on_subscription(call: types.CallbackQuery):
    command_payment_stat()
    await call.message.edit_reply_markup()
    tg_id = call.from_user.id
    language = await lang(call.from_user.id)
    text = await get_text(22, language)
    await subscribe_activity(tg_id)
    await call.message.answer(text=text)


def register(dp: Dispatcher):
    try:
        count = get_last_id()
        for n in range(0, int(count) + 1):
            dp.register_callback_query_handler(apartment_contacts, text=f'contact_{n}')
            dp.register_callback_query_handler(apartment_contacts_favorites, text=f'contact_favorites_{n}')
            dp.register_callback_query_handler(save_to_favorites, text=f"save_{n}")
            dp.register_callback_query_handler(turn_on_subscription, text='subscription_on')
    except TypeError as e:
        print(f'Error in register function: {e}')
