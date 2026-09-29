import os
import json
import base64

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
# GET SOIL CARD
# --------------------------------------------------

image_path = input("📄 Enter Soil Health Card image path: ").strip()

if not os.path.exists(image_path):
    print("❌ File not found.")
    exit()


# --------------------------------------------------
# READ IMAGE
# --------------------------------------------------

with open(image_path, "rb") as image_file:
    image_bytes = image_file.read()


if not image_bytes:
    print("❌ Image file is empty.")
    exit()


# --------------------------------------------------
# DETERMINE IMAGE TYPE
# --------------------------------------------------

extension = os.path.splitext(image_path)[1].lower()

mime_types = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png"
}

mime_type = mime_types.get(extension)

if mime_type is None:
    print("❌ Please use JPG, JPEG, or PNG.")
    exit()


# --------------------------------------------------
# CONVERT IMAGE
# --------------------------------------------------

image_base64 = base64.b64encode(image_bytes).decode("utf-8")


# --------------------------------------------------
# GEMINI PROMPT
# --------------------------------------------------

prompt = """
You are an agricultural soil-report extraction assistant.

The uploaded image is a Soil Health Card or soil test report.

Read the document carefully and extract ONLY values that are
actually visible in the document.

Extract these parameters when available:

1. pH
2. Electrical Conductivity (EC)
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

Important rules:

- Do NOT guess missing values.
- Do NOT calculate values.
- Do NOT invent values.
- Preserve the numerical values shown in the document.
- Preserve units when visible.
- If a value is not visible, return null.
- If the image is unclear, return null for that field.
- Identify the crop if a crop name is visible.
- Identify the farmer/location information only if clearly visible.
- Do not provide fertilizer dosage or chemical recommendations.

Return ONLY valid JSON using exactly this structure:

{
    "document_type": "Soil Health Card or Soil Test Report",
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
# SEND IMAGE TO GEMINI
# --------------------------------------------------

print("\n🔎 Reading Soil Health Card...")
print("🤖 Sending document to Kisan Alert AI...")


try:

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",

        contents=[
            {
                "text": prompt
            },
            {
                "inline_data": {
                    "mime_type": mime_type,
                    "data": image_base64
                }
            }
        ]
    )

except Exception as e:

    print("\n❌ Gemini error:")
    print(e)
    exit()


# --------------------------------------------------
# PARSE JSON
# --------------------------------------------------

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
print("🧪 KISAN ALERT — SOIL HEALTH CARD")
print("=================================")

# --------------------------------------------------
# SAVE EXTRACTED SOIL DATA
# --------------------------------------------------

output_file = "soil_card_data.json"

with open(output_file, "w", encoding="utf-8") as file:
    json.dump(
        result,
        file,
        indent=2,
        ensure_ascii=False
    )

print(f"\n💾 Soil data saved to: {output_file}")

print("\n✅ Soil Health Card extraction completed.")