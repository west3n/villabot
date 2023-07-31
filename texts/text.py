from database.postgre import connect


async def get_text(action: int, lang):
    db, cur = connect()
    try:
        if lang == 'EN':
            cur.execute("SELECT text_in_english FROM texts_in_bot_text WHERE action=%s", (action,))
            text = cur.fetchone()[0]
            return text
        if lang == 'RU':
            cur.execute("SELECT text_in_russian FROM texts_in_bot_text WHERE action=%s", (action,))
            text = cur.fetchone()[0]
            return text
        if lang == 'IN':
            cur.execute("SELECT text_in_indonesian FROM texts_in_bot_text WHERE action=%s", (action,))
            text = cur.fetchone()[0]
            return text
    finally:
        cur.close()
        db.close()
