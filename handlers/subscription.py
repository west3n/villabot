import asyncio
import base64
import hashlib
import hmac
import json

import decouple
import requests
from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.utils.exceptions import MessageToDeleteNotFound, MessageIdentifierNotSpecified
from decouple import config
from database import postgre_user, postgre
from database.postgre_statistic import contact_stat, apartment_favorites_amount, apartment_contacts_amount
from psycopg2.errors import UniqueViolation, InFailedSqlTransaction
from keyboards import inline, reply
from texts.text import get_text
from yookassa import Configuration, Payment
import time

db, cur = postgre.connect()
Configuration.configure(config('ACCOUNT_ID'), config('SECRET_KEY'))


class Phone(StatesGroup):
    phone = State()


async def create_payment(call, user_data, description_text):
    res = Payment.create(
        {
            "amount": {
                "value": 490,
                "currency": "RUB"
            },
            "confirmation": {
                "type": "redirect",
                "return_url": f"https://t.me/rentee_bot?start=payments_{call.from_user.id}"
            },
            "capture": True,
            "description": f"{description_text}",
            "receipt": {
                "customer": {
                    "full_name": f"{user_data[2]}",
                    "phone": f"{user_data[5].replace('+', '')}",
                },
                "items": [
                    {
                        "description": "Месячная подписка на Rentee Bot",
                        "quantity": "1",
                        "amount": {
                            "value": 490,
                            "currency": "RUB"
                        },
                        "vat_code": "1",
                        "payment_mode": "full_payment",
                        "payment_subject": "agent_commission"
                    },
                ]
            }
        }
    )
    link = res.confirmation.confirmation_url
    payment_id = res.id
    return link, payment_id


async def create_invoice(tg_id, description_text):
    api_key = decouple.config("THEDEX_KEY")
    secret_key = decouple.config('THEDEX_SECRET')
    baseUrl = 'https://app.thedex.cloud'
    nonce = time.time_ns() // 1_000_000
    request = '/api/v1/invoices/create'
    data = {
        'request': request,
        'nonce': nonce,
        'amount': 8.5,
        'clientId': f"{tg_id}",
        'currency': 'USD',
        'merchantId': decouple.config("MERCHANT_ID"),
        'title': description_text
    }
    completeUrl = baseUrl + request
    data_json = json.dumps(data, separators=(',', ':'))
    payload = base64.b64encode(data_json.encode('ascii'))
    signature = hmac.new(secret_key.encode('ascii'), payload, hashlib.sha512).hexdigest()
    headers = {
        'Content-type': 'application/json',
        'X-EX-APIKEY': api_key,
        'X-EX-PAYLOAD': payload,
        'X-EX-SIGNATURE': signature
    }
    resp = requests.post(completeUrl, headers=headers, data=data_json)
    resp_json = json.dumps(resp.json(), sort_keys=True, indent=4)
    return json.loads(resp_json)['invoiceId'], json.loads(resp_json)['payUrl']


async def invoice_one(invoice_id):
    api_key = decouple.config("THEDEX_KEY")
    secret_key = decouple.config('THEDEX_SECRET')
    baseUrl = 'https://app.thedex.cloud'
    nonce = time.time_ns() // 1_000_000
    request = '/api/v1/invoices/one'
    data = {
        "invoiceId": invoice_id,
        "orderId": "null",
        'nonce': nonce,
        'request': request

    }
    completeUrl = baseUrl + request
    data_json = json.dumps(data, separators=(',', ':'))
    payload = base64.b64encode(data_json.encode('ascii'))
    signature = hmac.new(secret_key.encode('ascii'), payload, hashlib.sha512).hexdigest()
    headers = {
        'Content-type': 'application/json',
        'X-EX-APIKEY': api_key,
        'X-EX-PAYLOAD': payload,
        'X-EX-SIGNATURE': signature,
    }
    resp = requests.post(completeUrl, headers=headers, data=data_json)
    resp_json = json.dumps(resp.json(), sort_keys=True, indent=4)
    return json.loads(resp_json)['statusName']


async def apartment_contacts(call: types.CallbackQuery, state: FSMContext):
    contact_stat()
    tg_id = call.from_user.id
    subscription_status = await postgre_user.check_subscribe_status(tg_id)
    language = await postgre_user.lang(call.from_user.id)
    if subscription_status[0]:
        unique_id = int(call.data.split("_")[1])
        apartment_contacts_amount(unique_id)
        cur.execute(f"SELECT agent_name, agent_whats_up FROM appart_apartment WHERE id=%s", (unique_id,))
        contact = cur.fetchone()
        cur.execute(f"SELECT aps_type, location_id FROM appart_apartment WHERE id=%s", (unique_id,))
        info = cur.fetchone()
        if language in ["EN", "IN"]:
            await call.message.reply(
                f"<b>Agent name:</b> {contact[0]}\n",
                reply_markup=inline.agent_link(contact[1], info[0], info[1], language)
            )
        elif language == "RU":
            await call.message.reply(
                f"<b>Имя агента:</b> {contact[0]}\n",
                reply_markup=inline.agent_link(contact[1], info[0], info[1], language)
            )
    else:
        user_data = await postgre_user.get_user_data(call.from_user.id)
        if user_data[11]:
            payment_status = Payment.find_one(user_data[11]).status
            thedex_status = await invoice_one(user_data[12])
            if payment_status == 'succeeded' or thedex_status == 'Successful':
                await postgre_user.subscribe_activity(call.from_user.id)
                unique_id = int(call.data.split("_")[1])
                apartment_contacts_amount(unique_id)
                cur.execute(f"SELECT agent_name, agent_whats_up FROM appart_apartment WHERE id=%s", (unique_id,))
                contact = cur.fetchone()
                cur.execute(f"SELECT aps_type, location_id FROM appart_apartment WHERE id=%s", (unique_id,))
                info = cur.fetchone()
                if language in ["EN", "IN"]:
                    await call.message.reply(
                        f"<b>Agent name:</b> {contact[0]}\n",
                        reply_markup=inline.agent_link(contact[1], info[0], info[1], language)
                    )
                elif language == "RU":
                    await call.message.reply(
                        f"<b>Имя агента:</b> {contact[0]}\n",
                        reply_markup=inline.agent_link(contact[1], info[0], info[1], language)
                    )
            else:
                text = await get_text(19, language)
                if language in ["EN", "IN"]:
                    text += "\nThe last payment was canceled, please start over!"
                    text += "\nTo pay for the subscription, please click the button below:"
                    description_text = "Monthly subscription to Rentee Bot"
                else:
                    text += '\nПоследняя оплата была отменена, необходимо начать заново!'
                    text += '\nДля оплаты подписки необходимо нажать на кнопку ниже:'
                    description_text = 'Месячная подписка на Rentee Bot'
                yookassa_link, yookassa_payment_id = await create_payment(call, user_data, description_text)
                thedex_payment_id, thedex_link = await create_invoice(call.from_user.id, description_text)
                await postgre_user.new_payment_id(yookassa_payment_id, thedex_payment_id, call.from_user.id)
                message_3 = await call.message.answer(
                    text=text, reply_markup=inline.link_to_payments(yookassa_link, thedex_link, language))
                await asyncio.sleep(40)
                await call.bot.delete_message(call.message.chat.id, message_3.message_id)
        else:
            if user_data[5]:
                text = await get_text(19, language)
                if language in ["EN", "IN"]:
                    text += "\nTo pay for the subscription, please click the button below:"
                    description_text = "Monthly subscription to Rentee Bot"
                else:
                    text += '\nДля оплаты подписки необходимо нажать на кнопку ниже:'
                    description_text = 'Месячная подписка на Rentee Bot'
                yookassa_link, yookassa_payment_id = await create_payment(call, user_data, description_text)
                thedex_payment_id, thedex_link = await create_invoice(call.from_user.id, description_text)
                await postgre_user.new_payment_id(yookassa_payment_id, thedex_payment_id, call.from_user.id)
                message_3 = await call.message.answer(
                    text=text, reply_markup=inline.link_to_payments(yookassa_link, thedex_link, language))
                await asyncio.sleep(40)
                await call.bot.delete_message(call.message.chat.id, message_3.message_id)
            else:
                text = 'Для оформления подписки, вам необходимо предоставить номер телефона для отправки чека.' \
                       '\nНажмите на кнопку ниже или отправьте номер в формате +7xxxxxxxxxx'
                if language in ["EN", "IN"]:
                    text = "To subscribe, you need to provide a phone number for sending the receipt." \
                           "Press the button below or send your number in the format +7xxxxxxxxxx"
                await Phone.phone.set()
                message_2 = await call.message.answer(text, reply_markup=reply.contact())
                async with state.proxy() as data:
                    data['message_2'] = message_2.message_id


async def handle_user_phone(msg: types.Message, state: FSMContext):
    language = await postgre_user.lang(msg.from_user.id)
    if msg.contact:
        await msg.delete()
        async with state.proxy() as data:
            try:
                await msg.bot.delete_message(msg.chat.id, data.get('message'))
            except (MessageToDeleteNotFound, MessageIdentifierNotSpecified):
                pass
            try:
                await msg.bot.delete_message(msg.chat.id, data.get('message_2'))
            except (MessageToDeleteNotFound, MessageIdentifierNotSpecified):
                pass
        phone = msg.contact.phone_number
        await postgre_user.new_phone(phone, msg.from_user.id)
        user_data = await postgre_user.get_user_data(msg.from_user.id)
        if user_data[5]:
            text = await get_text(19, language)
            user_data = await postgre_user.get_user_data(msg.from_user.id)
            if language in ["EN", "IN"]:
                text += "\nTo pay for the subscription, please click the button below:"
                description_text = "Monthly subscription to Rentee Bot"
            else:
                text += '\nДля оплаты подписки необходимо нажать на кнопку ниже:'
                description_text = 'Месячная подписка на Rentee Bot'
            yookassa_link, yookassa_payment_id = await create_payment(msg, user_data, description_text)
            thedex_payment_id, thedex_link = await create_invoice(msg.from_user.id, description_text)
            await postgre_user.new_payment_id(yookassa_payment_id, thedex_payment_id, msg.from_user.id)
            await msg.answer(text=text, reply_markup=inline.link_to_payments(yookassa_link, thedex_link, language))
    else:
        async with state.proxy() as data:
            try:
                await msg.bot.delete_message(msg.chat.id, data.get('message'))
            except (MessageToDeleteNotFound, MessageIdentifierNotSpecified):
                pass
            try:
                await msg.bot.delete_message(msg.chat.id, data.get('message_2'))
            except (MessageToDeleteNotFound, MessageIdentifierNotSpecified):
                pass
        if msg.text.startswith('+') and msg.text.split("+")[1].isdigit():
            phone = msg.text
            await msg.delete()
            await postgre_user.new_phone(phone, msg.from_user.id)
            user_data = await postgre_user.get_user_data(msg.from_user.id)
            if user_data[5]:
                text = await get_text(19, language)
                user_data = await postgre_user.get_user_data(msg.from_user.id)
                if language in ["EN", "IN"]:
                    text += "\nTo pay for the subscription, please click the button below:"
                    description_text = "Monthly subscription to Rentee Bot"
                else:
                    text += '\nДля оплаты подписки необходимо нажать на кнопку ниже:'
                    description_text = 'Месячная подписка на Rentee Bot'
                yookassa_link, yookassa_payment_id = await create_payment(msg, user_data, description_text)
                thedex_payment_id, thedex_link = await create_invoice(msg.from_user.id, description_text)
                await postgre_user.new_payment_id(yookassa_payment_id, thedex_payment_id, msg.from_user.id)
                await msg.answer(text=text, reply_markup=inline.link_to_payments(yookassa_link, thedex_link, language))
        else:
            await msg.delete()
            text = 'Введите номер в формате +7xxxxxxxxxx'
            if language in ["EN", "IN"]:
                text = 'Input phone number in the format +7xxxxxxxxx'
            message = await msg.answer(text)
            async with state.proxy() as data:
                data['message'] = message.message_id


async def apartment_contacts_favorites(call: types.CallbackQuery, state: FSMContext):
    contact_stat()
    await call.message.edit_reply_markup()
    tg_id = call.from_user.id
    subscription_status = await postgre_user.check_subscribe_status(tg_id)
    language = await postgre_user.lang(call.from_user.id)
    if subscription_status[0]:
        unique_id = int(call.data.split("_")[2])
        apartment_contacts_amount(unique_id)
        cur.execute(f"SELECT agent_name, agent_whats_up FROM appart_apartment WHERE id=%s", (unique_id,))
        contact = cur.fetchone()
        cur.execute(f"SELECT aps_type, location_id FROM appart_apartment WHERE id=%s", (unique_id,))
        info = cur.fetchone()
        if language in ["EN", "IN"]:
            await call.message.reply(
                f"<b>Agent name:</b> {contact[0]}\n",
                reply_markup=inline.agent_link(contact[1], info[0], info[1], language)
            )
        elif language == "RU":
            await call.message.reply(
                f"<b>Имя агента:</b> {contact[0]}\n",
                reply_markup=inline.agent_link(contact[1], info[0], info[1], language)
            )
    else:
        user_data = await postgre_user.get_user_data(call.from_user.id)
        if user_data[11]:
            payment_status = Payment.find_one(user_data[11]).status
            thedex_status = await invoice_one(user_data[12])
            if payment_status == 'succeeded' or thedex_status == 'Successful':
                await postgre_user.subscribe_activity(call.from_user.id)
                unique_id = int(call.data.split("_")[2])
                apartment_contacts_amount(unique_id)
                cur.execute(f"SELECT agent_name, agent_whats_up FROM appart_apartment WHERE id=%s", (unique_id,))
                contact = cur.fetchone()
                cur.execute(f"SELECT aps_type, location_id FROM appart_apartment WHERE id=%s", (unique_id,))
                info = cur.fetchone()
                if language in ["EN", "IN"]:
                    await call.message.reply(
                        f"<b>Agent name:</b> {contact[0]}\n",
                        reply_markup=inline.agent_link(contact[1], info[0], info[1], language)
                    )
                elif language == "RU":
                    await call.message.reply(
                        f"<b>Имя агента:</b> {contact[0]}\n",
                        reply_markup=inline.agent_link(contact[1], info[0], info[1], language)
                    )
            else:
                text = await get_text(19, language)
                if language in ["EN", "IN"]:
                    text += "\nThe last payment was canceled, please start over!"
                    text += "\nTo pay for the subscription, please click the button below:"
                    description_text = "Monthly subscription to Rentee Bot"
                else:
                    text += '\nПоследняя оплата была отменена, необходимо начать заново!'
                    text += '\nДля оплаты подписки необходимо нажать на кнопку ниже:'
                    description_text = 'Месячная подписка на Rentee Bot'
                yookassa_link, yookassa_payment_id = await create_payment(call, user_data, description_text)
                thedex_payment_id, thedex_link = await create_invoice(call.from_user.id, description_text)
                await postgre_user.new_payment_id(yookassa_payment_id, thedex_payment_id, call.from_user.id)
                message_3 = await call.message.answer(
                    text=text, reply_markup=inline.link_to_payments(yookassa_link, thedex_link, language))
                await asyncio.sleep(40)
                await call.bot.delete_message(call.message.chat.id, message_3.message_id)
        else:
            if user_data[5]:
                text = await get_text(19, language)
                if language in ["EN", "IN"]:
                    text += "\nTo pay for the subscription, please click the button below:"
                    description_text = "Monthly subscription to Rentee Bot"
                else:
                    text += '\nДля оплаты подписки необходимо нажать на кнопку ниже:'
                    description_text = 'Месячная подписка на Rentee Bot'
                yookassa_link, yookassa_payment_id = await create_payment(call, user_data, description_text)
                thedex_payment_id, thedex_link = await create_invoice(call.from_user.id, description_text)
                await postgre_user.new_payment_id(yookassa_payment_id, thedex_payment_id, call.from_user.id)
                message_3 = await call.message.answer(
                    text=text, reply_markup=inline.link_to_payments(yookassa_link, thedex_link, language))
                await asyncio.sleep(40)
                await call.bot.delete_message(call.message.chat.id, message_3.message_id)
            else:
                text = 'Для оформления подписки, вам необходимо предоставить номер телефона для отправки чека.' \
                       '\nНажмите на кнопку ниже или отправьте номер в формате +7xxxxxxxxxx'
                if language in ["EN", "IN"]:
                    text = "To subscribe, you need to provide a phone number for sending the receipt." \
                           "Press the button below or send your number in the format +7xxxxxxxxxx"
                await Phone.phone.set()
                message_2 = await call.message.answer(text, reply_markup=reply.contact())
                async with state.proxy() as data:
                    data['message_2'] = message_2.message_id


async def save_to_favorites(call: types.CallbackQuery):
    unique_id = call.data
    id_data = int(unique_id.split("_")[1])
    language = await postgre_user.lang(call.from_user.id)
    await call.message.edit_reply_markup(reply_markup=inline.contacts(str(id_data), language))
    tg_id = call.from_user.id
    try:
        user_id = await postgre_user.status(tg_id)
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
    language = await postgre_user.lang(call.from_user.id)
    tg_id = call.from_user.id
    try:
        await call.message.edit_reply_markup()
        user_id = await postgre_user.status(tg_id)
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


def register(dp: Dispatcher):
    try:
        for n in range(0, 1000):
            dp.register_callback_query_handler(apartment_contacts, text=f'contact_{n}')
            dp.register_message_handler(handle_user_phone, state=Phone.phone, content_types=['contact', 'text'])
            dp.register_callback_query_handler(apartment_contacts_favorites, text=f'contact_favorites_{n}')
            dp.register_callback_query_handler(save_to_favorites, text=f"save_{n}")
            dp.register_callback_query_handler(remove_from_favorites, text=f'remove_{n}')
    except TypeError as e:
        print(f'Error in register function: {e}')
