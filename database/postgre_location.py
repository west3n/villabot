from database.postgre import db, cur


def get_location():
    cur.execute("SELECT name FROM appart_location")
    locations = cur.fetchall()
    return locations
