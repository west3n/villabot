from database.postgre import cur, db
from database.postgre_user import status
import datetime


async def add_feedback(tg_id, data):
    user_id = await status(tg_id)
    cur.execute("INSERT INTO appart_feedback(user_id, type_a, text) VALUES (%s, %s, %s)",
                (user_id, data.get('f_type'), data.get('text'),))
    db.commit()


async def get_update_history(tg_id):
    user_id = await status(tg_id)
    cur.execute("SELECT text, answer FROM appart_feedback WHERE user_id=%s", (user_id,))
    history = cur.fetchone()
    return history


async def update_feedback(tg_id, history, data):
    user_id = await status(tg_id)
    history_str = ''
    history_str += f'[{datetime.datetime.now()}] User: {history[0]}\n' \
                   f'[{datetime.datetime.now()}] Admin: {history[1]}'
    cur.execute("UPDATE appart_feedback SET text=%s, answer=NULL, history=%s WHERE user_id=%s",
                (data.get('text'), history_str, user_id,))
    db.commit()


async def delete_feedback(tg_id):
    user_id = await status(tg_id)
    cur.execute("DELETE FROM appart_feedback WHERE user_id=%s", (user_id,))
    db.commit()
