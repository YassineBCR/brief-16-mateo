# api/database.py

import psycopg2

def create_conn():
    conn = psycopg2.connect(
        dbname="postgres",
        user="yass",
        password="toto",
        host="localhost",
        port="5432"
    )
    return conn
