from database.postgre import cur, db
from datetime import datetime


def unique_user_stat():
    now = datetime.now().date()
    cur.execute("""
        INSERT INTO statistic_statistic (date, unique_users)
        VALUES (%s, COALESCE((SELECT unique_users FROM statistic_statistic WHERE date=%s), 0) + 1)
        ON CONFLICT (date) DO UPDATE SET unique_users = COALESCE(statistic_statistic.unique_users, 0) + 1
    """, (now, now))
    db.commit()


def command_start_stat():
    now = datetime.now().date()
    cur.execute("""
            INSERT INTO statistic_statistic (date, users_start)
            VALUES (%s, COALESCE((SELECT users_start FROM statistic_statistic WHERE date=%s), 0) + 1)
            ON CONFLICT (date) DO UPDATE SET users_start = COALESCE(statistic_statistic.users_start, 0) + 1
        """, (now, now))
    db.commit()


def command_contact_stat():
    now = datetime.now().date()
    cur.execute("""
            INSERT INTO statistic_statistic (date, users_finsh)
            VALUES (%s, COALESCE((SELECT users_finsh FROM statistic_statistic WHERE date=%s), 0) + 1)
            ON CONFLICT (date) DO UPDATE SET users_finsh = COALESCE(statistic_statistic.users_finsh, 0) + 1
        """, (now, now))
    db.commit()


def command_payment_stat():
    now = datetime.now().date()
    cur.execute("""
            INSERT INTO statistic_statistic (date, users_pay)
            VALUES (%s, COALESCE((SELECT users_pay FROM statistic_statistic WHERE date=%s), 0) + 1)
            ON CONFLICT (date) DO UPDATE SET users_pay = COALESCE(statistic_statistic.users_pay, 0) + 1
        """, (now, now))
    db.commit()
