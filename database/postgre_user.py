import datetime
from database.postgre import connect


async def status(tg_id: int):
    db, cur = connect()
    try:
        cur.execute("SELECT id FROM appart_rentuser WHERE tg_id=%s", (tg_id,))
        result = cur.fetchone()

        if result:
            return result[0]
        else:
            return None
    finally:
        cur.close()
        db.close()


async def lang(tg_id):
    db, cur = connect()
    try:
        cur.execute("SELECT default_lang FROM appart_rentuser WHERE tg_id=%s", (tg_id,))
        result = cur.fetchone()

        return result[0]
    finally:
        cur.close()
        db.close()


async def add_user(username, tg_id, start_register, last_activity, data, last_name):
    db, cur = connect()
    first_name = ""
    contact = ""
    try:
        cur.execute(
            "INSERT INTO appart_rentuser (first_name, last_name, username, tg_id, "
            "register, last_activity, default_lang, phone, subscribe) "
            "VALUES(%s, %s, %s, %s, %s, %s, %s, %s, false)",
            (first_name,
             last_name,
             username,
             tg_id,
             start_register,
             last_activity,
             data.get('lang'),
             contact))
        db.commit()
    finally:
        cur.close()
        db.close()


async def update_user(username, tg_id, start_register, last_activity, data, last_name):
    db, cur = connect()
    first_name = ""
    try:
        cur.execute(
            "UPDATE appart_rentuser SET first_name = %s, last_name = %s, username = %s, register = %s, "
            "last_activity = %s, default_lang = %s WHERE tg_id = %s",
            (first_name,
             last_name,
             username,
             start_register,
             last_activity,
             data.get('lang'),
             tg_id))
        db.commit()
    finally:
        cur.close()
        db.close()


async def update_activity(last_activity, tg_id):
    db, cur = connect()
    try:
        cur.execute("UPDATE appart_rentuser SET last_activity=%s WHERE tg_id=%s", (last_activity, tg_id,))
        db.commit()
    finally:
        cur.close()
        db.close()


async def check_subscribe_status(tg_id):
    db, cur = connect()
    try:
        cur.execute("SELECT subscribe FROM appart_rentuser WHERE tg_id=%s", (tg_id,))
        result = cur.fetchone()
        return result
    finally:
        cur.close()
        db.close()


async def subscribe_activity(tg_id):
    db, cur = connect()
    now = datetime.datetime.now().date() + datetime.timedelta(days=30)
    try:
        cur.execute("UPDATE appart_rentuser SET subscribe=true,"
                    " date_subscribe = %s, payments_id = null, invoice_id = null WHERE tg_id=%s", (now, tg_id,))
        db.commit()
    finally:
        cur.close()
        db.close()


async def get_user_data(tg_id):
    db, cur = connect()
    try:
        cur.execute("SELECT * FROM appart_rentuser WHERE tg_id=%s", (tg_id,))
        return cur.fetchone()
    finally:
        cur.close()
        db.close()


async def new_phone(phone, tg_id):
    db, cur = connect()
    try:
        cur.execute("UPDATE appart_rentuser SET phone = %s WHERE tg_id=%s", (phone, tg_id,))
        db.commit()
    finally:
        cur.close()
        db.close()


async def new_payment_id(payment_id, invoice_id,  tg_id):
    db, cur = connect()
    try:
        cur.execute("UPDATE appart_rentuser SET payments_id = %s, invoice_id = %s WHERE tg_id=%s",
                    (payment_id, invoice_id, tg_id,))
        db.commit()
    finally:
        cur.close()
        db.close()


async def get_all_tg_ids():
    db, cur = connect()
    try:
        cur.execute("SELECT tg_id FROM appart_rentuser")
        return [tg_id[0] for tg_id in cur.fetchall()]
    finally:
        cur.close()
        db.close()


async def end_subscription(tg_id):
    db, cur = connect()
    try:
        cur.execute("UPDATE appart_rentuser SET subscribe = false, date_subscribe = null WHERE tg_id=%s",
                    (tg_id,))
        db.commit()
    finally:
        cur.close()
        db.close()
