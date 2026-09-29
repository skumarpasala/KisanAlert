def get_numeric_value(parameter):
    """
    Safely extract a numeric value from a soil parameter.
    """
    if not parameter:
        return None

    value = parameter.get("value")

    if isinstance(value, (int, float)):
        return value

    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def recommend_crops(current_crop, soil_card):
    """
    Generate alternative crops to consider based on
    basic soil information.

    This is a prototype recommendation layer.
    It does NOT provide guaranteed crop recommendations.
    """

    parameters = soil_card.get("soil_parameters", {})

    ph = get_numeric_value(parameters.get("ph"))
    organic_carbon = get_numeric_value(
        parameters.get("organic_carbon")
    )

    nitrogen = get_numeric_value(
        parameters.get("nitrogen")
    )

    phosphorus = get_numeric_value(
        parameters.get("phosphorus")
    )

    potassium = get_numeric_value(
        parameters.get("potassium")
    )

    recommendations = []

    # -----------------------------------------------------
    # Red gram
    # -----------------------------------------------------

    if current_crop.lower() != "redgram":

        if ph is None or 6.0 <= ph <= 7.5:

            recommendations.append({
                "crop": "Redgram",
                "confidence": "medium",
                "reason": (
                    "The available soil information indicates "
                    "conditions that can be considered for "
                    "redgram as an alternative crop."
                ),
                "soil_role": (
                    "A legume crop that can be considered "
                    "within a crop rotation."
                )
            })

    # -----------------------------------------------------
    # Green gram
    # -----------------------------------------------------

    if current_crop.lower() != "greengram":

        if ph is None or 6.0 <= ph <= 7.5:

            recommendations.append({
                "crop": "Greengram",
                "confidence": "medium",
                "reason": (
                    "The available soil information indicates "
                    "conditions that can be considered for "
                    "greengram as an alternative crop."
                ),
                "soil_role": (
                    "A legume crop that can be considered "
                    "as part of crop rotation."
                )
            })

    # -----------------------------------------------------
    # Groundnut
    # -----------------------------------------------------

    if current_crop.lower() != "groundnut":

        if ph is None or 6.0 <= ph <= 7.5:

            recommendations.append({
                "crop": "Groundnut",
                "confidence": "medium",
                "reason": (
                    "The available soil information indicates "
                    "conditions that can be considered for "
                    "groundnut."
                ),
                "soil_role": (
                    "Can be considered as a rotational crop "
                    "where locally suitable."
                )
            })

    # -----------------------------------------------------
    # Limit the prototype output
    # -----------------------------------------------------

    recommendations = recommendations[:3]

    # -----------------------------------------------------
    # Soil observations
    # -----------------------------------------------------

    soil_observations = {
        "ph": ph,
        "organic_carbon": organic_carbon,
        "nitrogen": nitrogen,
        "phosphorus": phosphorus,
        "potassium": potassium
    }

    return {
        "current_crop": current_crop,
        "recommendations": recommendations,
        "soil_observations_used": soil_observations,
        "disclaimer": (
            "These are crops to consider based on the "
            "available soil information. They are not "
            "guaranteed recommendations. Local climate, "
            "water availability, season, market conditions, "
            "and agricultural guidance should also be considered."
        )
    }