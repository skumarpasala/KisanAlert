import json
import os

from google import genai
from dotenv import load_dotenv


load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


# --------------------------------
# STEP 1: Collect soil information
# --------------------------------

print("🌱 KISAN ALERT SOIL ADVISORY")
print("============================")

crop = input("🌾 Enter your crop: ")

print("\nEnter the available soil information.")

ph = float(input("🧪 Soil pH: "))
nitrogen = input("🟢 Nitrogen level (Low/Medium/High): ")
phosphorus = input("🔵 Phosphorus level (Low/Medium/High): ")
potassium = input("🟣 Potassium level (Low/Medium/High): ")
organic_carbon = input(
    "🌿 Organic carbon level (Low/Medium/High): "
)


# --------------------------------
# STEP 2: Create common soil model
# --------------------------------

soil_profile = {
    "crop": crop,
    "soil": {
        "ph": ph,
        "nitrogen": nitrogen,
        "phosphorus": phosphorus,
        "potassium": potassium,
        "organic_carbon": organic_carbon
    }
}


# --------------------------------
# STEP 3: Send soil data to Gemini
# --------------------------------

prompt = f"""
You are Kisan Alert, an agricultural AI assistant
helping small and marginal farmers in India.

Crop:
{crop}

Soil information:

pH:
{ph}

Nitrogen:
{nitrogen}

Phosphorus:
{phosphorus}

Potassium:
{potassium}

Organic carbon:
{organic_carbon}

Analyze the provided soil information for the given crop.

Provide practical guidance about:

- soil condition
- possible nutrient limitations
- crop suitability considerations
- soil management
- organic matter management

Return ONLY valid JSON in exactly this structure:

{{
    "crop": "{crop}",
    "soil_condition": "simple description",
    "nutrient_observations": [
        "observation 1",
        "observation 2"
    ],
    "soil_actions": [
        "action 1",
        "action 2",
        "action 3"
    ],
    "warning": "important caution"
}}

Use simple language suitable for an Indian farmer.

Do not invent soil measurements.

Do not provide fertilizer dosage or chemical application rates.

If the provided information is insufficient for a reliable conclusion,
clearly say so.

Do not include markdown.
Do not include ```json.
Do not add text outside the JSON.
"""


response = client.models.generate_content(
    model="gemini-3.5-flash-lite",
    contents=prompt
)


# --------------------------------
# STEP 4: Parse Gemini response
# --------------------------------

try:

    advisory = json.loads(response.text)

except json.JSONDecodeError:

    print("\n❌ Gemini returned invalid JSON")
    print(response.text)
    exit()


# --------------------------------
# STEP 5: Display result
# --------------------------------

print("\n🌱 KISAN ALERT SOIL ADVISORY")
print("============================")

print(
    json.dumps(
        advisory,
        ensure_ascii=False,
        indent=2
    )
)