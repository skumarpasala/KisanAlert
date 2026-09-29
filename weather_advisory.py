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
# Farmer information
# --------------------------------

crop = "Tomato"

location_name = "Visakhapatnam"

latitude = 17.6868
longitude = 83.2185


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

if response.status_code != 200:

    print("❌ Weather API error")
    print(response.text)
    exit()


weather = response.json()

current = weather["current"]
daily = weather["daily"]


# --------------------------------
# Prepare weather information
# --------------------------------

weather_information = f"""
Location: {location_name}

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
# Ask Gemini
# --------------------------------

prompt = f"""
You are Kisan Alert, an agricultural AI assistant
helping small and marginal farmers in India.

Farmer location:
{location_name}

Crop:
{crop}

Weather information:
{weather_information}

Based ONLY on the crop and weather information provided,
generate a simple agricultural advisory.

Consider:
- irrigation
- rainfall
- humidity
- possible weather-related crop risks
- actions the farmer can take

Return ONLY valid JSON in this structure:

{{
    "crop": "{crop}",
    "location": "{location_name}",
    "weather_risk": "low, medium, or high",
    "advisory": [
        "advisory step 1",
        "advisory step 2"
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
# Parse AI response
# --------------------------------

try:

    advisory = json.loads(response.text)

except json.JSONDecodeError:

    print("❌ Gemini returned invalid JSON")
    print(response.text)
    exit()


# --------------------------------
# Display result
# --------------------------------

print("\n🌾 KISAN ALERT WEATHER ADVISORY")
print("================================")

print(
    json.dumps(
        advisory,
        ensure_ascii=False,
        indent=2
    )
)