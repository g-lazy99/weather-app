# backend/main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI()

# Настройка CORS для работы с Expo
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class WeatherRequest(BaseModel):
    city: str


WEATHERAPI_KEY = os.getenv("WEATHERAPI_KEY")


@app.post("/forecast")
async def get_forecast(request: WeatherRequest):
    if not WEATHERAPI_KEY:
        raise HTTPException(status_code=500, detail="API ключ не найден")

    url = "http://api.weatherapi.com/v1/forecast.json"
    params = {
        "key": WEATHERAPI_KEY,
        "q": request.city,
        "days": 7,
        "lang": "ru",
        # Убираем параметр hour или ставим hour=24
    }

    response = requests.get(url, params=params)
    if response.status_code != 200:
        raise HTTPException(status_code=400, detail="Город не найден")

    data = response.json()
    return {
        "city": data["location"]["name"],
        "forecast": [
            {
                "date": day["date"],
                "temperature": day["day"]["avgtemp_c"],
                "description": day["day"]["condition"]["text"],
                "icon": f"https:{day['day']['condition']['icon']}",
                "details": {
                    "humidity": day["day"]["avghumidity"],
                    "wind_speed": day["day"]["maxwind_kph"],
                    "uv_index": day["day"]["uv"],
                    "sunrise": day["astro"]["sunrise"],
                    "sunset": day["astro"]["sunset"],
                    "hourly": [
                        {
                            "time": hour["time"],
                            "temperature": hour["temp_c"],
                            "description": hour["condition"]["text"],
                            "icon": f"https:{hour['condition']['icon']}"
                        }
                        for hour in day["hour"] if
                        hour["time"].endswith("00:00") or hour["time"].endswith("06:00") or hour["time"].endswith(
                            "12:00") or hour["time"].endswith("18:00")
                    ]
                }
            }
            for day in data["forecast"]["forecastday"]
        ]
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
