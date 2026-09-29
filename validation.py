def validate_crop(crop):
    if not crop:
        return False, "Crop is required."

    if not isinstance(crop, str):
        return False, "Crop must be a text value."

    crop = crop.strip()

    if not crop:
        return False, "Crop cannot be empty."

    if len(crop) > 100:
        return False, "Crop name is too long."

    return True, None


def validate_place(place):
    if not place:
        return False, "Location is required."

    if not isinstance(place, str):
        return False, "Location must be a text value."

    place = place.strip()

    if not place:
        return False, "Location cannot be empty."

    if len(place) > 150:
        return False, "Location name is too long."

    return True, None


def validate_language(language, supported_languages):
    if language is None:
        return True, None

    if not isinstance(language, str):
        return False, "Language must be a text value."

    language = language.strip()

    if not language:
        return True, None

    if language not in supported_languages:
        return False, (
            f"Unsupported language '{language}'. "
            f"Supported languages: {', '.join(supported_languages.keys())}"
        )

    return True, None