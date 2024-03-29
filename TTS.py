import json
import requests
from io import BytesIO
from gtts import gTTS
import base64


def create_audio_file(text):
    headers = {
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNTg1NDFkMzMtMWMzYi00YTA3LWJmYzItY2YyOGY3MTc3OTVkIiwidHlwZSI6ImFwaV90b2tlbiJ9.k4N4GWeW8H0_Th4oE8s2v9QZBvAEswprEWCi4U4XmlE"
    }

    url = "https://api.edenai.run/v2/audio/text_to_speech"
    payload = {
        "providers": "google,amazon",
        "language": "fr-FR",
        "option": "FEMALE",
        "text": text,
        "fallback_providers": "",
    }

    response = requests.post(url, json=payload, headers=headers)

    result = json.loads(response.text)
    audio_url = result["google"]["audio"]
    audio_bytes = base64.b64decode(audio_url)
    # Retournez le contenu du fichier audio pour l'utiliser dans la StreamingResponse
    return audio_bytes
