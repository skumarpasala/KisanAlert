import json

from soil_interpreter import interpret_soil


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


result = interpret_soil(soil_card)

print("\n🌱 KISAN ALERT — SOIL INTERPRETATION")
print("====================================")

print(
    json.dumps(
        result,
        indent=2,
        ensure_ascii=False
    )
)