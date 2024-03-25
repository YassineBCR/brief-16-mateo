import psycopg2
from config import dbname,user,port,password,host
from meteofrance_api import MeteoFranceClient
from meteofrance_api.helpers import readeable_phenomenoms_dict
from cities import cities
from pprint import pprint
import json

# Créer une connexion à la base de données
conn = psycopg2.connect(
    dbname=dbname, user=user, password=password, host=host, port=port
)
cur = conn.cursor()

# Créer la table "meteo_data" si elle n'existe pas
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
        readable_warnings JSON
    )
""")

# Créer une instance du client MeteoFranceClient
client = MeteoFranceClient()
  # Check if rain status, weather and warnings are available

for city in cities:
    try:
        list_places = client.search_places(city)
        my_place = list_places[0]
        data = client.get_forecast_for_place(my_place)
        print (data.position)
        my_place_daily_forcast = data.daily_forecast
        if data.position.get('rain_product_available'):
        # Fetch weather alerts
            if my_place.admin2 and len(my_place.admin2) < 3:
                my_place_weather_alerts = client.get_warning_current_phenomenoms(
                    my_place.admin2
                    )
                readable_warnings = readeable_phenomenoms_dict(
                        my_place_weather_alerts.phenomenons_max_colors
                )
            readable_warnings =  {}
        my_place_rain_forecast = client.get_rain(my_place.latitude, my_place.longitude)
        next_rain_dt = my_place_rain_forecast.next_rain_date_locale()
        if not next_rain_dt:
            rain_status = "No rain expected in the following hour."
        else :
            rain_status = next_rain_dt.strftime("%H:%M")
        for forecast in my_place_daily_forcast:
            pprint(rain_status)
            cur.execute("""
                INSERT INTO meteo_data (
                    city, latitude, longitude, date, tmin, tmax, hmin, hmax,
                    precipitation, sunrise, sunset, weather_desc, weather_icon,
                    rain_status, readable_warnings
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                city,
                data.position['lat'],
                data.position['lon'],
                forecast['dt'],
                forecast['T']['min'],
                forecast['T']['max'],
                forecast['humidity']['min'],
                forecast['humidity']['max'],
                forecast['precipitation']['24h'],
                forecast['sun']['rise'],
                forecast['sun']['set'],
                forecast['weather12H']['desc'],
                forecast['weather12H']['icon'],
                rain_status,
                json.dumps(readable_warnings)
            ))
            conn.commit()
            print(f"Données météorologiques pour {city} insérées avec succès.")
    except Exception as e:
            print(f"Erreur lors de la récupération des données météorologiques pour {city}: {e}")
            exit(0)

# Fermer la connexion à la base de données
cur.close()
conn.close()