import requests


BASE_URL = "http://127.0.0.1:5000"


def test_home():
    print("\n========== TEST 1: HOME ==========")

    response = requests.get(
        f"{BASE_URL}/"
    )

    print("Status:", response.status_code)
    print("Response:", response.text)

    if response.status_code == 200:
        print("✅ HOME API PASSED")
    else:
        print("❌ HOME API FAILED")


def test_diagnose():
    print("\n========== TEST 2: TEXT DIAGNOSIS ==========")

    data = {
        "symptoms": (
            "Tomato leaves have yellow spots "
            "and are drying."
        ),
        "language": "en"
    }

    response = requests.post(
        f"{BASE_URL}/diagnose",
        json=data
    )

    print("Status:", response.status_code)
    print("Response:", response.json())

    if response.status_code == 200:
        print("✅ TEXT DIAGNOSIS PASSED")
    else:
        print("❌ TEXT DIAGNOSIS FAILED")


def test_diagnose_image():
    print("\n========== TEST 3: IMAGE DIAGNOSIS ==========")

    image_path = "tomato_leaf.jpg"

    try:
        with open(image_path, "rb") as image_file:

            files = {
                "image": image_file
            }

            data = {
                "language": "en"
            }

            response = requests.post(
                f"{BASE_URL}/diagnose-image",
                files=files,
                data=data
            )

        print("Status:", response.status_code)
        print("Response:", response.json())

        if response.status_code == 200:
            print("✅ IMAGE DIAGNOSIS PASSED")
        else:
            print("❌ IMAGE DIAGNOSIS FAILED")

    except FileNotFoundError:
        print(
            f"⚠️ {image_path} not found. "
            "Skipping image test."
        )


def test_soil_card():
    print("\n========== TEST 4: SOIL CARD ==========")

    image_path = "soil_card.png"

    try:
        with open(image_path, "rb") as image_file:

            files = {
                "image": image_file
            }

            response = requests.post(
                f"{BASE_URL}/soil-card",
                files=files
            )

        print("Status:", response.status_code)
        print("Response:", response.json())

        if response.status_code == 200:
            print("✅ SOIL CARD PASSED")
        else:
            print("❌ SOIL CARD FAILED")

    except FileNotFoundError:
        print(
            f"⚠️ {image_path} not found. "
            "Skipping soil card test."
        )


def test_farm_advisory():
    print("\n========== TEST 5: FARM ADVISORY ==========")

    soil_card = {
        "document_type": "Soil Health Card",

        "farmer_name": "Demo Farmer",

        "location": "Visakhapatnam, Andhra Pradesh",

        "crop": "Tomato",

        "soil_parameters": {

            "ph": {
                "value": 6.5,
                "unit": ""
            },

            "electrical_conductivity": {
                "value": 0.42,
                "unit": "dS/m"
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
            },

            "sulphur": {
                "value": 18.6,
                "unit": "mg/kg"
            },

            "zinc": {
                "value": 0.72,
                "unit": "mg/kg"
            },

            "iron": {
                "value": 6.8,
                "unit": "mg/kg"
            },

            "manganese": {
                "value": 4.2,
                "unit": "mg/kg"
            },

            "copper": {
                "value": 0.68,
                "unit": "mg/kg"
            },

            "boron": {
                "value": 0.45,
                "unit": "mg/kg"
            }
        }
    }

    data = {
        "crop": "Tomato",

        "location":
            "Visakhapatnam",

        "language":
            "en",

        "soil_card":
            soil_card
    }

    response = requests.post(
        f"{BASE_URL}/farm-advisory",
        json=data
    )

    print("Status:", response.status_code)

    try:
        print("Response:")
        print(response.json())

    except Exception:
        print(response.text)

    if response.status_code == 200:
        print("✅ FARM ADVISORY PASSED")
    else:
        print("❌ FARM ADVISORY FAILED")


# --------------------------------------------------
# RUN ALL TESTS
# --------------------------------------------------

if __name__ == "__main__":

    print("\n")
    print("==========================================")
    print("       KISAN ALERT BACKEND TEST")
    print("==========================================")

    test_home()

    test_diagnose()

    test_diagnose_image()

    test_soil_card()

    test_farm_advisory()

    print("\n")
    print("==========================================")
    print("       TESTING COMPLETED")
    print("==========================================")