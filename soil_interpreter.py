def get_numeric_value(parameter):
    """
    Safely extract numeric value from a soil parameter.
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


def interpret_soil(soil_card):
    """
    Interpret extracted soil values.

    IMPORTANT:
    These are demo/reference ranges for the prototype.
    They are NOT fertilizer recommendation rules.
    """

    parameters = soil_card.get("soil_parameters", {})

    interpretation = {}

    # -------------------------
    # pH
    # -------------------------

    ph = get_numeric_value(parameters.get("ph"))

    if ph is None:
        interpretation["ph"] = {
            "value": None,
            "status": "unknown"
        }

    elif ph < 6.0:
        interpretation["ph"] = {
            "value": ph,
            "status": "acidic"
        }

    elif ph <= 7.5:
        interpretation["ph"] = {
            "value": ph,
            "status": "near_neutral"
        }

    else:
        interpretation["ph"] = {
            "value": ph,
            "status": "alkaline"
        }

    # -------------------------
    # Organic Carbon
    # -------------------------

    organic_carbon = get_numeric_value(
        parameters.get("organic_carbon")
    )

    if organic_carbon is None:
        interpretation["organic_carbon"] = {
            "value": None,
            "status": "unknown"
        }

    elif organic_carbon < 0.5:
        interpretation["organic_carbon"] = {
            "value": organic_carbon,
            "status": "low"
        }

    elif organic_carbon < 0.75:
        interpretation["organic_carbon"] = {
            "value": organic_carbon,
            "status": "medium"
        }

    else:
        interpretation["organic_carbon"] = {
            "value": organic_carbon,
            "status": "high"
        }

    # -------------------------
    # Nitrogen
    # -------------------------

    nitrogen = get_numeric_value(
        parameters.get("nitrogen")
    )

    if nitrogen is None:
        interpretation["nitrogen"] = {
            "value": None,
            "status": "unknown"
        }

    else:
        interpretation["nitrogen"] = {
            "value": nitrogen,
            "status": "measured"
        }

    # -------------------------
    # Phosphorus
    # -------------------------

    phosphorus = get_numeric_value(
        parameters.get("phosphorus")
    )

    if phosphorus is None:
        interpretation["phosphorus"] = {
            "value": None,
            "status": "unknown"
        }

    else:
        interpretation["phosphorus"] = {
            "value": phosphorus,
            "status": "measured"
        }

    # -------------------------
    # Potassium
    # -------------------------

    potassium = get_numeric_value(
        parameters.get("potassium")
    )

    if potassium is None:
        interpretation["potassium"] = {
            "value": None,
            "status": "unknown"
        }

    else:
        interpretation["potassium"] = {
            "value": potassium,
            "status": "measured"
        }

    return interpretation