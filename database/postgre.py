import psycopg2

db = psycopg2.connect(
    host="81.200.152.124",
    database="default_db",
    user="gen_user",
    password="Golova123"
)

cur = db.cursor()

