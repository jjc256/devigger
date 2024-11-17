import math
from enum import Enum


class DevigMethod(Enum):
    MULTIPLICATIVE = 1
    POWER = 2


def get_confidence_value(limit):
    """
    Returns a confidence value given a limit. The confidence value ranges from 1 to 10 and is logarithmic.

    Args:
        limit (int): The limit value.

    Returns:
        float: The confidence value.
    """
    min_limit = 250
    max_limit = 10000
    if limit < min_limit:
        limit = min_limit
    elif limit > max_limit:
        limit = max_limit
    return 1 + 9 * (math.log(limit / min_limit) / math.log(max_limit / min_limit))


def american_to_probability(odds):
    """
    Convert American odds to a probability.

    Args:
        odds (int): The American odds.

    Returns:
        float: The probability.
    """
    if odds > 0:
        return 100 / (odds + 100)
    return -odds / (-odds + 100)


def devig(odds1, odds2, method):
    """
    Calculate the devigged probabilities for two odds.

    Args:
        odds1 (int): The first odds.
        odds2 (int): The second odds.
        method (DevigMethod): The method to use for devigging.

    Returns:
        tuple: The devigged probabilities for the two odds.
    """
    prob1 = american_to_probability(odds1)
    prob2 = american_to_probability(odds2)
    if method == DevigMethod.MULTIPLICATIVE:
        return prob1 / (prob1 + prob2)
    elif method == DevigMethod.POWER:
        def equation(p):
            return math.pow(prob1, p) + math.pow(prob2, p) - 1

        p = 1
        while equation(p) > 0:
            p += 0.005

        return math.pow(prob1, p)


def kelly_criterion(true_prob, fanduel_prob):
    """
    Calculate the optimal bet size using the Kelly criterion.

    Args:
        true_prob (float): The true probability of the event.
        fanduel_prob (float): The probability implied by the FanDuel odds.

    Returns:
        float: The optimal bet size as a fraction of the bankroll.
    """
    return true_prob - (1 - true_prob) / (1 / fanduel_prob - 1)
