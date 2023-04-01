import psycopg2

db = psycopg2.connect(
    host="db-villabot-do-user-13857954-0.b.db.ondigitalocean.com",
    database="defaultdb",
    user="doadmin",
    password="AVNS_9TWJQ4KUZGhFG6d7kFX",
    port="25060"

)

cur = db.cursor()
