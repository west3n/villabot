from database.postgre import cur, db
from datetime import datetime


def link_stat():
    now = datetime.now().date()
    cur.execute("""
        INSERT INTO statistic_commonstatistic (date, link)
        VALUES (%s, COALESCE((SELECT link FROM statistic_commonstatistic WHERE date=%s), 0) + 1)
        ON CONFLICT (date) DO UPDATE SET link = COALESCE(statistic_commonstatistic.link, 0) + 1
    """, (now, now))
    db.commit()


def cmd_start_stat():
    now = datetime.now().date()
    cur.execute("""
            INSERT INTO statistic_commonstatistic (date, cmd_start)
            VALUES (%s, COALESCE((SELECT cmd_start FROM statistic_commonstatistic WHERE date=%s), 0) + 1)
            ON CONFLICT (date) DO UPDATE SET cmd_start = COALESCE(statistic_commonstatistic.cmd_start, 0) + 1
        """, (now, now))
    db.commit()


def start_register_stat():
    now = datetime.now().date()
    cur.execute("""
            INSERT INTO statistic_commonstatistic (date, start_register)
            VALUES (%s, COALESCE((SELECT start_register FROM statistic_commonstatistic WHERE date=%s), 0) + 1)
            ON CONFLICT (date) DO UPDATE SET start_register = COALESCE(statistic_commonstatistic.start_register, 0) + 1
        """, (now, now))
    db.commit()


def finish_register_stat():
    now = datetime.now().date()
    cur.execute("""
            INSERT INTO statistic_commonstatistic (date, finish_register)
            VALUES (%s, COALESCE((SELECT finish_register FROM statistic_commonstatistic WHERE date=%s), 0) + 1)
            ON CONFLICT (date) DO UPDATE SET finish_register = COALESCE(statistic_commonstatistic.finish_register, 0) + 1
        """, (now, now))
    db.commit()


def contact_stat():
    now = datetime.now().date()
    cur.execute("""
            INSERT INTO statistic_commonstatistic (date, contact)
            VALUES (%s, COALESCE((SELECT contact FROM statistic_commonstatistic WHERE date=%s), 0) + 1)
            ON CONFLICT (date) DO UPDATE SET contact = COALESCE(statistic_commonstatistic.contact, 0) + 1
        """, (now, now))
    db.commit()


def subscribe_stat():
    now = datetime.now().date()
    cur.execute("""
            INSERT INTO statistic_commonstatistic (date, subscribe)
            VALUES (%s, COALESCE((SELECT subscribe FROM statistic_commonstatistic WHERE date=%s), 0) + 1)
            ON CONFLICT (date) DO UPDATE SET subscribe = COALESCE(statistic_commonstatistic.subscribe, 0) + 1
        """, (now, now))
    db.commit()


def find_stat():
    now = datetime.now().date()
    cur.execute("""
            INSERT INTO statistic_commonstatistic (date, find)
            VALUES (%s, COALESCE((SELECT find FROM statistic_commonstatistic WHERE date=%s), 0) + 1)
            ON CONFLICT (date) DO UPDATE SET find = COALESCE(statistic_commonstatistic.find, 0) + 1
        """, (now, now))
    db.commit()


def search_stat():
    now = datetime.now().date()
    cur.execute("""
            INSERT INTO statistic_commonstatistic (date, search)
            VALUES (%s, COALESCE((SELECT search FROM statistic_commonstatistic WHERE date=%s), 0) + 1)
            ON CONFLICT (date) DO UPDATE SET search = COALESCE(statistic_commonstatistic.search, 0) + 1
        """, (now, now))
    db.commit()


def apartment_views_amount(apart_id):
    now = datetime.now()
    cur.execute("""
            INSERT INTO statistic_apartstatistic (find_date, views, apart_id)
            VALUES (%s, COALESCE((SELECT views FROM statistic_apartstatistic WHERE apart_id=%s), 0) + 1, %s)
            ON CONFLICT (apart_id) DO UPDATE SET views = COALESCE(statistic_apartstatistic.views, 0) + 1, find_date = %s
        """, (now, apart_id, apart_id, now))
    db.commit()


def apartment_favorites_amount(apart_id):
    now = datetime.now()
    cur.execute("""
            INSERT INTO statistic_apartstatistic (favorite_date, favorite, apart_id)
            VALUES (%s, COALESCE((SELECT favorite FROM statistic_apartstatistic WHERE apart_id=%s), 0) + 1, %s)
            ON CONFLICT (apart_id) DO UPDATE SET favorite = COALESCE(statistic_apartstatistic.favorite, 0) + 1, 
            favorite_date = %s
        """, (now, apart_id, apart_id, now))
    db.commit()


def apartment_contacts_amount(apart_id):
    cur.execute("""
            INSERT INTO statistic_apartstatistic (apart_id, contact)
            VALUES (%s, COALESCE((SELECT contact FROM statistic_apartstatistic WHERE apart_id=%s), 0) + 1)
            ON CONFLICT (apart_id) DO UPDATE SET contact = COALESCE(statistic_apartstatistic.contact, 0) + 1
        """, (apart_id, apart_id))
    db.commit()
