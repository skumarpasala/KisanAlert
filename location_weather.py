import requests
from google import genai
from dotenv import load_dotenv
import os
import json

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


# --------------------------------
# STEP 1: Farmer information
# --------------------------------

place = input("📍 Enter your village/town/city: ")
crop = input("🌱 Enter your crop: ")


# --------------------------------
# STEP 2: Convert location
# to coordinates
# --------------------------------

geocoding_url = "https://geocoding-api.open-meteo.com/v1/search"

geocoding_params = {
    "name": place,
    "count": 1,
    "language": "en",
    "format": "json"
}

location_response = requests.get(
    geocoding_url,
    params=geocoding_params
)

if location_response.status_code != 200:
    print("❌ Location lookup failed")
    exit()


location_data = location_response.json()

if "results" not in location_data or not location_data["results"]:
    print("❌ Location not found")
    exit()


location = location_data["results"][0]

location_name = location.get("name")
state = location.get("admin1")
country = location.get("country")

latitude = location.get("latitude")
longitude = location.get("longitude")


print("\n📍 Location found:")
print(location_name)
print(state)
print(country)

print("Latitude:", latitude)
print("Longitude:", longitude)


# --------------------------------
# STEP 3: Get weather
# --------------------------------

weather_url = "https://api.open-meteo.com/v1/forecast"

weather_params = {
    "latitude": latitude,
    "longitude": longitude,
    "current": "temperature_2m,relative_humidity_2m,precipitation,rain,wind_speed_10m",
    "daily": "temperature_2m_max,temperature_2m_min,precipitation_probability_max,precipitation_sum",
    "timezone": "auto",
    "forecast_days": 3
}

weather_response = requests.get(
    weather_url,
    params=weather_params
)

if weather_response.status_code != 200:
    print("❌ Weather API error")
    print(weather_response.text)
    exit()


weather = weather_response.json()

current = weather["current"]
daily = weather["daily"]


# --------------------------------
# STEP 4: Prepare weather data
# --------------------------------

weather_information = f"""
Location: {location_name}
State: {state}
Country: {country}

Current temperature:
{current["temperature_2m"]} °C

Current humidity:
{current["relative_humidity_2m"]} %

Current rain:
{current["rain"]} mm

Wind speed:
{current["wind_speed_10m"]} km/h

3-day forecast:
"""

for i in range(3):

    weather_information += f"""
Date: {daily["time"][i]}
Maximum temperature: {daily["temperature_2m_max"][i]} °C
Minimum temperature: {daily["temperature_2m_min"][i]} °C
Rain probability: {daily["precipitation_probability_max"][i]} %
Expected rainfall: {daily["precipitation_sum"][i]} mm
"""


# --------------------------------
# STEP 5: Ask Gemini
# --------------------------------

prompt = f"""
You are Kisan Alert, an agricultural AI assistant
helping small and marginal farmers in India.

Farmer location:
{location_name}, {state}, {country}

Crop:
{crop}

Weather information:
{weather_information}

Generate a simple agricultural advisory based ONLY
on the crop and weather information provided.

Consider:
- irrigation
- rainfall
- temperature
- humidity
- weather-related crop risks
- practical actions the farmer can take

Return ONLY valid JSON in exactly this structure:

{{
    "crop": "{crop}",
    "location": "{location_name}",
    "weather_risk": "low, medium, or high",
    "advisory": [
        "advisory step 1",
        "advisory step 2",
        "advisory step 3"
    ],
    "irrigation_advice": "simple irrigation advice",
    "risk_warning": "important weather-related warning"
}}

Use simple language suitable for an Indian farmer.

Do not invent weather values.

Do not provide pesticide dosage or chemical application rates.

Do not include markdown.
Do not include ```json.
Do not add text outside the JSON.
"""


response = client.models.generate_content(
    model="gemini-3.5-flash-lite",
    contents=prompt
)


# --------------------------------
# STEP 6: Parse AI response
# --------------------------------

try:

    advisory = json.loads(response.text)

except json.JSONDecodeError:

    print("\n❌ Gemini returned invalid JSON")
    print(response.text)
    exit()


# --------------------------------
# STEP 7: Display final advisory
# --------------------------------

print("\n🌾 KISAN ALERT LOCALIZED ADVISORY")
print("=================================")

print(
    json.dumps(
        advisory,
        ensure_ascii=False,
        indent=2
    )
)