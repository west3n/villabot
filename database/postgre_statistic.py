from database.postgre import cur, db
from datetime import datetime


def link_stat():
    now = datetime.now().date()
    cur.execute("""
        INSERT INTO statistic_usersstatistic (date, link)
        VALUES (%s, COALESCE((SELECT link FROM statistic_usersstatistic WHERE date=%s), 0) + 1)
        ON CONFLICT (date) DO UPDATE SET link = COALESCE(statistic_usersstatistic.link, 0) + 1
    """, (now, now))
    db.commit()


def cmd_start_stat():
    now = datetime.now().date()
    cur.execute("""
            INSERT INTO statistic_usersstatistic (date, cmd_start)
            VALUES (%s, COALESCE((SELECT cmd_start FROM statistic_usersstatistic WHERE date=%s), 0) + 1)
            ON CONFLICT (date) DO UPDATE SET cmd_start = COALESCE(statistic_usersstatistic.cmd_start, 0) + 1
        """, (now, now))
    db.commit()


def start_register_stat():
    now = datetime.now().date()
    cur.execute("""
            INSERT INTO statistic_usersstatistic (date, start_register)
            VALUES (%s, COALESCE((SELECT start_register FROM statistic_usersstatistic WHERE date=%s), 0) + 1)
            ON CONFLICT (date) DO UPDATE SET start_register = COALESCE(statistic_usersstatistic.start_register, 0) + 1
        """, (now, now))
    db.commit()


def finish_register_stat():
    now = datetime.now().date()
    cur.execute("""
            INSERT INTO statistic_usersstatistic (date, finish_register)
            VALUES (%s, COALESCE((SELECT finish_register FROM statistic_usersstatistic WHERE date=%s), 0) + 1)
            ON CONFLICT (date) DO UPDATE SET finish_register = COALESCE(statistic_usersstatistic.finish_register, 0) + 1
        """, (now, now))
    db.commit()


def contact_stat():
    now = datetime.now().date()
    cur.execute("""
            INSERT INTO statistic_usersstatistic (date, contact)
            VALUES (%s, COALESCE((SELECT contact FROM statistic_usersstatistic WHERE date=%s), 0) + 1)
            ON CONFLICT (date) DO UPDATE SET contact = COALESCE(statistic_usersstatistic.contact, 0) + 1
        """, (now, now))
    db.commit()


def subscribe_stat():
    now = datetime.now().date()
    cur.execute("""
            INSERT INTO statistic_usersstatistic (date, subscribe)
            VALUES (%s, COALESCE((SELECT subscribe FROM statistic_usersstatistic WHERE date=%s), 0) + 1)
            ON CONFLICT (date) DO UPDATE SET subscribe = COALESCE(statistic_usersstatistic.subscribe, 0) + 1
        """, (now, now))
    db.commit()


def find_stat():
    now = datetime.now().date()
    cur.execute("""
            INSERT INTO statistic_usersstatistic (date, find)
            VALUES (%s, COALESCE((SELECT find FROM statistic_usersstatistic WHERE date=%s), 0) + 1)
            ON CONFLICT (date) DO UPDATE SET find = COALESCE(statistic_usersstatistic.find, 0) + 1
        """, (now, now))
    db.commit()


def search_stat():
    now = datetime.now().date()
    cur.execute("""
            INSERT INTO statistic_usersstatistic (date, search)
            VALUES (%s, COALESCE((SELECT search FROM statistic_usersstatistic WHERE date=%s), 0) + 1)
            ON CONFLICT (date) DO UPDATE SET search = COALESCE(statistic_usersstatistic.search, 0) + 1
        """, (now, now))
    db.commit()