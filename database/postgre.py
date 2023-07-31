import psycopg2
import decouple


def connect():
    try:
        db = psycopg2.connect(
            host=decouple.config('DB_HOST'),
            database=decouple.config('DB_NAME'),
            user=decouple.config('DB_USER'),
            password=decouple.config('DB_PASS'),
            port=decouple.config('DB_PORT')
        )
        cur = db.cursor()
    except psycopg2.Error:
        db = psycopg2.connect(
            host=decouple.config('DB_HOST'),
            database=decouple.config('DB_NAME'),
            user=decouple.config('DB_USER'),
            password=decouple.config('DB_PASS'),
            port=decouple.config('DB_PORT')
        )
        cur = db.cursor()
    return db, cur
