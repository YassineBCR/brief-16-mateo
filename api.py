from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from NLP import generate_weather_report
from TTS import create_audio_file

app = FastAPI()


@app.get("/weather_report/{city}")
async def get_weather_report(city: str):
    weather_report = generate_weather_report(city)
    if weather_report.startswith("Erreur") or weather_report.startswith(
        "Je n'ai pas trouvé"
    ):
        raise HTTPException(status_code=500, detail=weather_report)
    else:
        audio_data = create_audio_file(weather_report)  # Convertissez le texte en audio
        # Écrivez le contenu du fichier audio dans un fichier local
        with open("audio.mp3", "wb") as f:
            f.write(audio_data)
        return StreamingResponse(open("audio.mp3", "rb"), media_type="audio/mpeg")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
