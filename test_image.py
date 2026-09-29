import requests

url = "http://127.0.0.1:5000/diagnose-image"

image_path = "/Users/SUJITHAKUMARP/Desktop/tomato_leaf.jpg"

with open(image_path, "rb") as image_file:

    files = {
        "image": image_file
    }

    data = {
        "language": "te"
    }

    response = requests.post(
        url,
        files=files,
        data=data
    )

print("STATUS CODE:", response.status_code)
print("RESPONSE:")
print(response.text)