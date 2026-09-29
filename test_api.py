import requests

url = "http://127.0.0.1:5000/diagnose"

data = {
    "symptoms": "Tomato leaves have yellow spots and the leaves are starting to dry."
}

response = requests.post(url, json=data)

print("STATUS CODE:", response.status_code)
print("RESPONSE:")
print(response.text)