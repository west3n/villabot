from database.postgre import cur
from database.postgre_user import status


async def get_favorite(tg_id):
    user_id = await status(tg_id)

    cur.execute("SELECT apart_id FROM appart_saveap WHERE user_id=%s", (user_id,))
    query = cur.fetchall()

    result = []
    if query is not None:
        for x in query:
            result.append(x)
    aps = []
    if result is not None:
        for x in result:
            cur.execute("SELECT * FROM appart_apartment WHERE id=%s", (x,))
            ap = cur.fetchone()
            aps.append(ap)
    return aps




