from flask import Flask, request, jsonify
from flask_cors import CORS
from google import genai
from dotenv import load_dotenv
import os
import json
import base64
import requests

from farm_schema import create_farm_profile
from soil_interpreter import interpret_soil
from crop_recommender import recommend_crops

from language_config import (
    SUPPORTED_LANGUAGES,
    detect_language_from_state
)

from validation import (
    validate_crop,
    validate_place,
    validate_language
)
from flask import render_template

# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

load_dotenv()

app = Flask(__name__)
CORS(app)
app.json.ensure_ascii = False

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


# --------------------------------------------------
# HOME
# --------------------------------------------------
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/")
def home():
    return "Kisan Alert Backend is Running!"

# --------------------------------------------------
# TEXT CROP DIAGNOSIS
# --------------------------------------------------

@app.route("/diagnose", methods=["POST"])
def diagnose():

    data = request.get_json()

    symptoms = data.get("symptoms", "")

    if not symptoms:
        return jsonify({
            "success": False,
            "error": "Please provide crop symptoms"
        }), 400

    # Language selected by the farmer
    language = data.get("language", "en")

    # Supported languages come from language_config.py
    if language not in SUPPORTED_LANGUAGES:
        return jsonify({
            "success": False,
            "error": "Unsupported language",
            "supported_languages": list(SUPPORTED_LANGUAGES.keys())
        }), 400

    language_name = SUPPORTED_LANGUAGES[language]["name"]

    prompt = f"""
You are an agricultural AI assistant helping small and marginal
farmers in India.

A farmer reports these crop symptoms:

{symptoms}

The farmer selected this language:

{language_name}

Provide all farmer-facing text in {language_name}.

Analyze the symptoms.

Return ONLY valid JSON in exactly this structure:

{{
    "disease": "likely disease or crop problem",
    "cause": "possible cause",
    "treatment": [
        "treatment step 1",
        "treatment step 2"
    ],
    "prevention": [
        "prevention step 1",
        "prevention step 2"
    ]
}}

Use simple language that a farmer can understand.

If the symptoms are not enough to identify a specific disease,
clearly indicate that the diagnosis is uncertain.

Do not include markdown.
Do not include ```json.
Do not add any text outside the JSON.
"""

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt
    )

    print("\n=== RAW GEMINI RESPONSE ===")
    print(response.text)
    print("===========================\n")

    try:
        import re

        clean_text = response.text.strip()

        # Remove markdown if Gemini adds it
        if clean_text.startswith("```json"):
            clean_text = clean_text[7:]

        elif clean_text.startswith("```"):
            clean_text = clean_text[3:]

        if clean_text.endswith("```"):
            clean_text = clean_text[:-3]

        # Remove trailing commas
        clean_text = re.sub(r',\s*([\]}])', r'\1', clean_text)

        advisory = json.loads(clean_text)

    except Exception as e:
        print("JSON ERROR:", e)
        print("RAW RESPONSE:", response.text)

        return jsonify({
            "success": False,
            "error": "AI returned an invalid response",
            "raw_response": response.text
        }), 500

    return jsonify({
        "success": True,
        "language": language,
        "disease": advisory.get("disease", ""),
        "cause": advisory.get("cause", ""),
        "treatment": advisory.get("treatment", []),
        "prevention": advisory.get("prevention", [])
    })


# --------------------------------------------------
# IMAGE CROP DIAGNOSIS
# --------------------------------------------------

@app.route("/diagnose-image", methods=["POST"])
def diagnose_image():

    if "image" not in request.files:
        return jsonify({
            "success": False,
            "error": "No image provided"
        }), 400

    image = request.files["image"]

    if image.filename == "":
        return jsonify({
            "success": False,
            "error": "No image selected"
        }), 400

    # Get selected language
    language = request.form.get("language", "en")

    # Supported languages come from language_config.py
    if language not in SUPPORTED_LANGUAGES:
        return jsonify({
            "success": False,
            "error": "Unsupported language",
            "supported_languages": list(SUPPORTED_LANGUAGES.keys())
        }), 400

    language_name = SUPPORTED_LANGUAGES[language]["name"]

    image_bytes = image.read()

    if not image_bytes:
        return jsonify({
            "success": False,
            "error": "Image is empty"
        }), 400

    mime_type = image.content_type or "image/jpeg"

    prompt = f"""
You are an agricultural AI assistant helping small and marginal
farmers in India.

Analyze the attached crop image.

The farmer selected this language:

{language_name}

Provide all farmer-facing text in {language_name}.

Identify any visible:
- crop disease
- pest damage
- nutrient deficiency
- other visible crop problem

Return ONLY valid JSON in exactly this structure:

{{
    "crop": "crop name",
    "disease": "likely disease or problem",
    "confidence": "high, medium, or low",
    "cause": "possible cause",
    "treatment": [
        "treatment step 1",
        "treatment step 2"
    ],
    "prevention": [
        "prevention step 1",
        "prevention step 2"
    ]
}}

Use simple language suitable for an Indian farmer.

If the image is unclear or the crop cannot be identified,
say so instead of inventing a diagnosis.

Do not include markdown.
Do not include ```json.
Do not add any text outside the JSON.
"""

    try:
        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=[
                prompt,
                {
                    "inline_data": {
                        "mime_type": mime_type,
                        "data": base64.b64encode(image_bytes).decode("utf-8")
                    }
                }
            ]
        )

    except Exception as e:
        print("Gemini image diagnosis error:", e)

        return jsonify({
            "success": False,
            "error": "AI service is temporarily unavailable. Please try again."
        }), 503

    try:
        raw_response = response.text.strip()

        # Remove Markdown code fences if Gemini adds them
        if raw_response.startswith("```json"):
            raw_response = raw_response[7:]

        elif raw_response.startswith("```"):
            raw_response = raw_response[3:]

        if raw_response.endswith("```"):
            raw_response = raw_response[:-3]

        raw_response = raw_response.strip()

        diagnosis = json.loads(raw_response)

    except json.JSONDecodeError:
        return jsonify({
            "success": False,
            "error": "AI returned invalid JSON",
            "raw_response": response.text
        }), 500

    return jsonify({
        "success": True,
        "language": language,
        "diagnosis": diagnosis
    })


# --------------------------------------------------
# FARM ADVISORY
# --------------------------------------------------

@app.route("/farm-advisory", methods=["POST"])
def farm_advisory():

    data = request.get_json()

    if not data:
        return jsonify({
            "success": False,
            "error": "Please provide JSON data"
        }), 400

    crop = data.get("crop", "").strip()
    place = data.get("location", "").strip()
    language = data.get("language", "").strip()

    soil_card = data.get("soil_card")

    # --------------------------------------------------
    # INPUT VALIDATION
    # --------------------------------------------------

    valid, error = validate_crop(crop)

    if not valid:
        return jsonify({
            "success": False,
            "error": error
        }), 400

    valid, error = validate_place(place)

    if not valid:
        return jsonify({
            "success": False,
            "error": error
        }), 400

    valid, error = validate_language(
        language,
        SUPPORTED_LANGUAGES
    )

    if not valid:
        return jsonify({
            "success": False,
            "error": error
        }), 400

    # --------------------------------------------------
    # SOIL INTERPRETATION
    # --------------------------------------------------

    soil_interpretation = {}

    if soil_card:
        soil_interpretation = interpret_soil(soil_card)

    # --------------------------------------------------
    # CROP RECOMMENDATIONS
    # --------------------------------------------------

    crop_recommendations = {
        "current_crop": crop,
        "recommendations": [],
        "soil_observations_used": {},
        "disclaimer": (
            "Crop recommendations require soil information "
            "and additional local agricultural context."
        )
    }

    if soil_card:
        crop_recommendations = recommend_crops(
            crop,
            soil_card
        )

    # --------------------------------------------------
    # 1. FIND LOCATION
    # --------------------------------------------------

    geocode_url = (
        "https://geocoding-api.open-meteo.com/v1/search"
    )

    geocode_params = {
        "name": place,
        "count": 1,
        "language": "en",
        "format": "json"
    }

    try:
        geocode_response = requests.get(
            geocode_url,
            params=geocode_params,
            timeout=10
        )

        geocode_response.raise_for_status()

        geocode_data = geocode_response.json()

    except requests.RequestException as e:
        return jsonify({
            "success": False,
            "error": "Location service failed",
            "details": str(e)
        }), 500

    if "results" not in geocode_data:
        return jsonify({
            "success": False,
            "error": "Location not found"
        }), 404

    if not geocode_data["results"]:
        return jsonify({
            "success": False,
            "error": "Location not found"
        }), 404

    location = geocode_data["results"][0]

    location_name = location.get("name", place)
    state = location.get("admin1", "")
    country = location.get("country", "")

    latitude = location["latitude"]
    longitude = location["longitude"]

    # --------------------------------------------------
    # AUTOMATIC LANGUAGE DETECTION
    # --------------------------------------------------

    # If farmer selects a language, use it.
    # Otherwise, detect a default language from the state.

    if language:
        language_source = "farmer_selection"

    else:
        language = detect_language_from_state(state)
        language_source = "state_default"

    language_name = SUPPORTED_LANGUAGES[language]["name"]

    # --------------------------------------------------
    # 2. GET WEATHER
    # --------------------------------------------------

    weather_url = (
        "https://api.open-meteo.com/v1/forecast"
    )

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

    try:
        weather_response = requests.get(
            weather_url,
            params=weather_params,
            timeout=10
        )

        weather_response.raise_for_status()

        weather_data = weather_response.json()

    except requests.RequestException as e:
        return jsonify({
            "success": False,
            "error": "Weather service failed",
            "details": str(e)
        }), 500

    current = weather_data.get("current", {})
    daily = weather_data.get("daily", {})

    # --------------------------------------------------
    # 3. SOIL HEALTH CARD
    # --------------------------------------------------

    if not soil_card:
        return jsonify({
            "success": False,
            "error": "Please provide soil_card data from /soil-card"
        }), 400

    soil_parameters = soil_card.get(
        "soil_parameters",
        {}
    )

    soil_data = {
        "ph": soil_parameters.get("ph"),

        "electrical_conductivity":
            soil_parameters.get(
                "electrical_conductivity"
            ),

        "organic_carbon":
            soil_parameters.get(
                "organic_carbon"
            ),

        "nitrogen":
            soil_parameters.get(
                "nitrogen"
            ),

        "phosphorus":
            soil_parameters.get(
                "phosphorus"
            ),

        "potassium":
            soil_parameters.get(
                "potassium"
            ),

        "sulphur":
            soil_parameters.get(
                "sulphur"
            ),

        "zinc":
            soil_parameters.get(
                "zinc"
            ),

        "iron":
            soil_parameters.get(
                "iron"
            ),

        "manganese":
            soil_parameters.get(
                "manganese"
            ),

        "copper":
            soil_parameters.get(
                "copper"
            ),

        "boron":
            soil_parameters.get(
                "boron"
            )
    }

    # --------------------------------------------------
    # 4. FARM DATA
    # --------------------------------------------------

    farm_data = {

        "crop": crop,

        "language": {
            "code": language,
            "name": language_name
        },

        "location": {
            "name": location_name,
            "state": state,
            "country": country,
            "latitude": latitude,
            "longitude": longitude
        },

        "weather": {

            "current": {

                "temperature":
                    current.get(
                        "temperature_2m"
                    ),

                "humidity":
                    current.get(
                        "relative_humidity_2m"
                    ),

                "precipitation":
                    current.get(
                        "precipitation"
                    ),

                "rain":
                    current.get(
                        "rain"
                    ),

                "wind_speed":
                    current.get(
                        "wind_speed_10m"
                    )
            },

            "forecast": {

                "dates":
                    daily.get(
                        "time"
                    ),

                "max_temperature":
                    daily.get(
                        "temperature_2m_max"
                    ),

                "min_temperature":
                    daily.get(
                        "temperature_2m_min"
                    ),

                "rain_probability":
                    daily.get(
                        "precipitation_probability_max"
                    ),

                "rainfall":
                    daily.get(
                        "precipitation_sum"
                    )
            }
        },

        "soil": soil_data,

        "soil_interpretation":
            soil_interpretation,

        "crop_recommendations":
            crop_recommendations,

        # Satellite adapter.
        # Actual satellite measurements are not connected yet.
        "satellite": {

            "source": {
                "name": "ISRO / Bhuvan",
                "status": "not_connected"
            },

            "surface_soil_moisture": {

                "product":
                    "Surface Soil Moisture - 2 Day",

                "status":
                    "not_connected",

                "resolution":
                    "0.25 x 0.25 degree",

                "unit":
                    "m3/m3",

                "value":
                    None
            },

            "vegetation_condition": {

                "status":
                    "planned",

                "value":
                    None
            }
        }
    }

    # --------------------------------------------------
    # COMMON INTEROPERABLE FARM PROFILE
    # --------------------------------------------------

    farm_profile = create_farm_profile(

        crop=crop,

        location={
            "name": location_name,
            "state": state,
            "country": country,
            "latitude": latitude,
            "longitude": longitude
        },

        soil=soil_data,

        weather=weather_data,

        satellite=farm_data["satellite"],

        language={
            "code": language,
            "name": language_name,
            "source": language_source
        }
    )

    # --------------------------------------------------
    # 5. GEMINI AGRICULTURAL AI
    # --------------------------------------------------

    prompt = f"""
You are Kisan Alert, an agricultural advisory AI
designed for small and marginal farmers in India.

Analyze the following farm information:

{json.dumps(
    farm_data,
    indent=2,
    ensure_ascii=False
)}

IMPORTANT RULES:

1. Use ONLY the information supplied above.

2. Do not invent weather measurements.

3. Do not invent soil measurements.

4. Satellite measurements are currently NOT available.
   - The satellite section only contains metadata
     about the planned ISRO/Bhuvan integration.
   - Do NOT describe the metadata as an actual
     satellite observation.
   - Do NOT invent soil moisture, vegetation,
     NDVI, crop health, or any other satellite
     measurement.
   - If satellite data is unavailable, clearly say
     that Kisan Alert did not use satellite
     measurements for this advisory.

5. Do not pretend satellite values exist.

6. Do not provide pesticide dosage.

7. Do not provide fertilizer dosage.

8. Do not provide chemical application rates.

9. Do not guarantee crop yield.

10. Communicate uncertainty when information
    is insufficient.

11. Use simple language suitable for farmers.

12. Return the entire advisory in {language_name}.

13. Keep the crop recommendations as candidates
    to consider, not guaranteed recommendations.

14. Consider the supplied location and weather
    conditions.

15. Consider the supplied Soil Health Card
    information.

16. Prefer practical soil-health and
    regenerative practices.

Return ONLY valid JSON.

Use exactly this structure:

{{
    "crop": "...",

    "overall_risk":
        "low, medium, or high",

    "weather_observation":
        "...",

    "soil_observation":
        "...",

    "satellite_observation":
        "...",

    "irrigation_advice":
        "...",

    "crop_assessment":
        "...",

    "alternative_crops_to_consider": [
        {{
            "crop": "...",
            "reason": "...",
            "confidence":
                "low, medium, or high"
        }}
    ],

    "farm_actions": [
        "...",
        "...",
        "..."
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

        raw_response = response.text.strip()

        # Remove Markdown code fences if Gemini adds them

        if raw_response.startswith("```json"):
            raw_response = raw_response[7:]

        elif raw_response.startswith("```"):
            raw_response = raw_response[3:]

        if raw_response.endswith("```"):
            raw_response = raw_response[:-3]

        raw_response = raw_response.strip()

        advisory = json.loads(raw_response)

    except json.JSONDecodeError:

        return jsonify({
            "success": False,
            "error": "Gemini returned invalid JSON",
            "raw_response": response.text
        }), 500

    except Exception as e:

        return jsonify({
            "success": False,
            "error": "Gemini request failed",
            "details": str(e)
        }), 500

    # --------------------------------------------------
    # 6. FINAL RESPONSE
    # --------------------------------------------------

    return jsonify({

        "success": True,

        "farm": {

            "crop": crop,

            "language": {
                "code": language,
                "name": language_name
            },

            "location": {
                "name": location_name,
                "state": state,
                "country": country,
                "latitude": latitude,
                "longitude": longitude
            }
        },

        "detected_language": {
            "code": language,
            "name": language_name,
            "source": language_source
        },

        "weather": farm_data["weather"],

        "farm_profile":
            farm_profile,

        "soil_interpretation":
            soil_interpretation,

        "crop_recommendations":
            crop_recommendations,

        "advisory":
            advisory
    })


# --------------------------------------------------
# SOIL HEALTH CARD API
# --------------------------------------------------

@app.route("/soil-card", methods=["POST"])
def soil_card():

    # --------------------------------------------------
    # CHECK IMAGE
    # --------------------------------------------------

    if "image" not in request.files:

        return jsonify({
            "success": False,
            "error":
                "Please upload a Soil Health Card image"
        }), 400

    image = request.files["image"]

    if image.filename == "":

        return jsonify({
            "success": False,
            "error": "No image selected"
        }), 400

    # --------------------------------------------------
    # CHECK FILE TYPE
    # --------------------------------------------------

    filename = image.filename.lower()

    allowed_extensions = (
        ".jpg",
        ".jpeg",
        ".png"
    )

    if not filename.endswith(
        allowed_extensions
    ):

        return jsonify({
            "success": False,
            "error":
                "Please upload JPG, JPEG, or PNG"
        }), 400

    # --------------------------------------------------
    # READ IMAGE
    # --------------------------------------------------

    image_bytes = image.read()

    if not image_bytes:

        return jsonify({
            "success": False,
            "error":
                "Uploaded image is empty"
        }), 400

    # --------------------------------------------------
    # MIME TYPE
    # --------------------------------------------------

    if filename.endswith(".png"):
        mime_type = "image/png"

    else:
        mime_type = "image/jpeg"

    # --------------------------------------------------
    # ENCODE IMAGE
    # --------------------------------------------------

    image_base64 = base64.b64encode(
        image_bytes
    ).decode("utf-8")

    # --------------------------------------------------
    # GEMINI PROMPT
    # --------------------------------------------------

    prompt = """
You are an agricultural soil-report extraction assistant.

The uploaded image is a Soil Health Card
or soil test report.

Read the document carefully.

Extract ONLY information that is actually
visible in the document.

Extract:

1. pH
2. Electrical Conductivity
3. Organic Carbon
4. Nitrogen
5. Phosphorus
6. Potassium
7. Sulphur
8. Zinc
9. Iron
10. Manganese
11. Copper
12. Boron

Rules:

- Do NOT guess missing values.
- Do NOT calculate values.
- Do NOT invent values.
- Preserve numerical values.
- Preserve units.
- If a value is not visible, return null.
- If the document is unclear, return null.
- Identify crop only if visible.
- Do not provide fertilizer dosage.
- Do not provide pesticide dosage.

Return ONLY valid JSON.

Use exactly:

{
    "document_type": "...",
    "farmer_name": null,
    "location": null,
    "crop": null,

    "soil_parameters": {

        "ph": {
            "value": null,
            "unit": null
        },

        "electrical_conductivity": {
            "value": null,
            "unit": null
        },

        "organic_carbon": {
            "value": null,
            "unit": null
        },

        "nitrogen": {
            "value": null,
            "unit": null
        },

        "phosphorus": {
            "value": null,
            "unit": null
        },

        "potassium": {
            "value": null,
            "unit": null
        },

        "sulphur": {
            "value": null,
            "unit": null
        },

        "zinc": {
            "value": null,
            "unit": null
        },

        "iron": {
            "value": null,
            "unit": null
        },

        "manganese": {
            "value": null,
            "unit": null
        },

        "copper": {
            "value": null,
            "unit": null
        },

        "boron": {
            "value": null,
            "unit": null
        }
    }
}
"""

    # --------------------------------------------------
    # SEND TO GEMINI
    # --------------------------------------------------

    try:

        response = client.models.generate_content(

            model="gemini-3.5-flash-lite",

            contents=[
                {
                    "text": prompt
                },
                {
                    "inline_data": {
                        "mime_type":
                            mime_type,

                        "data":
                            image_base64
                    }
                }
            ]
        )

    except Exception as e:

        return jsonify({
            "success": False,
            "error": "AI service failed",
            "details": str(e)
        }), 500

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

        return jsonify({
            "success": False,
            "error":
                "AI returned invalid JSON",
            "raw_response":
                response.text
        }), 500

    # --------------------------------------------------
    # RETURN RESULT
    # --------------------------------------------------

    return jsonify({

        "success": True,

        "soil_card":
            result

    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": "Endpoint not found."
    }), 404


@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        "success": False,
        "error": "HTTP method not allowed for this endpoint."
    }), 405


@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({
        "success": False,
        "error": "Internal server error."
    }), 500

# --------------------------------------------------
# RUN SERVER
# --------------------------------------------------

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)