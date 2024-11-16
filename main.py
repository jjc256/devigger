from src.scrape import fanduel_nba, pinnacle_nba
from src.wager import Moneyline, PlayerProps, TeamTotal, Spread, TotalPoints, StatCategory

# Fetch data from Pinnacle and Fanduel
pinnacle = pinnacle_nba()
fanduel = fanduel_nba()

common_wagers = []

# Iterate through each game in Pinnacle data
for pinnacle_id in pinnacle:
    pinnacle_game = pinnacle[pinnacle_id]
    name = pinnacle_game["name"]
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
                        home_team, away_team = name.split(" @ ")
                        pinnacle_home_odds = pinnacle_wager["prices"][0]["price"]
                        pinnacle_away_odds = pinnacle_wager["prices"][1]["price"]
                        fanduel_home_odds = fanduel_wager["runners"][1]["winRunnerOdds"]
                        fanduel_away_odds = fanduel_wager["runners"][0]["winRunnerOdds"]
                        pinnacle_limit = pinnacle_wager["limit"]

                        # Create home moneyline object
                        home_moneyline = Moneyline(
                            name, fanduel_home_odds, pinnacle_home_odds, pinnacle_limit, home_team, away_team)

                        # Create away moneyline object
                        away_moneyline = Moneyline(
                            name, fanduel_away_odds, pinnacle_away_odds, pinnacle_limit, away_team, home_team)
                        break
