from enum import Enum


class StatCategory(Enum):
    POINTS = 1
    REBOUNDS = 2
    THREE_PT = 3
    DOUBLE_DOUBLE = 4
    PRA = 5


class Wager:
    def __init__(self, game: str, fanduel_odds: int, pinnacle_odds: int, pinnacle_limit: int):
        """
        Initialize a Wager object.

        :param game: The name of the game (string).
        :param fanduel_odds: The odds from FanDuel (integer).
        :param pinnacle_odds: The odds from Pinnacle (integer).
        :param pinnacle_limit: The limit from Pinnacle (integer).
        """
        self.game = game
        self.fanduel_odds = fanduel_odds
        self.pinnacle_odds = pinnacle_odds
        self.pinnacle_limit = pinnacle_limit


class Moneyline(Wager):
    def __init__(self, game: str, fanduel_odds: int, pinnacle_odds: int, pinnacle_limit: int, team: str, opponent: str):
        """
        Initialize a Moneyline object, extending Wager with team and opponent fields.

        :param game: The name of the game (string).
        :param fanduel_odds: The odds from FanDuel (integer).
        :param pinnacle_odds: The odds from Pinnacle (integer).
        :param pinnacle_limit: The limit from Pinnacle (integer).
        :param team: The name of the team (string).
        :param opponent: The name of the opponent team (string).
        """
        super().__init__(game, fanduel_odds, pinnacle_odds, pinnacle_limit)
        self.team = team
        self.opponent = opponent

    def __repr__(self):
        """
        Provide a string representation of the Moneyline object.
        """
        return (f"Moneyline(game={self.game}, team={self.team}, opponent={self.opponent}, "
                f"fanduel_odds={self.fanduel_odds}, pinnacle_odds={self.pinnacle_odds}, "
                f"pinnacle_limit={self.pinnacle_limit})")


class PlayerProps(Wager):
    def __init__(self, game: str, fanduel_odds: int, pinnacle_odds: int, pinnacle_limit: int, player: str, stat: StatCategory, over_under: str, value: float):
        """
        Initialize a PlayerProps object, extending Wager with player, over_under, and value fields.

        :param game: The name of the game (string).
        :param fanduel_odds: The odds from FanDuel (integer).
        :param pinnacle_odds: The odds from Pinnacle (integer).
        :param pinnacle_limit: The limit from Pinnacle (integer).
        :param player: The name of the player (string).
        :param stat: The stat category (StatCategory).
        :param over_under: The over/under (string).
        :param value: The value (float).
        """
        super().__init__(game, fanduel_odds, pinnacle_odds, pinnacle_limit)
        self.player = player
        self.over_under = over_under
        self.stat = stat
        self.value = value

    def __repr__(self):
        """
        Provide a string representation of the PlayerProps object.
        """
        return (f"PlayerProps(game={self.game}, player={self.player}, over_under={self.over_under}, "
                f"value={self.value}, fanduel_odds={self.fanduel_odds}, pinnacle_odds={self.pinnacle_odds}, "
                f"pinnacle_limit={self.pinnacle_limit})")


class TeamTotal(Wager):
    def __init__(self, game: str, fanduel_odds: int, pinnacle_odds: int, pinnacle_limit: int, team: str, over_under: str, value: float):
        """
        Initialize a TeamTotal object, extending Wager with team, over_under, and value fields.

        :param game: The name of the game (string).
        :param fanduel_odds: The odds from FanDuel (integer).
        :param pinnacle_odds: The odds from Pinnacle (integer).
        :param pinnacle_limit: The limit from Pinnacle (integer).
        :param team: The name of the team (string).
        :param over_under: The over/under (string).
        :param value: The value (float).
        """
        super().__init__(game, fanduel_odds, pinnacle_odds, pinnacle_limit)
        self.team = team
        self.over_under = over_under
        self.value = value

    def __repr__(self):
        """
        Provide a string representation of the TeamTotal object.
        """
        return (f"TeamTotal(game={self.game}, team={self.team}, over_under={self.over_under}, "
                f"value={self.value}, fanduel_odds={self.fanduel_odds}, pinnacle_odds={self.pinnacle_odds}, "
                f"pinnacle_limit={self.pinnacle_limit})")


class Spread(Wager):
    def __init__(self, game: str, fanduel_odds: int, pinnacle_odds: int, pinnacle_limit: int, team: str, opponent: str, spread: float):
        """
        Initialize a Spread object, extending Wager with team, opponent, and spread fields.

        :param game: The name of the game (string).
        :param fanduel_odds: The odds from FanDuel (integer).
        :param pinnacle_odds: The odds from Pinnacle (integer).
        :param pinnacle_limit: The limit from Pinnacle (integer).
        :param team: The name of the team (string).
        :param opponent: The name of the opponent team (string).
        :param spread: The spread (float).
        """
        super().__init__(game, fanduel_odds, pinnacle_odds, pinnacle_limit)
        self.team = team
        self.opponent = opponent
        self.spread = spread

    def __repr__(self):
        """
        Provide a string representation of the Spread object.
        """
        return (f"Spread(game={self.game}, team={self.team}, opponent={self.opponent}, "
                f"spread={self.spread}, fanduel_odds={self.fanduel_odds}, pinnacle_odds={self.pinnacle_odds}, "
                f"pinnacle_limit={self.pinnacle_limit})")


class TotalPoints(Wager):
    def __init__(self, game: str, fanduel_odds: int, pinnacle_odds: int, pinnacle_limit: int, over_under: str, value: float):
        """
        Initialize a TotalPoints object, extending Wager with over_under and value fields.

        :param game: The name of the game (string).
        :param fanduel_odds: The odds from FanDuel (integer).
        :param pinnacle_odds: The odds from Pinnacle (integer).
        :param pinnacle_limit: The limit from Pinnacle (integer).
        :param over_under: The over/under (string).
        :param value: The value (float).
        """
        super().__init__(game, fanduel_odds, pinnacle_odds, pinnacle_limit)
        self.over_under = over_under
        self.value = value

    def __repr__(self):
        """
        Provide a string representation of the TotalPoints object.
        """
        return (f"TotalPoints(game={self.game}, over_under={self.over_under}, "
                f"value={self.value}, fanduel_odds={self.fanduel_odds}, pinnacle_odds={self.pinnacle_odds}, "
                f"pinnacle_limit={self.pinnacle_limit})")
