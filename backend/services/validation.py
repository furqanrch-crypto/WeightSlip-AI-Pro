from typing import Optional


def validate_weights(
    first_weight: Optional[float],
    second_weight: Optional[float],
    net_weight: Optional[float],
    tolerance: float = 1.0,
) -> dict:
    if first_weight is None or second_weight is None or net_weight is None:
        return {
            "status": "review_required",
            "valid": False,
            "calculated_net": None,
            "difference": None,
            "message": "One or more weight values are missing.",
        }

    calculated_net = first_weight - second_weight
    difference = abs(calculated_net - net_weight)
    valid = difference <= tolerance

    return {
        "status": "valid" if valid else "review_required",
        "valid": valid,
        "calculated_net": calculated_net,
        "difference": difference,
        "message": (
            "Weight values are consistent."
            if valid
            else "Net weight does not match first weight minus second weight."
        ),
    }
