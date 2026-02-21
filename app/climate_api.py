import requests

API_KEY = "51b36670957d42ff1d1b0388dc823564"
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

def get_climate(city: str):
    params = {
        "q": city,
        "appid": API_KEY,
        "units": "metric"
    }

    response = requests.get(BASE_URL, params=params)
    data = response.json()

    print("FULL API RESPONSE:", data)   # 👈 ADD THIS LINE

    if response.status_code != 200:
        return {"error": data}

    return {
        "city": data.get("name"),
        "temperature": data["main"]["temp"],
        "humidity": data["main"]["humidity"],
        "weather": data["weather"][0]["description"]
    }