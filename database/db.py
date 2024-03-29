import psycopg2
from meteofrance_api import MeteoFranceClient
from meteofrance_api.helpers import readeable_phenomenoms_dict
from cities import cities
import json
import datetime
from config import dbname, user, password, host, port

def create_db_connection():
    conn = psycopg2.connect(
        dbname=dbname, user=user, password=password, host=host, port=port
    )
    return conn
def create_table(cur, conn):
    cur.execute("""
        CREATE TABLE IF NOT EXISTS meteo_data (
            id SERIAL PRIMARY KEY,
            city VARCHAR(100),
            latitude FLOAT,
            longitude FLOAT,
            date BIGINT,
            tmin FLOAT,
            tmax FLOAT,
            hmin INTEGER,
            hmax INTEGER,
            precipitation FLOAT,
            sunrise BIGINT,
            sunset BIGINT,
            weather_desc VARCHAR(100),
            weather_icon VARCHAR(100),
            rain_status VARCHAR(100),
            readable_warnings JSON,
            insert_dt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    # Commit après la création de la table
    conn.commit()

def insert_meteo_data(conn, cur, city, latitude, longitude, date, tmin, tmax, hmin, hmax, precipitation, sunrise, sunset, weather_desc, weather_icon, rain_status, readable_warnings):
    cur.execute("""
        INSERT INTO meteo_data (
            city, latitude, longitude, date, tmin, tmax, hmin, hmax,
            precipitation, sunrise, sunset, weather_desc, weather_icon,
            rain_status, readable_warnings
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        city,
        latitude,
        longitude,
        date,
        tmin,
        tmax,
        hmin,
        hmax,
        precipitation,
        sunrise,
        sunset,
        weather_desc,
        weather_icon,
        rain_status,
        json.dumps(readable_warnings)
    ))
    # Commit après l'insertion de données
    conn.commit()
def update_meteo_data(conn):
    cur = conn.cursor()

    create_table(cur, conn)

    client = MeteoFranceClient()

    for city in cities:
        try:
            list_places = client.search_places(city)
            my_place = list_places[0]
            data = client.get_forecast_for_place(my_place)

            my_place_daily_forecast = data.daily_forecast
            if data.position.get('rain_product_available'):
                if my_place.admin2 and len(my_place.admin2) < 3:
                    my_place_weather_alerts = client.get_warning_current_phenomenoms(
                        my_place.admin2
                    )
                    readable_warnings = readeable_phenomenoms_dict(
                            my_place_weather_alerts.phenomenons_max_colors
                    )
                else:
                    readable_warnings = {}

                my_place_rain_forecast = client.get_rain(my_place.latitude, my_place.longitude)
                next_rain_dt = my_place_rain_forecast.next_rain_date_locale()
                if not next_rain_dt:
                    rain_status = "No rain expected in the following hour."
                else:
                    rain_status = next_rain_dt.strftime("%H:%M")

                for forecast in my_place_daily_forecast:
                    try:
                        insert_meteo_data(conn, cur, city, data.position['lat'], data.position['lon'], forecast['dt'], forecast['T']['min'], forecast['T']['max'], forecast['humidity']['min'], forecast['humidity']['max'], forecast['precipitation']['24h'], forecast['sun']['rise'], forecast['sun']['set'], forecast['weather12H']['desc'], forecast['weather12H']['icon'], rain_status, readable_warnings)
                        print(f"Données météorologiques pour {city} insérées avec succès.")
                    except Exception as e:
                        print(f"Erreur lors de l'insertion des données météorologiques pour {city}: {e}")
        except Exception as e:
            print(f"Erreur lors de la récupération des données météorologiques pour {city}: {e}")
            continue
    
    conn.commit()
    cur.close()
