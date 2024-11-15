import math


def get_confidence_value(limit):
    """
    Returns a confidence value given a limit. The confidence value ranges from 1 to 10 and is logarithmic.

    Args:
        limit (int): The limit value.

    Returns:
        float: The confidence value.
    """
    min_limit = 250
    max_limit = 1500
    if limit < min_limit:
        limit = min_limit
    elif limit > max_limit:
        limit = max_limit
    return 1 + 9 * (math.log(limit / min_limit) / math.log(max_limit / min_limit))
