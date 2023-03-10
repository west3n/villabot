from database.postgre import db, cur


async def get_text(action: int, lang):
    if lang == 'EN':
        text = cur.execute("SELECT text_in_english FROM texts_in_bot_text WHERE action=%s", (action,)).fetchone()
        return text
    if lang == 'RU':
        text = cur.execute("SELECT text_in_russian FROM texts_in_bot_text WHERE action=%s", (action,)).fetchone()
        return text
    if lang == 'IN':
        text = cur.execute("SELECT text_in_indonesian FROM texts_in_bot_text WHERE action=%s", (action,)).fetchone()
        return text
