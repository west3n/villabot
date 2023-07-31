from database.postgre import connect


def get_location():
    db, cur = connect()
    try:
        cur.execute("SELECT name FROM appart_location")
        locations = cur.fetchall()
        return locations
    finally:
        db.close()
        cur.close()
