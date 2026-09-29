import requests
import json
from google import genai
from dotenv import load_dotenv
import os


# Load Gemini API key
load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


# --------------------------------------------------
# 1. GET LOCATION
# --------------------------------------------------

place = input("📍 Enter your village/town/city: ")
crop = input("🌾 Enter your crop: ")

print("\n🔎 Finding location...")

geocode_url = "https://geocoding-api.open-meteo.com/v1/search"

geocode_params = {
    "name": place,
    "count": 1,
    "language": "en",
    "format": "json"
}

geocode_response = requests.get(
    geocode_url,
    params=geocode_params
)

geocode_data = geocode_response.json()

if "results" not in geocode_data:
    print("❌ Location not found.")
    exit()

location = geocode_data["results"][0]

location_name = location.get("name", place)
state = location.get("admin1", "")
country = location.get("country", "")

latitude = location["latitude"]
longitude = location["longitude"]


print("\n📍 Location found:")
print(location_name)
print(state)
print(country)
print("Latitude:", latitude)
print("Longitude:", longitude)


# --------------------------------------------------
# 2. GET WEATHER
# --------------------------------------------------

print("\n🌦️ Getting weather data...")

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

weather_data = weather_response.json()

current = weather_data.get("current", {})
daily = weather_data.get("daily", {})


# --------------------------------------------------
# 3. GET SOIL INFORMATION
# --------------------------------------------------

# --------------------------------------------------
# LOAD SOIL HEALTH CARD DATA
# --------------------------------------------------

print("\n🧪 Loading Soil Health Card data...")

soil_card_file = "soil_card_data.json"

if not os.path.exists(soil_card_file):
    print("❌ Soil Health Card data not found.")
    print("Please run soil_card.py first.")
    exit()

try:
    with open(soil_card_file, "r", encoding="utf-8") as file:
        soil_card = json.load(file)

except Exception as e:
    print("❌ Could not read Soil Health Card data.")
    print(e)
    exit()


# Extract soil parameters

parameters = soil_card.get("soil_parameters", {})

soil_data = {
    "ph": parameters.get("ph"),
    "electrical_conductivity": parameters.get(
        "electrical_conductivity"
    ),
    "organic_carbon": parameters.get(
        "organic_carbon"
    ),
    "nitrogen": parameters.get("nitrogen"),
    "phosphorus": parameters.get("phosphorus"),
    "potassium": parameters.get("potassium"),
    "sulphur": parameters.get("sulphur"),
    "zinc": parameters.get("zinc"),
    "iron": parameters.get("iron"),
    "manganese": parameters.get("manganese"),
    "copper": parameters.get("copper"),
    "boron": parameters.get("boron")
}


print("\n🧪 SOIL HEALTH CARD DATA")
print("========================")

print(
    json.dumps(
        soil_data,
        indent=2,
        ensure_ascii=False
    )
)

# --------------------------------------------------
# 4. CREATE COMMON FARM DATA
# --------------------------------------------------

farm_data = {
    "crop": crop,

    "location": {
        "name": location_name,
        "state": state,
        "country": country,
        "latitude": latitude,
        "longitude": longitude
    },

    "weather": {
        "current": {
            "temperature": current.get("temperature_2m"),
            "humidity": current.get("relative_humidity_2m"),
            "precipitation": current.get("precipitation"),
            "rain": current.get("rain"),
            "wind_speed": current.get("wind_speed_10m")
        },

        "forecast": {
            "dates": daily.get("time"),
            "max_temperature": daily.get("temperature_2m_max"),
            "min_temperature": daily.get("temperature_2m_min"),
            "rain_probability": daily.get("precipitation_probability_max"),
            "rainfall": daily.get("precipitation_sum")
        }
    },

    "soil": soil_data,

    "satellite": {
        "source": "ISRO_Bhuvan",
        "surface_soil_moisture": {
            "status": "not_connected",
            "product": "Surface Soil Moisture - 2 Day",
            "resolution": "0.25 x 0.25 degree",
            "unit": "m3/m3"
        },
        "vegetation_condition": {
            "status": "planned"
        }
    }
}


print("\n📊 FARM DATA COLLECTED")
print("======================")

print(json.dumps(
    farm_data,
    indent=2,
    ensure_ascii=False
))


# --------------------------------------------------
# 5. SEND EVERYTHING TO GEMINI
# --------------------------------------------------

print("\n🤖 Sending farm data to Gemini AI...")


prompt = f"""
You are an agricultural advisory AI for small and marginal farmers.

Analyze the following farm information:

{json.dumps(farm_data, indent=2, ensure_ascii=False)}

Use ONLY the information provided above.

Consider:

1. Crop condition based on the supplied weather and soil information.
2. Weather-related risks.
3. Soil-related observations.
4. Satellite-data status and its potential relevance.
5. Irrigation considerations.
6. General farm actions.
7. Important warnings for the farmer.

IMPORTANT:
The satellite section currently contains metadata only.
Do NOT invent satellite measurements.

If satellite measurements are unavailable, clearly state that
satellite observations are not currently available.

Do not provide pesticide dosage, fertilizer dosage,
or chemical application rates.

Use simple language that a farmer can understand.

Return ONLY valid JSON in exactly this structure:

{{
    "crop": "...",
    "overall_risk": "low, medium, or high",
    "weather_observation": "...",
    "soil_observation": "...",
    "satellite_observation": "...",
    "irrigation_advice": "...",
    "farm_actions": [
        "...",
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

    result = json.loads(response.text)

except json.JSONDecodeError:

    print("\n❌ Gemini returned an invalid JSON response.")
    print(response.text)
    exit()

except Exception as e:

    print("\n❌ Gemini error:")
    print(e)
    exit()


# --------------------------------------------------
# 6. DISPLAY FINAL ADVISORY
# --------------------------------------------------

print("\n")
print("🌾 KISAN ALERT — COMBINED FARM ADVISORY")
print("========================================")

print(json.dumps(
    result,
    indent=2,
    ensure_ascii=False
))