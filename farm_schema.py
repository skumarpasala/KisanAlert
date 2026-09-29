import json
from datetime import datetime


def create_farm_profile(
    crop,
    location,
    soil,
    weather,
    satellite,
    language
):
    """
    Common Kisan Alert data model.

    Data from different states and different sources
    can be converted into this same structure.
    """

    farm_profile = {
        "schema_version": "1.0",

        "farmer": {
            "id": None
        },

        "location": {
            "name": location.get("name"),
            "state": location.get("state"),
            "country": location.get("country"),
            "latitude": location.get("latitude"),
            "longitude": location.get("longitude")
        },

        "crop": {
            "name": crop
        },

        "soil": soil,

        "weather": weather,

        "satellite": satellite,

        "language": {
            "code": language.get("code"),
            "name": language.get("name"),
            "source": language.get("source")
        },

        "metadata": {
            "created_at": datetime.now().isoformat(),
            "data_sources": [
                "Soil Health Card",
                "Open-Meteo",
                "ISRO / Bhuvan adapter"
            ]
        }
    }

    return farm_profile


# ---------------------------------------------------------
# DEMO DATA
# ---------------------------------------------------------

location = {
    "name": "Warangal",
    "state": "Telangana",
    "country": "India",
    "latitude": 18.0,
    "longitude": 79.58333
}

crop = "Cotton"


soil = {
    "source": "Soil Health Card",
    "parameters": {
        "ph": {
            "value": 6.5,
            "unit": "-"
        },
        "nitrogen": {
            "value": 280,
            "unit": "kg/ha"
        },
        "phosphorus": {
            "value": 12.5,
            "unit": "kg/ha"
        },
        "potassium": {
            "value": 325,
            "unit": "kg/ha"
        },
        "organic_carbon": {
            "value": 0.58,
            "unit": "%"
        }
    }
}


weather = {
    "source": "Open-Meteo",
    "status": "available"
}


satellite = {
    "source": {
        "name": "ISRO / Bhuvan",
        "status": "not_connected"
    },

    "surface_soil_moisture": {
        "product": "Surface Soil Moisture - 2 Day",
        "status": "not_connected",
        "value": None,
        "unit": "m3/m3"
    },

    "vegetation_condition": {
        "status": "planned",
        "value": None
    }
}


language = {
    "code": "te",
    "name": "Telugu",
    "source": "state_default"
}


# ---------------------------------------------------------
# CREATE COMMON FARM PROFILE
# ---------------------------------------------------------

farm_profile = create_farm_profile(
    crop=crop,
    location=location,
    soil=soil,
    weather=weather,
    satellite=satellite,
    language=language
)


print("\n🌾 KISAN ALERT — COMMON FARM DATA MODEL")
print("========================================")

print(
    json.dumps(
        farm_profile,
        indent=2,
        ensure_ascii=False
    )
)