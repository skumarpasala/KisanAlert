from crop_recommender import recommend_crops


# Demo Soil Health Card data
soil_card = {
    "soil_parameters": {
        "ph": {
            "value": 6.5,
            "unit": "-"
        },
        "organic_carbon": {
            "value": 0.58,
            "unit": "%"
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
        }
    }
}


# Current crop
current_crop = "Cotton"


# Run recommendation engine
result = recommend_crops(
    current_crop,
    soil_card
)


# Display result
print("\n🌾 KISAN ALERT — CROP RECOMMENDATION")
print("====================================")

print("Current crop:", result["current_crop"])

print("\n🌱 Crops to consider:")

for recommendation in result["recommendations"]:

    print("\nCrop:", recommendation["crop"])
    print("Confidence:", recommendation["confidence"])
    print("Reason:", recommendation["reason"])
    print("Soil role:", recommendation["soil_role"])


print("\n🧪 Soil information used:")
print(result["soil_observations_used"])

print("\n⚠️ Important:")
print(result["disclaimer"])