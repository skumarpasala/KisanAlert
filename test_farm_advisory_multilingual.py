import requests
import json

# First get the Soil Health Card
soil_card_url = "http://127.0.0.1:5000/soil-card"

image_path = "/Users/SUJITHAKUMARP/Desktop/soil_card.png"

with open(image_path, "rb") as image_file:

    files = {
        "image": image_file
    }

    soil_response = requests.post(
        soil_card_url,
        files=files
    )

soil_result = soil_response.json()

if not soil_result.get("success"):
    print("❌ Soil Card API failed")
    print(soil_result)
    exit()

soil_card = soil_result["soil_card"]

print("✅ Soil Health Card extracted successfully")


# Now send it to Farm Advisory

farm_url = "http://127.0.0.1:5000/farm-advisory"

farm_data = {

    "crop": "Cotton",
    "location": "Warangal",
    "soil_card": soil_card
}

response = requests.post(
    farm_url,
    json=farm_data
)

print("\nSTATUS CODE:", response.status_code)

print("\n🌾 KISAN ALERT FARM ADVISORY")
print("============================")

print(
    json.dumps(
        response.json(),
        indent=2,
        ensure_ascii=False
    )
)