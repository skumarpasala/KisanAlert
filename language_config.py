SUPPORTED_LANGUAGES = {
    "en": {
        "name": "English",
        "speech_recognition": "en-IN",
        "tts": "en"
    },
    "te": {
        "name": "Telugu",
        "speech_recognition": "te-IN",
        "tts": "te"
    },
    "hi": {
        "name": "Hindi",
        "speech_recognition": "hi-IN",
        "tts": "hi"
    },
    "ta": {
        "name": "Tamil",
        "speech_recognition": "ta-IN",
        "tts": "ta"
    },
    "kn": {
        "name": "Kannada",
        "speech_recognition": "kn-IN",
        "tts": "kn"
    },
    "ml": {
        "name": "Malayalam",
        "speech_recognition": "ml-IN",
        "tts": "ml"
    },
    "mr": {
        "name": "Marathi",
        "speech_recognition": "mr-IN",
        "tts": "mr"
    },
    "bn": {
        "name": "Bengali",
        "speech_recognition": "bn-IN",
        "tts": "bn"
    },
    "pa": {
        "name": "Punjabi",
        "speech_recognition": "pa-IN",
        "tts": "pa"
    },
    "gu": {
        "name": "Gujarati",
        "speech_recognition": "gu-IN",
        "tts": "gu"
    },
    "or": {
        "name": "Odia",
        "speech_recognition": "or-IN",
        "tts": "or"
    }
}


STATE_LANGUAGE_MAP = {
    "Andhra Pradesh": "te",
    "Telangana": "te",
    "Tamil Nadu": "ta",
    "Karnataka": "kn",
    "Kerala": "ml",
    "Maharashtra": "mr",
    "West Bengal": "bn",
    "Odisha": "or",
    "Punjab": "pa",
    "Gujarat": "gu",

    "Bihar": "hi",
    "Uttar Pradesh": "hi",
    "Madhya Pradesh": "hi",
    "Rajasthan": "hi",
    "Haryana": "hi",
    "Jharkhand": "hi",
    "Chhattisgarh": "hi",
    "Uttarakhand": "hi",
    "Himachal Pradesh": "hi",

    "Goa": "en"
}


def get_language(code):
    return SUPPORTED_LANGUAGES.get(code)


def detect_language_from_state(state):
    return STATE_LANGUAGE_MAP.get(state, "en")