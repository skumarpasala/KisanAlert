import requests
import json

url = "http://127.0.0.1:5000/soil-card"

image_path = "/Users/SUJITHAKUMARP/Desktop/soil_card.png"

with open(image_path, "rb") as image_file:

    files = {
        "image": image_file
    }

    response = requests.post(
        url,
        files=files
    )

print("STATUS CODE:", response.status_code)

print("\nSOIL CARD API RESPONSE:")

print(
    json.dumps(
        response.json(),
        indent=2,
        ensure_ascii=False
    )
)