import requests
import json


# ---------------------------------------------------------
# 1. Get farm location
# ---------------------------------------------------------

place = input("📍 Enter your village/town/city: ").strip()

if not place:
    print("❌ Please enter a location.")
    exit()


print("\n🔎 Finding location...")

geocode_url = "https://geocoding-api.open-meteo.com/v1/search"

geocode_params = {
    "name": place,
    "count": 1,
    "language": "en",
    "format": "json"
}

try:
    response = requests.get(
        geocode_url,
        params=geocode_params,
        timeout=10
    )

    response.raise_for_status()
    data = response.json()

except requests.RequestException as e:
    print("❌ Location service error:")
    print(e)
    exit()


if "results" not in data or not data["results"]:
    print("❌ Location not found.")
    exit()


location = data["results"][0]

location_name = location.get("name", place)
state = location.get("admin1", "")
country = location.get("country", "")

latitude = location["latitude"]
longitude = location["longitude"]


# ---------------------------------------------------------
# 2. Display farm coordinates
# ---------------------------------------------------------

print("\n📍 FARM LOCATION")
print("================")
print("Place:", location_name)
print("State:", state)
print("Country:", country)
print("Latitude:", latitude)
print("Longitude:", longitude)


# ---------------------------------------------------------
# 3. Satellite data adapter
# ---------------------------------------------------------
#
# IMPORTANT:
# Bhuvan currently provides the Surface Soil Moisture -
# 2 Day product, but the public Bhuvan API documentation
# does not provide a simple coordinate-based endpoint that
# we can safely call here.
#
# Therefore we store the official product metadata and
# leave the measurement as unavailable until a valid
# data-access endpoint is connected.
#
# We NEVER invent a satellite measurement.
# ---------------------------------------------------------

satellite_data = {

    "source": {
        "name": "ISRO / Bhuvan",
        "provider": "ISRO / NRSC",
        "status": "catalog_available_data_access_pending"
    },

    "location": {
        "name": location_name,
        "state": state,
        "country": country,
        "latitude": latitude,
        "longitude": longitude
    },

    "products": {

        "surface_soil_moisture": {

            "product": "Surface Soil Moisture - 2 Day",

            "status": "data_access_pending",

            "coverage": "India",

            "frequency": "2 days",

            "resolution": "0.25 x 0.25 degree",

            "unit": "m3/m3",

            "value": None,

            "observation_date": None,

            "source_note": (
                "Official Bhuvan/ISRO product identified. "
                "A direct coordinate-level data access "
                "endpoint is not connected yet."
            )
        },

        "vegetation_condition": {

            "status": "planned",

            "value": None,

            "observation_date": None
        }
    }
}


# ---------------------------------------------------------
# 4. Display satellite layer
# ---------------------------------------------------------

print("\n🛰️ KISAN ALERT — SATELLITE LAYER")
print("=================================")

print(
    json.dumps(
        satellite_data,
        indent=2,
        ensure_ascii=False
    )
)


# ---------------------------------------------------------
# 5. Data-integrity status
# ---------------------------------------------------------

print("\n⚠️ SATELLITE DATA STATUS")
print("------------------------")

print("Source: ISRO / Bhuvan")
print("Product: Surface Soil Moisture - 2 Day")
print("Coverage: India")
print("Resolution: 0.25 x 0.25 degree")
print("Frequency: 2 days")
print("Actual measurement: Not connected")


print("\n🔒 DATA INTEGRITY")
print("-----------------")
print("Kisan Alert will NOT invent satellite measurements.")


# ---------------------------------------------------------
# 6. Adapter status
# ---------------------------------------------------------

print("\n✅ SATELLITE ADAPTER STATUS")
print("---------------------------")
print("Location integration: READY")
print("Bhuvan product mapping: READY")
print("Satellite measurement access: PENDING")
print("AI integration: READY")