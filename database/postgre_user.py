from database.postgre import db, cur


async def status(tg_id: int):
    cur.execute("SELECT id FROM appart_rentuser WHERE tg_id=%s", (tg_id,))
    result = cur.fetchone()
    if result:
        return result[0]
    else:
        return None


async def add_user(username, tg_id, start_register, last_activity, data, last_name):
    cur.execute(
        "INSERT INTO appart_rentuser (first_name, last_name, username, tg_id, "
        "register, last_activity, default_lang, phone) "
        "VALUES(%s, %s, %s, %s, %s, %s, %s, %s)",
        (data.get('first_name'), last_name, username, tg_id, start_register,
         last_activity, data.get('lang'), data.get('contact'),))
    db.commit()


async def update_activity(last_activity, tg_id):
    cur.execute("UPDATE appart_rentuser SET last_activity=%s WHERE tg_id=%s", (last_activity, tg_id,))
    db.commit()
