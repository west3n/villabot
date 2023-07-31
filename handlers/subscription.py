from aiogram import Dispatcher, types
from aiogram.types import ContentTypes
from decouple import config
from database.postgre import connect
from database.postgre_find import get_last_id
from database.postgre_user import status, lang, check_subscribe_status, subscribe_activity
from database.postgre_statistic import contact_stat, subscribe_stat, apartment_favorites_amount, apartment_contacts_amount
from psycopg2.errors import UniqueViolation, InFailedSqlTransaction
from keyboards import inline
from texts.text import get_text
from google_analytics import analytics

pay_token = config("PAY_TOKEN")
db, cur = connect()


async def apartment_contacts(call: types.CallbackQuery):
    contact_stat()
    tg_id = call.from_user.id
    subscription_status = await check_subscribe_status(tg_id)
    language = await lang(call.from_user.id)
    if subscription_status[0]:
        unique_id = int(call.data.split("_")[1])
        apartment_contacts_amount(unique_id)
        cur.execute(f"SELECT agent_name, agent_whats_up FROM appart_apartment WHERE id=%s", (unique_id,))
        contact = cur.fetchone()
        cur.execute(f"SELECT aps_type, location_id FROM appart_apartment WHERE id=%s", (unique_id,))
        info = cur.fetchone()
        if language in ["EN", "IN"]:
            await call.message.reply(
                f"<b>Agent name:</b> {contact[0]}\n", reply_markup=inline.agent_link(contact[1], info[0], info[1], language)
            )
        elif language == "RU":
            await call.message.reply(
                f"<b>Имя агента:</b> {contact[0]}\n", reply_markup=inline.agent_link(contact[1], info[0], info[1], language)
            )
    else:
        text = await get_text(19, language)
        await call.message.reply(text,
                                 reply_markup=inline.subscribe(language))


async def apartment_contacts_favorites(call: types.CallbackQuery):
    contact_stat()
    await call.message.edit_reply_markup()
    tg_id = call.from_user.id
    subscription_status = await check_subscribe_status(tg_id)
    language = await lang(call.from_user.id)
    if subscription_status[0]:
        unique_id = int(call.data.split("_")[2])
        apartment_contacts_amount(unique_id)
        cur.execute(f"SELECT agent_name, agent_whats_up FROM appart_apartment WHERE id=%s", (unique_id,))
        contact = cur.fetchone()
        cur.execute(f"SELECT aps_type, location_id FROM appart_apartment WHERE id=%s", (unique_id,))
        info = cur.fetchone()
        if language in ["EN", "IN"]:
            await call.message.reply(
                f"<b>Agent name:</b> {contact[0]}\n", reply_markup=inline.agent_link(contact[1], info[0], info[1], language)
            )
        elif language == "RU":
            await call.message.reply(
                f"<b>Имя агента:</b> {contact[0]}\n", reply_markup=inline.agent_link(contact[1], info[0], info[1], language)
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
        cur.execute("INSERT INTO appart_saveap (apart_id, user_id) VALUES (%s, %s)", (id_data, user_id,))
        db.commit()
        apartment_favorites_amount(id_data)
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


async def remove_from_favorites(call: types.CallbackQuery):
    unique_id = call.data
    id_data = int(unique_id.split("_")[1])
    language = await lang(call.from_user.id)
    tg_id = call.from_user.id
    try:
        await call.message.edit_reply_markup()
        user_id = await status(tg_id)
        cur.execute("DELETE FROM appart_saveap WHERE apart_id = %s AND user_id = %s", (id_data, user_id,))
        db.commit()
        text = await get_text(23, language)
        await call.answer(text)
    except UniqueViolation:
        db.rollback()
        await call.message.edit_reply_markup()
        text = await get_text(23, language)
        await call.answer(text=text)
    except InFailedSqlTransaction:
        db.rollback()
        await call.message.edit_reply_markup()
        text = await get_text(23, language)
        await call.answer(text=text)


async def turn_on_subscription(call: types.CallbackQuery):
    subscribe_stat()
    await call.message.edit_reply_markup()
    prices = [
        types.LabeledPrice(label='Monthly subscription', amount=29900),
    ]
    await call.bot.send_invoice(
        chat_id=call.message.chat.id,
        title='Monthly subscription',
        description="To pay, click on the button below",
        provider_token=pay_token,
        currency='RUB',
        prices=prices,
        payload='PAYMENT_PAYLOAD'
    )


async def handle_successful_payment(msg: types.Message):
    await msg.answer("Подписка успешно оформлена!")
    await subscribe_activity(msg.from_id)


def register(dp: Dispatcher):
    try:
        for n in range(0, 1000):
            dp.register_callback_query_handler(apartment_contacts, text=f'contact_{n}')
            dp.register_callback_query_handler(apartment_contacts_favorites, text=f'contact_favorites_{n}')
            dp.register_callback_query_handler(save_to_favorites, text=f"save_{n}")
            dp.register_callback_query_handler(remove_from_favorites, text=f'remove_{n}')
            dp.register_callback_query_handler(turn_on_subscription, text='subscription_on')
            dp.register_message_handler(handle_successful_payment, content_types=ContentTypes.SUCCESSFUL_PAYMENT)
    except TypeError as e:
        print(f'Error in register function: {e}')
