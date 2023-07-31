from database.postgre_user import status
from database.postgre import connect


async def get_favorite(tg_id):
    db, cur = connect()
    try:
        user_id = await status(tg_id)
        cur.execute("SELECT apart_id FROM appart_saveap WHERE user_id=%s", (user_id,))
        query = cur.fetchall()
        result = []
        if query:
            for x in query:
                result.append(x[0])
        aps = []
        if result:
            for x in result:
                cur.execute("SELECT * FROM appart_apartment WHERE id=%s", (x,))
                ap = cur.fetchone()
                aps.append(ap)
        return aps
    finally:
        cur.close()
        db.close()
