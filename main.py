from src.scrape import fanduel_nba, pinnacle_nba
from src.wager import Moneyline, PlayerProps, TeamTotal, Spread, TotalPoints, StatCategory, OverUnder
from src.devig import devig, DevigMethod, american_to_probability, kelly_criterion, get_confidence_value

# Fetch data from Pinnacle and Fanduel
pinnacle = pinnacle_nba()
fanduel = fanduel_nba()

common_wagers = []

# Iterate through each game in Pinnacle data
for pinnacle_id in pinnacle:
    pinnacle_game = pinnacle[pinnacle_id]
    name = pinnacle_game["name"]
    away_team, home_team = name.split(" @ ")
    fanduel_game = None

    # Find the corresponding game in Fanduel data
    for fanduel_id in fanduel:
        if fanduel[fanduel_id]["name"] == name:
            fanduel_game = fanduel[fanduel_id]
            break

    if fanduel_game:
        # Iterate through each market in Pinnacle game
        for pinnacle_wager in pinnacle_game["markets"]:
            description = pinnacle_wager["description"]

            if description == "moneyline":
                # Find the corresponding market in Fanduel game
                for fanduel_wager in fanduel_game["markets"]:
                    if fanduel_wager["marketType"] == "MONEY_LINE":
                        pinnacle_home_odds = pinnacle_wager["prices"][0]["price"]
                        pinnacle_away_odds = pinnacle_wager["prices"][1]["price"]
                        fanduel_home_odds = fanduel_wager["runners"][1]["winRunnerOdds"]
                        fanduel_away_odds = fanduel_wager["runners"][0]["winRunnerOdds"]
                        pinnacle_limit = pinnacle_wager["limit"]

                        # Create home moneyline object
                        home_moneyline = Moneyline(
                            name, fanduel_home_odds, pinnacle_home_odds, pinnacle_limit, home_team, away_team, pinnacle_away_odds)

                        # Create away moneyline object
                        away_moneyline = Moneyline(
                            name, fanduel_away_odds, pinnacle_away_odds, pinnacle_limit, away_team, home_team, pinnacle_home_odds)

                        common_wagers.append(home_moneyline)
                        common_wagers.append(away_moneyline)
                        break
            elif description == "handicap":
                home_handicap = abs(pinnacle_wager["prices"][0]["handicap"])
                # Find the corresponding market in Fanduel game
                for fanduel_wager in fanduel_game["markets"]:
                    if fanduel_wager["marketType"] == "MATCH_HANDICAP_(2-WAY)" and fanduel_wager["runners"][1]["handicap"] == home_handicap:
                        pinnacle_home_odds = pinnacle_wager["prices"][0]["price"]
                        pinnacle_away_odds = pinnacle_wager["prices"][1]["price"]
                        fanduel_home_odds = fanduel_wager["runners"][1]["winRunnerOdds"]
                        fanduel_away_odds = fanduel_wager["runners"][0]["winRunnerOdds"]
                        pinnacle_limit = pinnacle_wager["limit"]

                        # Create home spread object
                        home_spread = Spread(
                            name, fanduel_home_odds, pinnacle_home_odds, pinnacle_limit, home_team, away_team, home_handicap, pinnacle_away_odds)

                        # Create away spread object
                        away_spread = Spread(
                            name, fanduel_away_odds, pinnacle_away_odds, pinnacle_limit, away_team, home_team, -home_handicap, pinnacle_home_odds)

                        common_wagers.append(home_spread)
                        common_wagers.append(away_spread)
                        break
            elif description == "total points":
                threshold = float(pinnacle_wager["threshold"])
                for fanduel_wager in fanduel_game["markets"]:
                    if fanduel_wager["marketType"] == "TOTAL_POINTS_(OVER/UNDER)" and threshold == fanduel_wager["runners"][0]["handicap"]:
                        pinnacle_over_odds = pinnacle_wager["prices"][0]["price"]
                        pinnacle_under_odds = pinnacle_wager["prices"][1]["price"]
                        fanduel_over_odds = fanduel_wager["runners"][0]["winRunnerOdds"]
                        fanduel_under_odds = fanduel_wager["runners"][1]["winRunnerOdds"]
                        pinnacle_limit = pinnacle_wager["limit"]

                        # Create over total points object
                        over_total_points = TotalPoints(
                            name, fanduel_over_odds, pinnacle_over_odds, pinnacle_limit, OverUnder.OVER, threshold, pinnacle_under_odds)

                        # Create under total points object
                        under_total_points = TotalPoints(
                            name, fanduel_under_odds, pinnacle_under_odds, pinnacle_limit, OverUnder.UNDER, threshold, pinnacle_over_odds)

                        common_wagers.append(over_total_points)
                        common_wagers.append(under_total_points)
                        break
            elif description == "team total":
                # there are no team total market easily accessible on fanduel data
                pass
            elif " (" in description and description.endswith(")"):
                # Check for player props markets (e.g., "Player Name (Category)")
                player_name, raw_category = description.split(" (")
                category = raw_category.rstrip(")")
                category = category.rstrip(")")
                fanduel_category_map = {
                    "Assists": "TO_RECORD_{}+_ASSISTS",
                    "3 Point FG": "{}+_MADE_THREES",
                    "Points": "TO_SCORE_{}+_POINTS",
                    "Rebounds": "TO_SCORE_{}+_REBOUNDS"
                }
                # Round N up to the nearest integer
                N = int(pinnacle_wager["prices"][0]["points"] + 1)
                fanduel_category_template = fanduel_category_map.get(category)
                if fanduel_category_template:
                    for fanduel_wager in fanduel_game["markets"]:
                        if fanduel_wager["marketType"] != fanduel_category_template.format(N):
                            continue
                        for runner in fanduel_wager["runners"]:
                            if fanduel_wager["marketType"].startswith(fanduel_category_template.split("{}")[0]):
                                if runner["runnerName"] == player_name:
                                    pinnacle_over_odds = pinnacle_wager["prices"][0]["price"]
                                    pinnacle_under_odds = pinnacle_wager["prices"][1]["price"]
                                    fanduel_odds = runner["winRunnerOdds"]
                                    pinnacle_limit = pinnacle_wager["limit"]

                                    # Create player props over object
                                    player_props_over = PlayerProps(
                                        name, fanduel_odds, pinnacle_over_odds, pinnacle_limit,
                                        player_name, category, OverUnder.OVER, N, pinnacle_under_odds
                                    )
                                    common_wagers.append(player_props_over)
                                    break

for wager in common_wagers:
    true_prob = devig(wager.pinnacle_odds,
                      wager.pinnacle_opposing_odds, DevigMethod.POWER)
    fanduel_prob = american_to_probability(wager.fanduel_odds)
    if true_prob > fanduel_prob:
        ev = (true_prob - fanduel_prob) / fanduel_prob * 100
        kelly_percentage = kelly_criterion(true_prob, fanduel_prob) * 100
        risk_percentage = kelly_percentage * get_confidence_value(wager.pinnacle_limit)
        print(wager.pretty())
        print(f"EV: {ev:.2f}%")
        print(f"Risk: {risk_percentage:.2f}%")
        print()
