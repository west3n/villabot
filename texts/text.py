from database.postgre import db, cur


async def get_text(action: int, lang):
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
