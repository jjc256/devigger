from enum import Enum


class League(Enum):
    NBA = 1
    NFL = 2
    NHL = 3
    NCAAFB = 4
    NCAAB = 5
    UCL = 6
    EPL = 7
    SHL = 8
    NL = 9
    TFL = 10
    TSL = 11
    J1 = 12
    L1 = 13
    IWF = 14
    GSL = 15
    CBA = 16
    AO = 17


class StatCategory(Enum):
    POINTS = 1
    REBOUNDS = 2
    THREE_PT = 3
    DOUBLE_DOUBLE = 4
    PRA = 5
    ASSISTS = 6
    FIRST_TD = 7
    ANYTIME_TD = 8
    LONGEST_RECEPTION = 9
    ANYTIME_GOAL = 10

    def pretty_name(self):
        if self == StatCategory.THREE_PT:
            return "Threes"
        elif self == StatCategory.FIRST_TD:
            return "First Touchdown"
        elif self == StatCategory.ANYTIME_TD:
            return "Anytime Touchdown"
        elif self == StatCategory.LONGEST_RECEPTION:
            return "Yards Longest Reception"
        elif self == StatCategory.ANYTIME_GOAL:
            return "Anytime Goal Scorer"
        return self.name.capitalize()


class OverUnder(Enum):
    OVER = 1
    UNDER = 2


class Wager:
    def __init__(self, game: str, fanduel_odds: int, pinnacle_odds: int, pinnacle_opposing_odds: int,
                 pinnacle_limit: int, external_market_id: str, selection_id: int, league: League):
        """
        Initialize a Wager object.

        :param game: The name of the game (string).
        :param fanduel_odds: The odds from FanDuel (integer).
        :param pinnacle_odds: The odds from Pinnacle (integer).
        :param pinnacle_opposing_odds: The opposing odds from Pinnacle (integer).
        :param pinnacle_limit: The limit from Pinnacle (integer).
        :param external_market_id: The external market ID (string).
        :param selection_id: The selection ID (integer).
        :param league: The league (League).
        """
        self.game = game
        self.fanduel_odds = fanduel_odds
        self.pinnacle_odds = pinnacle_odds
        self.pinnacle_opposing_odds = pinnacle_opposing_odds
        self.pinnacle_limit = pinnacle_limit
        self.external_market_id = external_market_id
        self.selection_id = selection_id
        self.league = league


class Moneyline(Wager):
    def __init__(self, game: str, fanduel_odds: int, pinnacle_odds: int, pinnacle_limit: int,
                 team: str, opponent: str, pinnacle_opposing_odds: int, pinnacle_draw_odds: int,
                 external_market_id: str, selection_id: int, league: League):
        """
        Initialize a Moneyline object, extending Wager with team and opponent fields.

        :param game: The name of the game (string).
        :param fanduel_odds: The odds from FanDuel (integer).
        :param pinnacle_odds: The odds from Pinnacle (integer).
        :param pinnacle_limit: The limit from Pinnacle (integer).
        :param team: The name of the team (string).
        :param opponent: The name of the opponent team (string).
        :param pinnacle_opposing_odds: The opposing odds from Pinnacle (integer).
        :param pinnacle_draw_odds: The draw odds from Pinnacle (integer). Default to 0 for no draw odds.
        :param external_market_id: The external market ID (string).
        :param selection_id: The selection ID (integer).
        :param league: The league (League).
        """
        super().__init__(game, fanduel_odds, pinnacle_odds,
                         pinnacle_opposing_odds, pinnacle_limit, external_market_id, selection_id, league)
        self.team = team
        self.opponent = opponent
        self.pinnacle_draw_odds = pinnacle_draw_odds

    def __repr__(self):
        """
        Provide a string representation of the Moneyline object.
        """
        return (f"Moneyline(game={self.game}, team={self.team}, opponent={self.opponent}, "
                f"fanduel_odds={self.fanduel_odds}, pinnacle_odds={self.pinnacle_odds}, "
                f"pinnacle_opposing_odds={self.pinnacle_opposing_odds}, " +
                (f"pinnacle_draw_odds={self.pinnacle_draw_odds}, " if " v " in self.game else "") +
                f"pinnacle_limit={self.pinnacle_limit}, league={self.league})")

    def pretty(self):
        """
        Provide a pretty string representation of the Moneyline object.
        """
        return f"{self.team} Moneyline {self.game}"


class Draw(Wager):
    def __init__(self, game: str, fanduel_draw_odds: int, pinnacle_odds: int, pinnacle_home_odds: int, pinnacle_away_odds: int,
                 pinnacle_limit: int, external_market_id: str, selection_id: int, league: League):
        """
        Initialize a Draw object, extending Wager with team and opponent fields.

        :param game: The name of the game (string).
        :param fanduel_draw_odds: The odds from FanDuel (integer).
        :param pinnacle_odds: The odds from Pinnacle (integer).
        :param pinnacle_home_odds: The home odds from Pinnacle (integer).
        :param pinnacle_away_odds: The away odds from Pinnacle (integer).
        :param pinnacle_limit: The limit from Pinnacle (integer).
        :param pinnacle_opposing_odds: The opposing odds from Pinnacle (integer). Set to 0 because there is no opposing team.
        :param external_market_id: The external market ID (string).
        :param selection_id: The selection ID (integer).
        :param league: The league (League).
        """
        super().__init__(game, fanduel_draw_odds, pinnacle_odds,
                         0, pinnacle_limit, external_market_id, selection_id, league)
        self.pinnacle_home_odds = pinnacle_home_odds
        self.pinnacle_away_odds = pinnacle_away_odds

    def __repr__(self):
        """
        Provide a string representation of the Draw object.
        """
        return (f"Draw(game={self.game}, fanduel_draw_odds={self.fanduel_odds}, pinnacle_odds={self.pinnacle_odds}, "
                f"pinnacle_home_odds={self.pinnacle_home_odds}, pinnacle_away_odds={self.pinnacle_away_odds}, "
                f"pinnacle_limit={self.pinnacle_limit}, league={self.league})")

    def pretty(self):
        """
        Provide a pretty string representation of the Draw object.
        """
        return f"Draw {self.game}"


class PlayerProps(Wager):
    def __init__(self, game: str, fanduel_odds: int, pinnacle_odds: int, pinnacle_limit: int, player: str,
                 stat: StatCategory, over_under: OverUnder, value: float, pinnacle_opposing_odds: int,
                 external_market_id: str, selection_id: int, league: League):
        """
        Initialize a PlayerProps object, extending Wager with player, over_under, and value fields.

        :param game: The name of the game (string).
        :param fanduel_odds: The odds from FanDuel (integer).
        :param pinnacle_odds: The odds from Pinnacle (integer).
        :param pinnacle_limit: The limit from Pinnacle (integer).
        :param player: The name of the player (string).
        :param stat: The stat category (StatCategory).
        :type stat: StatCategory
        :param over_under: The over/under (OverUnder).
        :type over_under: OverUnder
        :param value: The value (float).
        :param pinnacle_opposing_odds: The opposing odds from Pinnacle (integer).
        :param external_market_id: The external market ID (string).
        :param selection_id: The selection ID (integer).
        :param league: The league (League).
        """
        super().__init__(game, fanduel_odds, pinnacle_odds,
                         pinnacle_opposing_odds, pinnacle_limit, external_market_id, selection_id, league)
        self.player = player
        self.over_under = over_under
        self.stat = stat
        self.value = value

    def __repr__(self):
        """
        Provide a string representation of the PlayerProps object.
        """
        return (f"PlayerProps(game={self.game}, player={self.player}, stat={self.stat}, over_under={self.over_under}, "
                f"value={self.value}, fanduel_odds={self.fanduel_odds}, pinnacle_odds={self.pinnacle_odds}, "
                f"pinnacle_opposing_odds={self.pinnacle_opposing_odds}, pinnacle_limit={self.pinnacle_limit}, league={self.league})")

    def pretty(self):
        """
        Provide a pretty string representation of the PlayerProps object.
        """
        return f"{self.player} {self.value}+ {self.stat.pretty_name()} {self.game}"


class PlayerPropsYes(Wager):
    def __init__(self, game: str, fanduel_odds: int, pinnacle_odds: int, pinnacle_limit: int, player: str,
                 stat: StatCategory, pinnacle_opposing_odds: int, external_market_id: str, selection_id: int, league: League):
        """
        Initialize a PlayerPropsYesNo object, extending Wager with player and yes_no fields.

        :param game: The name of the game (string).
        :param fanduel_odds: The odds from FanDuel (integer).
        :param pinnacle_odds: The odds from Pinnacle (integer).
        :param pinnacle_limit: The limit from Pinnacle (integer).
        :param player: The name of the player (string).
        :param stat: The stat category (StatCategory).
        :type stat: StatCategory
        :param pinnacle_opposing_odds: The opposing odds from Pinnacle (integer).
        :param external_market_id: The external market ID (string).
        :param selection_id: The selection ID (integer).
        :param league: The league (League).
        """
        super().__init__(game, fanduel_odds, pinnacle_odds,
                         pinnacle_opposing_odds, pinnacle_limit, external_market_id, selection_id, league)
        self.player = player
        self.stat = stat

    def __repr__(self):
        """
        Provide a string representation of the PlayerPropsYesNo object.
        """
        return (f"PlayerPropsYesNo(game={self.game}, player={self.player}, stat={self.stat}, "
                f"fanduel_odds={self.fanduel_odds}, pinnacle_odds={self.pinnacle_odds}, "
                f"pinnacle_opposing_odds={self.pinnacle_opposing_odds}, pinnacle_limit={self.pinnacle_limit}, league={self.league})")

    def pretty(self):
        """
        Provide a pretty string representation of the PlayerPropsYesNo object.
        """
        return f"{self.player} {self.stat.pretty_name()} {self.game}"


class TeamTotal(Wager):
    def __init__(self, game: str, fanduel_odds: int, pinnacle_odds: int, pinnacle_limit: int, team: str,
                 over_under: OverUnder, value: float, pinnacle_opposing_odds: int, external_market_id: str, selection_id: int, league: League):
        """
        Initialize a TeamTotal object, extending Wager with team, over_under, and value fields.

        :param game: The name of the game (string).
        :param fanduel_odds: The odds from FanDuel (integer).
        :param pinnacle_odds: The odds from Pinnacle (integer).
        :param pinnacle_limit: The limit from Pinnacle (integer).
        :param team: The name of the team (string).
        :param over_under: The over/under (OverUnder).
        :param value: The value (float).
        :param pinnacle_opposing_odds: The opposing odds from Pinnacle (integer).
        :param external_market_id: The external market ID (string).
        :param selection_id: The selection ID (integer).
        :param league: The league (League).
        """
        super().__init__(game, fanduel_odds, pinnacle_odds,
                         pinnacle_opposing_odds, pinnacle_limit, external_market_id, selection_id, league)
        self.team = team
        self.over_under = over_under
        self.value = value

    def __repr__(self):
        """
        Provide a string representation of the TeamTotal object.
        """
        return (f"TeamTotal(game={self.game}, team={self.team}, over_under={self.over_under}, "
                f"value={self.value}, fanduel_odds={self.fanduel_odds}, pinnacle_odds={self.pinnacle_odds}, "
                f"pinnacle_opposing_odds={self.pinnacle_opposing_odds}, pinnacle_limit={self.pinnacle_limit}, league={self.league})")

    def pretty(self):
        """
        Provide a pretty string representation of the TeamTotal object.
        """
        return f"{self.team} {self.over_under.name.capitalize()} {self.value} points {self.game}"


class Spread(Wager):
    def __init__(self, game: str, fanduel_odds: int, pinnacle_odds: int, pinnacle_limit: int,
                 team: str, opponent: str, spread: float, pinnacle_opposing_odds: int, external_market_id: str, selection_id: int, league: League):
        """
        Initialize a Spread object, extending Wager with team, opponent, and spread fields.

        :param game: The name of the game (string).
        :param fanduel_odds: The odds from FanDuel (integer).
        :param pinnacle_odds: The odds from Pinnacle (integer).
        :param pinnacle_limit: The limit from Pinnacle (integer).
        :param team: The name of the team (string).
        :param opponent: The name of the opponent team (string).
        :param spread: The spread (float).
        :param pinnacle_opposing_odds: The opposing odds from Pinnacle (integer).
        :param external_market_id: The external market ID (string).
        :param selection_id: The selection ID (integer).
        :param league: The league (League).
        """
        super().__init__(game, fanduel_odds, pinnacle_odds,
                         pinnacle_opposing_odds, pinnacle_limit, external_market_id, selection_id, league)
        self.team = team
        self.opponent = opponent
        self.spread = spread

    def __repr__(self):
        """
        Provide a string representation of the Spread object.
        """
        return (f"Spread(game={self.game}, team={self.team}, opponent={self.opponent}, "
                f"spread={self.spread}, fanduel_odds={self.fanduel_odds}, pinnacle_odds={self.pinnacle_odds}, "
                f"pinnacle_opposing_odds={self.pinnacle_opposing_odds}, pinnacle_limit={self.pinnacle_limit}, league={self.league})")

    def pretty(self):
        """
        Provide a pretty string representation of the Spread object.
        """
        return f"{self.team} {'+' if self.spread > 0 else ''}{self.spread} Handicap {self.game}"


class TotalPoints(Wager):
    def __init__(self, game: str, fanduel_odds: int, pinnacle_odds: int, pinnacle_limit: int,
                 over_under: OverUnder, value: float, pinnacle_opposing_odds: int, external_market_id: str, selection_id: int, league: League):
        """
        Initialize a TotalPoints object, extending Wager with over_under and value fields.

        :param game: The name of the game (string).
        :param fanduel_odds: The odds from FanDuel (integer).
        :param pinnacle_odds: The odds from Pinnacle (integer).
        :param pinnacle_limit: The limit from Pinnacle (integer).
        :param over_under: The over/under (OverUnder).
        :param value: The value (float).
        :param pinnacle_opposing_odds: The opposing odds from Pinnacle (integer).
        :param external_market_id: The external market ID (string).
        :param selection_id: The selection ID (integer).
        :param league: The league (League).
        """
        super().__init__(game, fanduel_odds, pinnacle_odds,
                         pinnacle_opposing_odds, pinnacle_limit, external_market_id, selection_id, league)
        self.over_under = over_under
        self.value = value

    def __repr__(self):
        """
        Provide a string representation of the TotalPoints object.
        """
        return (f"TotalPoints(game={self.game}, over_under={self.over_under}, "
                f"value={self.value}, fanduel_odds={self.fanduel_odds}, pinnacle_odds={self.pinnacle_odds}, "
                f"pinnacle_opposing_odds={self.pinnacle_opposing_odds}, pinnacle_limit={self.pinnacle_limit}, league={self.league})")

    def pretty(self):
        """
        Provide a pretty string representation of the TotalPoints object.
        """
        return f"{self.over_under.name.capitalize()} {self.value} Total Points {self.game}"
