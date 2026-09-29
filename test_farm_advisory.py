import requests
import json

url = "http://127.0.0.1:5000/farm-advisory"

data = {
    "crop": "Tomato",
    "location": "Visakhapatnam"
}

response = requests.post(
    url,
    json=data
)

print("STATUS CODE:", response.status_code)

print("\nKISAN ALERT FARM ADVISORY:")
print(
    json.dumps(
        response.json(),
        indent=2,
        ensure_ascii=False
    )
)