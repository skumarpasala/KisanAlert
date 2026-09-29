import requests


# --------------------------------
# Location
# --------------------------------

latitude = 17.6868
longitude = 83.2185

location_name = "Visakhapatnam"


# --------------------------------
# Get weather
# --------------------------------

url = "https://api.open-meteo.com/v1/forecast"

params = {
    "latitude": latitude,
    "longitude": longitude,
    "current": "temperature_2m,relative_humidity_2m,precipitation,rain,wind_speed_10m",
    "daily": "temperature_2m_max,temperature_2m_min,precipitation_probability_max,precipitation_sum",
    "timezone": "auto",
    "forecast_days": 3
}


response = requests.get(
    url,
    params=params
)


# --------------------------------
# Check response
# --------------------------------

if response.status_code != 200:

    print("❌ Weather API error")
    print(response.text)
    exit()


weather = response.json()


# --------------------------------
# Display weather
# --------------------------------

current = weather["current"]
daily = weather["daily"]


print("🌦️ KISAN ALERT WEATHER")
print("======================")

print("📍 Location:", location_name)

print(
    "🌡️ Temperature:",
    current["temperature_2m"],
    "°C"
)

print(
    "💧 Humidity:",
    current["relative_humidity_2m"],
    "%"
)

print(
    "🌧️ Rain:",
    current["rain"],
    "mm"
)

print(
    "💨 Wind:",
    current["wind_speed_10m"],
    "km/h"
)


print("\n📅 NEXT 3 DAYS")

for i in range(3):

    print(
        daily["time"][i],
        "| Max:",
        daily["temperature_2m_max"][i],
        "°C",
        "| Rain probability:",
        daily["precipitation_probability_max"][i],
        "%",
        "| Rain:",
        daily["precipitation_sum"][i],
        "mm"
    )