import psycopg2

db = psycopg2.connect(
    host="80.90.190.122",
    database="default_db",
    user="gen_user",
    password="Golova123"
)

cur = db.cursor()
