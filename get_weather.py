import psycopg2
from database.config import dbname, user, password, host, port


def get_meteo_data(city):
    conn = psycopg2.connect(
        dbname="mateo", user="yass", password="toto", host="localhost", port="5432"
    )
    cur = conn.cursor()
    cur.execute("SELECT * FROM meteo_data WHERE city = %s", (city,))
    result = cur.fetchone()
    conn.close()
    return result
