import json
import requests
from get_weather import get_meteo_data


def generate_weather_report(city):
    meteo_data = get_meteo_data(city)
    if meteo_data:
        temperature_min = meteo_data[5]
        temperature_max = meteo_data[6]
        precipitation = meteo_data[9]
        wind_speed = meteo_data[10]
        wind_direction = meteo_data[11]
        humidity = meteo_data[12]

        prompt = f"Bonjour et bienvenue dans votre bulletin météo. Aujourd'hui à {city}, attendez-vous à une température minimale de {temperature_min}°C et une température maximale de {temperature_max}°C. Des précipitations de {precipitation} sont attendues, avec un vent soufflant à {wind_speed} km/h en direction de {wind_direction}. L'humidité sera de {humidity}%. Planifiez votre journée en conséquence et restez à l'écoute pour plus de mises à jour météo."

        headers = {
            "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNTg1NDFkMzMtMWMzYi00YTA3LWJmYzItY2YyOGY3MTc3OTVkIiwidHlwZSI6ImFwaV90b2tlbiJ9.k4N4GWeW8H0_Th4oE8s2v9QZBvAEswprEWCi4U4XmlE"
        }

        url = "https://api.edenai.run/v2/text/generation"
        payload = {
            "providers": "mistral",
            "text": prompt,
            "temperature": 0.5,
            "max_tokens": 200,
            "fallback_providers": "",
        }

        response = requests.post(url, json=payload, headers=headers)

        result = json.loads(response.text)
        if "mistral" in result:
            generated_text = result["mistral"]["generated_text"]
            return generated_text
        else:
            return "Erreur lors de la génération du texte avec mistral."
    else:
        return f"Je n'ai pas trouvé de données météo pour {city}."
