# 🌾 Kisan Alert

### AI-Powered Smart Agriculture Advisory Platform

Kisan Alert is an AI-powered agriculture platform that helps farmers make informed decisions using **crop disease diagnosis, soil analysis, weather data, crop recommendations, and localized farm advisories**.

## 🚜 Problem

Small and marginal farmers often face difficulties with:

* Identifying crop diseases
* Understanding soil health
* Selecting suitable crops
* Responding to changing weather conditions
* Accessing timely agricultural guidance

## 💡 Solution

Kisan Alert combines **AI + soil + weather + location + crop information** to generate practical agricultural recommendations.

```text
Crop / Image / Soil / Location
              ↓
       AI + Data Processing
              ↓
    Soil + Weather + Disease
              ↓
       Farm Recommendation
              ↓
       Farmer Advisory
```

## ✨ Key Features

* 🌱 **AI Disease Diagnosis** — Diagnose crop diseases from symptoms.
* 📷 **Image Diagnosis** — Analyze crop/leaf images.
* 📄 **Soil Health Card** — Extract and process soil parameters.
* 🌱 **Soil Interpretation** — Interpret pH, N, P, K, organic carbon, etc.
* 🌾 **Crop Recommendation** — Recommend crops based on available farm conditions.
* 🌦️ **Weather Intelligence** — Use location-based weather information.
* 📍 **Location Intelligence** — Convert locations into coordinates for localized data.
* 🛰️ **Satellite Integration** — Architecture for agricultural satellite data.
* 🧠 **Farm Advisory** — Combine multiple data sources into one advisory.
* 🌐 **Language Support** — Supports English and Telugu responses.
* 🎙️ **Voice Interaction** — Voice input/output support.

## 🏗️ Technology Stack

**Frontend**

* HTML
* CSS
* JavaScript

**Backend**

* Python
* Flask
* REST APIs

**AI**

* Google Gemini API

**Data**

* Weather data
* Geolocation
* Soil Health Card data
* Agricultural parameters
* Satellite-data integration

## 🔌 Backend APIs

| Endpoint          | Purpose                       |
| ----------------- | ----------------------------- |
| `/diagnose`       | Text-based disease diagnosis  |
| `/diagnose-image` | Image-based disease diagnosis |
| `/soil-card`      | Soil Health Card processing   |
| `/farm-advisory`  | Combined farm advisory        |

## ⚙️ Run Locally

### Clone

```bash
git clone YOUR_REPOSITORY_URL
cd KisanAlert
```

### Install dependencies

```bash
pip install -r requirements.txt
```

### Configure API key

Create a `.env` file:

```env
GEMINI_API_KEY=your_api_key_here
```

### Start backend

```bash
python main.py
```

Backend:

```text
http://127.0.0.1:5000
```

## 🧪 Testing

Run the backend API tests:

```bash
python test_all_apis.py
```

## 🚀 Future Scope

* Real-time satellite-derived soil moisture
* NDVI and vegetation monitoring
* More regional languages
* Advanced crop recommendations
* Pest and disease alerts
* Historical farm analytics
* Expanded agricultural data interoperability

## 🌾 Vision

> **Making AI-powered agricultural intelligence accessible to every farmer.**

---

### Project

**Kisan Alert** — AI-powered agriculture intelligence for smarter, climate-aware farming.
