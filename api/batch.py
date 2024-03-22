import schedule
from cities import cities
import time
import json
from pprint import pprint
from meteofrance_api import MeteoFranceClient
from meteofrance_api.helpers import readeable_phenomenoms_dict
from database import create_conn


client = MeteoFranceClient()

conn = create_conn() 
cur = conn.cursor()


cur.execute(
    """
    CREATE TABLE IF NOT EXISTS meteo_france (
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
    """
)

def update_weather_data():
    for c in cities:
        list_places = client.search_places(c)
        my_place = list_places[0]
        my_place_weather_forecast = client.get_forecast_for_place(my_place)

        my_place_daily_forecast = my_place_weather_forecast.daily_forecast

        for day in my_place_daily_forecast:
            if len(my_place_weather_forecast.position["dept"]) == 3:
                rain_status = "No rain forecast available."
                readable_warnings = {'result': "No weather alerts available."}
                weather_desc = "No weather description available."
                weather_icon = "No weather icon available."

                cur.execute(
                    """
                    INSERT INTO meteo_france (city, latitude, longitude, date,
                                            tmin, tmax, hmin, hmax, precipitation, sunrise, sunset,
                                            weather_desc, weather_icon, rain_status, readable_warnings)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        my_place.name,
                        my_place_weather_forecast.position['lat'],
                        my_place_weather_forecast.position['lon'],
                        day['dt'],
                        day['T']['min'],
                        day['T']['max'],
                        day['humidity']['min'],
                        day['humidity']['max'],
                        day['precipitation']['24h'],
                        day['sun']['rise'],
                        day['sun']['set'],
                        weather_desc,
                        weather_icon,
                        rain_status,
                        json.dumps(readable_warnings),
                    ),
                )

            elif my_place_weather_forecast.position["rain_product_available"] == 1:
                if day['weather12H'] is not None:
                    weather_desc = day['weather12H']['desc']
                    weather_icon = day['weather12H']['icon']
                else:
                    weather_desc = "No weather description available."
                    weather_icon = "No weather icon available."

                
                if my_place.admin2 and len(my_place.admin2) < 3:
                    my_place_weather_alerts = client.get_warning_current_phenomenoms(
                        my_place.admin2
                    )
                    readable_warnings = readeable_phenomenoms_dict(
                        my_place_weather_alerts.phenomenons_max_colors
                    )

                my_place_rain_forecast = client.get_rain(
                    my_place.latitude, my_place.longitude)
                next_rain_dt = my_place_rain_forecast.next_rain_date_locale()

                if not next_rain_dt:
                    rain_status = "No rain expected in the following hour."

                    cur.execute(
                        """
                        INSERT INTO meteo_france (city, latitude, longitude, date,
                                                tmin, tmax, hmin, hmax, precipitation, sunrise, sunset,
                                                weather_desc, weather_icon, rain_status, readable_warnings)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """,
                        (
                            my_place.name,
                            my_place_weather_forecast.position['lat'],
                            my_place_weather_forecast.position['lon'],
                            day['dt'],
                            day['T']['min'],
                            day['T']['max'],
                            day['humidity']['min'],
                            day['humidity']['max'],
                            day['precipitation']['24h'],
                            day['sun']['rise'],
                            day['sun']['set'],
                            weather_desc,
                            weather_icon,
                            rain_status,
                            json.dumps(readable_warnings),
                        ),
                    )

                else:
                    rain_status = next_rain_dt.strftime("%H:%M")

                    cur.execute(
                        """
                        INSERT INTO meteo_france (city, latitude, longitude, date,
                                                tmin, tmax, hmin, hmax, precipitation, sunrise, sunset,
                                                weather_desc, weather_icon, rain_status, readable_warnings)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """,
                        (
                            my_place.name,
                            my_place_weather_forecast.position['lat'],
                            my_place_weather_forecast.position['lon'],
                            day['dt'],
                            day['T']['min'],
                            day['T']['max'],
                            day['humidity']['min'],
                            day['humidity']['max'],
                            day['precipitation']['24h'],
                            day['sun']['rise'],
                            day['sun']['set'],
                            weather_desc,
                            weather_icon,
                            rain_status,
                            json.dumps(readable_warnings),
                        ),
                    )

            else:
                if day['weather12H'] is not None:
                    weather_desc = day['weather12H']['desc']
                    weather_icon = day['weather12H']['icon']
                else:
                    weather_desc = "No weather description available."
                    weather_icon = "No weather icon available."
                rain_status = "No rain forecast available."

                if my_place.admin2 and len(my_place.admin2) < 3:
                    my_place_weather_alerts = client.get_warning_current_phenomenoms(
                        my_place.admin2
                    )
                    readable_warnings = readeable_phenomenoms_dict(
                        my_place_weather_alerts.phenomenons_max_colors
                    )

                cur.execute(
                    """
                    INSERT INTO meteo_france (city, latitude, longitude, date,
                                            tmin, tmax, hmin, hmax, precipitation, sunrise, sunset,
                                            weather_desc, weather_icon, rain_status, readable_warnings)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        my_place.name,
                        my_place_weather_forecast.position['lat'],
                        my_place_weather_forecast.position['lon'],
                        day['dt'],
                        day['T']['min'],
                        day['T']['max'],
                        day['humidity']['min'],
                        day['humidity']['max'],
                        day['precipitation']['24h'],
                        day['sun']['rise'],
                        day['sun']['set'],
                        weather_desc,
                        weather_icon,
                        rain_status,
                        json.dumps(readable_warnings),
                    ),
                )

    conn.commit()

    print("Weather data updated successfully!")

cur.close()

conn.close()

schedule.every(1).hours.do(update_weather_data)
while True:
    schedule.run_pending()
    time.sleep(1)