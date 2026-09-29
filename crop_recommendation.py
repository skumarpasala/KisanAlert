import requests
import json
import os

from google import genai
from dotenv import load_dotenv


# --------------------------------------------------
# SETUP
# --------------------------------------------------

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


# --------------------------------------------------
# FARM INPUT
# --------------------------------------------------

place = input("📍 Enter your village/town/city: ").strip()
current_crop = input("🌱 Enter current crop: ").strip()


# --------------------------------------------------
# LOCATION
# --------------------------------------------------

print("\n🔎 Finding location...")

geocode_url = "https://geocoding-api.open-meteo.com/v1/search"

geocode_params = {
    "name": place,
    "count": 1,
    "language": "en",
    "format": "json"
}

response = requests.get(
    geocode_url,
    params=geocode_params,
    timeout=10
)

location_data = response.json()

if "results" not in location_data:
    print("❌ Location not found.")
    exit()

location = location_data["results"][0]

location_name = location.get("name", place)
state = location.get("admin1", "")
country = location.get("country", "")

latitude = location["latitude"]
longitude = location["longitude"]


# --------------------------------------------------
# WEATHER
# --------------------------------------------------

print("🌦️ Getting weather data...")

weather_url = "https://api.open-meteo.com/v1/forecast"

weather_params = {
    "latitude": latitude,
    "longitude": longitude,
    "current": (
        "temperature_2m,"
        "relative_humidity_2m,"
        "precipitation,"
        "rain,"
        "wind_speed_10m"
    ),
    "daily": (
        "temperature_2m_max,"
        "temperature_2m_min,"
        "precipitation_probability_max,"
        "precipitation_sum"
    ),
    "timezone": "auto",
    "forecast_days": 3
}

weather_response = requests.get(
    weather_url,
    params=weather_params,
    timeout=10
)

weather_data = weather_response.json()

current_weather = weather_data.get("current", {})
daily_weather = weather_data.get("daily", {})


# --------------------------------------------------
# LOAD SOIL HEALTH CARD
# --------------------------------------------------

print("🧪 Loading Soil Health Card...")

soil_card_file = "soil_card_data.json"

if not os.path.exists(soil_card_file):
    print("❌ soil_card_data.json not found.")
    print("Please run soil_card.py first.")
    exit()

with open(
    soil_card_file,
    "r",
    encoding="utf-8"
) as file:

    soil_card = json.load(file)


soil_parameters = soil_card.get(
    "soil_parameters",
    {}
)


# --------------------------------------------------
# FARM DATA
# --------------------------------------------------

farm_data = {

    "current_crop": current_crop,

    "location": {
        "name": location_name,
        "state": state,
        "country": country,
        "latitude": latitude,
        "longitude": longitude
    },

    "weather": {

        "current": {
            "temperature": current_weather.get(
                "temperature_2m"
            ),
            "humidity": current_weather.get(
                "relative_humidity_2m"
            ),
            "rain": current_weather.get(
                "rain"
            ),
            "wind_speed": current_weather.get(
                "wind_speed_10m"
            )
        },

        "forecast": {
            "dates": daily_weather.get(
                "time"
            ),
            "max_temperature": daily_weather.get(
                "temperature_2m_max"
            ),
            "min_temperature": daily_weather.get(
                "temperature_2m_min"
            ),
            "rain_probability": daily_weather.get(
                "precipitation_probability_max"
            ),
            "rainfall": daily_weather.get(
                "precipitation_sum"
            )
        }
    },

    "soil": soil_parameters,

    "satellite": {
        "source": "ISRO_Bhuvan",
        "surface_soil_moisture": {
            "status": "not_connected"
        },
        "vegetation_condition": {
            "status": "planned"
        }
    }
}


# --------------------------------------------------
# DISPLAY FARM DATA
# --------------------------------------------------

print("\n🌾 FARM INFORMATION")
print("===================")

print(
    json.dumps(
        farm_data,
        indent=2,
        ensure_ascii=False
    )
)


# --------------------------------------------------
# AI RECOMMENDATION
# --------------------------------------------------

print("\n🤖 Generating crop recommendations...")


prompt = f"""
You are Kisan Alert, an agricultural decision-support AI.

Analyze the following farm information:

{json.dumps(
    farm_data,
    indent=2,
    ensure_ascii=False
)}

Your task is to provide:

1. Whether the current crop is reasonably suitable
   for the supplied conditions.

2. Alternative crop options that may be considered
   based ONLY on the supplied soil, weather and location.

3. Regenerative agriculture practices that can improve
   long-term soil health.

4. Crop rotation or diversification suggestions.

5. Important risks or uncertainties.

IMPORTANT RULES:

- Use only the supplied information.
- Do not invent soil measurements.
- Do not invent satellite measurements.
- Satellite observations are currently unavailable.
- Do not claim that satellite data was used.
- Do not provide fertilizer dosage.
- Do not provide pesticide dosage.
- Do not provide chemical application rates.
- Do not claim a crop is guaranteed to produce higher yield.
- Clearly mention uncertainty when information is insufficient.
- Recommendations should be understandable to farmers.
- Prefer soil-health practices such as crop rotation,
  residue management, organic matter improvement,
  cover crops, reduced soil disturbance and biodiversity
  where appropriate.
- Do not recommend practices that clearly conflict
  with the supplied farm conditions.

Return ONLY valid JSON.

Use exactly this structure:

{{
    "current_crop": "...",

    "current_crop_assessment": "...",

    "alternative_crops": [
        {{
            "crop": "...",
            "reason": "...",
            "confidence": "low, medium, or high"
        }},
        {{
            "crop": "...",
            "reason": "...",
            "confidence": "low, medium, or high"
        }}
    ],

    "regenerative_practices": [
        "...",
        "...",
        "..."
    ],

    "crop_rotation": [
        "...",
        "..."
    ],

    "warnings": [
        "...",
        "..."
    ]
}}
"""


try:

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt
    )

except Exception as e:

    print("\n❌ Gemini error:")
    print(e)
    exit()


# --------------------------------------------------
# PARSE RESPONSE
# --------------------------------------------------

try:

    raw_response = response.text.strip()

    if raw_response.startswith("```json"):
        raw_response = raw_response[7:]

    elif raw_response.startswith("```"):
        raw_response = raw_response[3:]

    if raw_response.endswith("```"):
        raw_response = raw_response[:-3]

    raw_response = raw_response.strip()

    result = json.loads(raw_response)

except json.JSONDecodeError:

    print("\n❌ Gemini returned invalid JSON.")
    print("\nRAW RESPONSE:")
    print(response.text)
    exit()


# --------------------------------------------------
# DISPLAY RESULT
# --------------------------------------------------

print("\n")
print("🌱 KISAN ALERT — CROP & REGENERATIVE ADVISORY")
print("=============================================")

print(
    json.dumps(
        result,
        indent=2,
        ensure_ascii=False
    )
)