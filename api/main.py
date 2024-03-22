from fastapi import FastAPI, HTTPException
from database import create_conn
import uvicorn
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Remplacez "*" par l'origine de votre frontend en production
    allow_credentials=True,
    allow_methods=["*"],    
    allow_headers=["*"],
)

@app.get("/weather/{city_name}")
async def get_weather_by_city(city_name: str):
    conn = create_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM weather WHERE city = %s", (city_name,))
    result = cur.fetchone()
    cur.close()
    conn.close()

    if result is None:
        raise HTTPException(status_code=404, detail="City not found")

    return {
        "city": result[1],
        "latitude": result[2],
        "longitude": result[3],
        "date": result[4],
        "tmin": result[5],
        "tmax": result[6],
        "hmin": result[7],
        "hmax": result[8],
        "precipitation": result[9],
        "sunrise": result[10],
        "sunset": result[11],
        "weather_desc": result[12],
        "weather_icon": result[13],
        "rain_status": result[14],
        "readable_warnings": result[15]
    }

if __name__ == '__main__':
    import uvicorn    
    uvicorn.run(app, host='127.0.0.1', port=8010)