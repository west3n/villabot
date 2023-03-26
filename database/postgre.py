import psycopg2

db = psycopg2.connect(
    host="85.92.111.75",
    database="default_db",
    user="gen_user",
    password="Golova123"
)

cur = db.cursor()
