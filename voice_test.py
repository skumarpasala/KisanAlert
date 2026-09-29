import speech_recognition as sr
import requests
import json
from gtts import gTTS
import subprocess
import os

from language_config import SUPPORTED_LANGUAGES


# --------------------------------------------------
# SELECT LANGUAGE
# --------------------------------------------------

print("🌾 KISAN ALERT — VOICE ASSISTANT")
print("================================")

print("\nAvailable languages:")

for code, info in SUPPORTED_LANGUAGES.items():
    print(f"{code} - {info['name']}")

language = input("\n🌐 Enter language code: ").strip().lower()

if language not in SUPPORTED_LANGUAGES:
    print("❌ Unsupported language.")
    print("Available:", ", ".join(SUPPORTED_LANGUAGES.keys()))
    exit()

language_info = SUPPORTED_LANGUAGES[language]

speech_language = language_info["speech_recognition"]
tts_language = language_info["tts"]
language_name = language_info["name"]

print(f"\n✅ Selected language: {language_name}")


# --------------------------------------------------
# SPEECH RECOGNITION
# --------------------------------------------------

recognizer = sr.Recognizer()

print("\n🎤 Speak your crop problem...")

try:

    with sr.Microphone() as source:

        recognizer.adjust_for_ambient_noise(source)

        print("🎙️ Listening...")

        audio = recognizer.listen(source)

except Exception as e:

    print("❌ Microphone error:")
    print(e)

    exit()


print("\n⏳ Converting speech to text...")


try:

    symptoms = recognizer.recognize_google(
        audio,
        language=speech_language
    )

    print("\n🗣️ You said:")
    print(symptoms)

except sr.UnknownValueError:

    print("❌ Could not understand the speech.")
    exit()

except sr.RequestError as e:

    print("❌ Speech recognition error:")
    print(e)
    exit()


# --------------------------------------------------
# SEND TO KISAN ALERT AI
# --------------------------------------------------

print("\n🤖 Sending symptoms to Kisan Alert AI...")


url = "http://127.0.0.1:5000/diagnose"

data = {
    "symptoms": symptoms,
    "language": language
}


try:

    response = requests.post(
        url,
        json=data,
        timeout=60
    )

except requests.RequestException as e:

    print("❌ Could not connect to Kisan Alert backend.")
    print(e)

    exit()


if response.status_code != 200:

    print("❌ API Error")
    print(response.text)

    exit()


result = response.json()


# --------------------------------------------------
# DISPLAY AI RESPONSE
# --------------------------------------------------

print("\n🌱 KISAN ALERT RESPONSE:")
print("========================")

print(
    json.dumps(
        result,
        ensure_ascii=False,
        indent=2
    )
)


# --------------------------------------------------
# PREPARE VOICE RESPONSE
# --------------------------------------------------

disease = result.get("disease", "")

cause = result.get("cause", "")

treatment = result.get("treatment", [])

prevention = result.get("prevention", [])


if isinstance(treatment, list):
    treatment_text = ". ".join(treatment)
else:
    treatment_text = str(treatment)


if isinstance(prevention, list):
    prevention_text = ". ".join(prevention)
else:
    prevention_text = str(prevention)


voice_text = f"""
{language_name}

Disease or problem:
{disease}

Possible cause:
{cause}

Treatment:
{treatment_text}

Prevention:
{prevention_text}
"""


# --------------------------------------------------
# TEXT TO SPEECH
# --------------------------------------------------

print(f"\n🔊 Generating {language_name} voice...")


audio_file = "kisan_alert_response.mp3"


try:

    tts = gTTS(
        text=voice_text,
        lang=tts_language
    )

    tts.save(audio_file)

except Exception as e:

    print("❌ Text-to-speech failed:")
    print(e)

    exit()


print("🔊 Kisan Alert is speaking...\n")


# --------------------------------------------------
# PLAY AUDIO
# --------------------------------------------------

try:

    subprocess.run(
        ["afplay", audio_file],
        check=True
    )

except Exception as e:

    print("❌ Could not play audio:")
    print(e)

finally:

    if os.path.exists(audio_file):
        os.remove(audio_file)


print("\n✅ Voice advisory completed!")