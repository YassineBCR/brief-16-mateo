from db import create_db_connection, update_meteo_data


def exec_fetch_data():
    conn = create_db_connection()
    cur = conn.cursor()

    update_meteo_data(conn)  # Passer la connexion à la fonction update_meteo_data()

    cur.close()
    conn.close()


if __name__ == "__main__":
    exec_fetch_data()
