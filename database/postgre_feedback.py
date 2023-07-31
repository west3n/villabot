from database.postgre_user import status
import datetime
from database.postgre import connect


async def add_feedback(tg_id, data):
    db, cur = connect()
    try:
        user_id = await status(tg_id)
        cur.execute("INSERT INTO appart_feedback(user_id, type_a, text) VALUES (%s, %s, %s)",
                    (user_id, data.get('f_type'), data.get('text'),))
        db.commit()
    finally:
        cur.close()
        db.close()


async def get_update_history(tg_id):
    db, cur = connect()
    try:
        user_id = await status(tg_id)
        cur.execute("SELECT text, answer FROM appart_feedback WHERE user_id=%s", (user_id,))
        history = cur.fetchone()
        return history
    finally:
        cur.close()
        db.close()


async def get_history(user_id):
    db, cur = connect()
    try:
        cur.execute("SELECT history FROM appart_feedback WHERE user_id=%s", (user_id,))
        result = cur.fetchone()
        return result
    finally:
        cur.close()
        db.close()


async def update_feedback(tg_id, history, data):
    db, cur = connect()
    try:
        user_id = await status(tg_id)
        old_history = await get_history(user_id)
        history_str = ''
        if old_history is None:
            history_str += f'[{datetime.datetime.now()}] User: {history[0]}\n' \
                           f'[{datetime.datetime.now()}] Admin: {history[1]}'
        if old_history is not None:
            history_str += f'{old_history[0]}\n'
            history_str += f'[{datetime.datetime.now()}] User: {history[0]}\n' \
                           f'[{datetime.datetime.now()}] Admin: {history[1]}'
        cur.execute("UPDATE appart_feedback SET text=%s, answer=NULL, history=%s WHERE user_id=%s",
                    (data.get('text'), history_str, user_id,))
        db.commit()
    finally:
        cur.close()
        db.close()


async def delete_feedback(tg_id):
    db, cur = connect()
    try:
        user_id = await status(tg_id)
        cur.execute("DELETE FROM appart_feedback WHERE user_id=%s", (user_id,))
        db.commit()
    finally:
        cur.close()
        db.close()
