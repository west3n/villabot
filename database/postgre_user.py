from database.postgre import db, cur


async def status(tg_id: int):
    cur.execute("SELECT id FROM appart_rentuser WHERE tg_id=%s", (tg_id,))
    result = cur.fetchone()
    if result:
        return result[0]
    else:
        return None


async def lang(tg_id):
    cur.execute("SELECT default_lang FROM appart_rentuser WHERE tg_id=%s", (tg_id,))
    result = cur.fetchone()
    return result[0]


async def add_user(username, tg_id, start_register, last_activity, data, last_name):
    cur.execute(
        "INSERT INTO appart_rentuser (first_name, last_name, username, tg_id, "
        "register, last_activity, default_lang, phone, subscribe) "
        "VALUES(%s, %s, %s, %s, %s, %s, %s, %s, false)",
        (data.get('first_name'), last_name, username, tg_id, start_register,
         last_activity, data.get('lang'), data.get('contact'),))
    db.commit()


async def update_user(username, tg_id, start_register, last_activity, data, last_name):
    cur.execute(
        "UPDATE appart_rentuser SET first_name = %s, last_name = %s, username = %s, register = %s, "
        "last_activity = %s, default_lang = %s, phone = %s WHERE tg_id = %s",
        (data.get('first_name'), last_name, username, start_register,
         last_activity, data.get('lang'), data.get('contact'), tg_id))
    db.commit()


async def update_activity(last_activity, tg_id):
    cur.execute("UPDATE appart_rentuser SET last_activity=%s WHERE tg_id=%s", (last_activity, tg_id,))
    db.commit()


async def check_subscribe_status(tg_id):
    cur.execute("SELECT subscribe FROM appart_rentuser WHERE tg_id=%s", (tg_id,))
    result = cur.fetchone()
    return result


async def subscribe_activity(tg_id):
    cur.execute("UPDATE appart_rentuser SET subscribe=true WHERE tg_id=%s", (tg_id,))
    db.commit()
