import tkinter as tk
from src.scrape import *
from src.wager import *
from src.devig import *
from datetime import datetime
import sys
import webbrowser
from src.sheet_operations import write_to_sheet


# Default to 1000 if no argument provided
BANKROLL = float(sys.argv[1]) if len(sys.argv) > 1 else 1000


def game_names_equal(game1, game2):
    if " @ " in game1:
        team1_1, team1_2 = game1.split(" @ ")
    elif " v " in game1:
        team1_1, team1_2 = game1.split(" v ")
    if " @ " in game2:
        team2_1, team2_2 = game2.split(" @ ")
    elif " v " in game2:
        team2_1, team2_2 = game2.split(" v ")
    return (team1_1 in team2_1 or team2_1 in team1_1) and (team1_2 in team2_2 or team2_2 in team1_2)


def wagers():
    # Fetch data from Pinnacle and Fanduel
    pinnacle = {
        **pinnacle_nba(),
        **pinnacle_nfl(),
        **pinnacle_nhl(),
        **pinnacle_ncaaf(),
        **pinnacle_ncaab(),
        **pinnacle_ucl(),
        **pinnacle_epl(),
        **pinnacle_shl(),
        **pinnacle_nla(),
        **pinnacle_turkish_first(),
        **pinnacle_turkish_super(),
        **pinnacle_j1(),
        **pinnacle_ligue1(),
        **pinnacle_women_friendlies()
    }
    fanduel = {
        **fanduel_nba(),
        **fanduel_nfl(),
        **fanduel_nhl(),
        **fanduel_ncaaf(),
        **fanduel_ncaab(),
        **fanduel_ucl(),
        **fanduel_epl(),
        **fanduel_shl(),
        **fanduel_nla(),
        **fanduel_turkish_first(),
        **fanduel_turkish_super(),
        **fanduel_j1(),
        **fanduel_ligue1(),
        **fanduel_women_friendlies()
    }

    common_wagers = []

    # Iterate through each game in Pinnacle data
    for pinnacle_id in pinnacle:
        pinnacle_game = pinnacle[pinnacle_id]
        name = pinnacle_game["name"]
        away_team, home_team = name.split(" @ ") if " @ " in name else name.split(" v ")[::-1]
        fanduel_game = None

        # Find the corresponding game in Fanduel data
        for fanduel_id in fanduel:
            if game_names_equal(name, fanduel[fanduel_id]["name"]):
                fanduel_game = fanduel[fanduel_id]
                break

        if fanduel_game:
            # Iterate through each market in Pinnacle game
            for pinnacle_wager in pinnacle_game["markets"]:
                if pinnacle_wager.get("prices") is None:
                    continue
                description = pinnacle_wager["description"]

                if description == "moneyline":
                    # Find the corresponding market in Fanduel game
                    for fanduel_wager in fanduel_game["markets"]:
                        external_market_id = fanduel_wager["externalMarketId"]
                        if fanduel_wager["marketType"] == "MONEY_LINE":
                            pinnacle_home_odds = pinnacle_wager["prices"][0]["price"]
                            pinnacle_away_odds = pinnacle_wager["prices"][1]["price"]
                            home_index = 1 if " @ " in name else 0
                            fanduel_home_odds = fanduel_wager["runners"][home_index]["winRunnerOdds"]
                            fanduel_away_odds = fanduel_wager["runners"][1 -
                                                                         home_index]["winRunnerOdds"]
                            pinnacle_limit = pinnacle_wager["limit"]
                            home_selection_id = fanduel_wager["runners"][home_index]["selectionId"]
                            away_selection_id = fanduel_wager["runners"][1 -
                                                                         home_index]["selectionId"]

                            # Create home moneyline object
                            home_moneyline = Moneyline(
                                name, fanduel_home_odds, pinnacle_home_odds, pinnacle_limit,
                                home_team, away_team, pinnacle_away_odds, 0, external_market_id, home_selection_id)

                            # Create away moneyline object
                            away_moneyline = Moneyline(
                                name, fanduel_away_odds, pinnacle_away_odds, pinnacle_limit,
                                away_team, home_team, pinnacle_home_odds, 0, external_market_id, away_selection_id)

                            common_wagers.append(home_moneyline)
                            common_wagers.append(away_moneyline)
                            break
                        elif fanduel_wager["marketType"] == "WIN-DRAW-WIN":
                            pinnacle_home_odds = pinnacle_wager["prices"][0]["price"]
                            pinnacle_away_odds = pinnacle_wager["prices"][1]["price"]
                            pinnacle_draw_odds = pinnacle_wager["prices"][2]["price"]
                            fanduel_home_odds = fanduel_wager["runners"][0]["winRunnerOdds"]
                            fanduel_away_odds = fanduel_wager["runners"][2]["winRunnerOdds"]
                            fanduel_draw_odds = fanduel_wager["runners"][1]["winRunnerOdds"]
                            pinnacle_limit = pinnacle_wager["limit"]

                            home_selection_id = fanduel_wager["runners"][0]["selectionId"]
                            away_selection_id = fanduel_wager["runners"][2]["selectionId"]
                            draw_selection_id = fanduel_wager["runners"][1]["selectionId"]

                            # Create home moneyline object
                            home_moneyline = Moneyline(
                                name, fanduel_home_odds, pinnacle_home_odds, pinnacle_limit,
                                home_team, away_team, pinnacle_away_odds, pinnacle_draw_odds,
                                external_market_id, home_selection_id)

                            # Create away moneyline object
                            away_moneyline = Moneyline(
                                name, fanduel_away_odds, pinnacle_away_odds, pinnacle_limit,
                                away_team, home_team, pinnacle_home_odds, pinnacle_draw_odds,
                                external_market_id, away_selection_id)

                            # Create draw moneyline object
                            draw_moneyline = Draw(
                                name, fanduel_draw_odds, pinnacle_draw_odds, pinnacle_home_odds,
                                pinnacle_away_odds, pinnacle_limit, external_market_id, draw_selection_id)

                            common_wagers.append(home_moneyline)
                            common_wagers.append(away_moneyline)
                            common_wagers.append(draw_moneyline)
                            break
                elif description == "handicap":
                    home_handicap = pinnacle_wager["prices"][0]["handicap"]
                    # Find the corresponding market in Fanduel game
                    for fanduel_wager in fanduel_game["markets"]:
                        external_market_id = fanduel_wager["externalMarketId"]
                        if fanduel_wager["marketType"] == "MATCH_HANDICAP_(2-WAY)" and fanduel_wager["runners"][1]["handicap"] == home_handicap:
                            pinnacle_home_odds = pinnacle_wager["prices"][0]["price"]
                            pinnacle_away_odds = pinnacle_wager["prices"][1]["price"]
                            fanduel_home_odds = fanduel_wager["runners"][1]["winRunnerOdds"]
                            fanduel_away_odds = fanduel_wager["runners"][0]["winRunnerOdds"]
                            pinnacle_limit = pinnacle_wager["limit"]

                            home_selection_id = fanduel_wager["runners"][1]["selectionId"]
                            away_selection_id = fanduel_wager["runners"][0]["selectionId"]

                            # Create home spread object
                            home_spread = Spread(
                                name, fanduel_home_odds, pinnacle_home_odds, pinnacle_limit,
                                home_team, away_team, home_handicap, pinnacle_away_odds, external_market_id, home_selection_id)

                            # Create away spread object
                            away_spread = Spread(
                                name, fanduel_away_odds, pinnacle_away_odds, pinnacle_limit,
                                away_team, home_team, -home_handicap, pinnacle_home_odds, external_market_id, away_selection_id)

                            common_wagers.append(home_spread)
                            common_wagers.append(away_spread)
                            break
                elif description == "total points":
                    threshold = float(pinnacle_wager["threshold"])
                    for fanduel_wager in fanduel_game["markets"]:
                        external_market_id = fanduel_wager["externalMarketId"]
                        if fanduel_wager["marketType"] == "TOTAL_POINTS_(OVER/UNDER)" and threshold == fanduel_wager["runners"][0]["handicap"]:
                            pinnacle_over_odds = pinnacle_wager["prices"][0]["price"]
                            pinnacle_under_odds = pinnacle_wager["prices"][1]["price"]
                            fanduel_over_odds = fanduel_wager["runners"][0]["winRunnerOdds"]
                            fanduel_under_odds = fanduel_wager["runners"][1]["winRunnerOdds"]
                            pinnacle_limit = pinnacle_wager["limit"]

                            over_selection_id = fanduel_wager["runners"][0]["selectionId"]
                            under_selection_id = fanduel_wager["runners"][1]["selectionId"]

                            # Create over total points object
                            over_total_points = TotalPoints(
                                name, fanduel_over_odds, pinnacle_over_odds, pinnacle_limit, OverUnder.OVER,
                                threshold, pinnacle_under_odds, external_market_id, over_selection_id)

                            # Create under total points object
                            under_total_points = TotalPoints(
                                name, fanduel_under_odds, pinnacle_under_odds, pinnacle_limit, OverUnder.UNDER,
                                threshold, pinnacle_over_odds, external_market_id, under_selection_id)

                            common_wagers.append(over_total_points)
                            common_wagers.append(under_total_points)
                            break
                elif description == "team total":
                    # there are no team total market easily accessible on fanduel data
                    pass
                elif " (" in description and description.endswith(")"):
                    # Check for player props markets (e.g., "Player Name (Category)")
                    player_name, raw_category = description.rsplit(" (", 1)
                    category = raw_category.rstrip(")")
                    category = category.rstrip(")")
                    fanduel_category_map = {
                        "Assists": "TO_RECORD_{}+_ASSISTS",
                        "3 Point FG": "{}+_MADE_THREES",
                        "Points": "TO_SCORE_{}+_POINTS",
                        "Rebounds": "TO_SCORE_{}+_REBOUNDS",
                        "1st TD Scorer": "FIRST_TOUCHDOWN_SCORER",
                        "Anytime TD": "ANY_TIME_TOUCHDOWN_SCORER",
                        "Longest Reception": "PLAYERS_WITH_{}+_YARDS_RECEPTION",
                        "Goals": "placeholder"
                    }
                    # Round N up to the nearest integer
                    if "points" in pinnacle_wager["prices"][0]:
                        N = int(pinnacle_wager["prices"][0]["points"] + 1)
                    else:
                        continue
                    fanduel_category_template = fanduel_category_map.get(category)
                    stat_category = (
                        StatCategory.POINTS if category == "Points" else
                        StatCategory.REBOUNDS if category == "Rebounds" else
                        StatCategory.THREE_PT if category == "3 Point FG" else
                        StatCategory.ASSISTS if category == "Assists" else
                        StatCategory.FIRST_TD if category == "1st TD Scorer" else
                        StatCategory.ANYTIME_TD if category == "Anytime TD" else
                        StatCategory.LONGEST_RECEPTION if category == "Longest Reception" else
                        StatCategory.ANYTIME_GOAL if category == "Goals"
                        else None
                    )
                    if fanduel_category_template and "{}" in fanduel_category_template:
                        for fanduel_wager in fanduel_game["markets"]:
                            external_market_id = fanduel_wager["externalMarketId"]
                            if fanduel_wager["marketType"] != fanduel_category_template.format(N):
                                continue
                            for runner in fanduel_wager["runners"]:
                                if fanduel_wager["marketType"].startswith(fanduel_category_template.split("{}")[0]):
                                    if runner["runnerName"] == player_name:
                                        pinnacle_over_odds = pinnacle_wager["prices"][0]["price"]
                                        pinnacle_under_odds = pinnacle_wager["prices"][1]["price"]
                                        fanduel_odds = runner["winRunnerOdds"]
                                        pinnacle_limit = pinnacle_wager["limit"]

                                        over_selection_id = runner["selectionId"]

                                        # Create player props over object
                                        player_props_over = PlayerProps(
                                            name, fanduel_odds, pinnacle_over_odds, pinnacle_limit,
                                            player_name, stat_category, OverUnder.OVER, N, pinnacle_under_odds,
                                            external_market_id, over_selection_id
                                        )
                                        common_wagers.append(player_props_over)
                                        break
                    # yes/no player props
                    elif fanduel_category_template:
                        if category == "Goals" and N == 1:
                            for fanduel_wager in fanduel_game["markets"]:
                                if fanduel_wager["marketType"] != "ANY_TIME_GOAL_SCORER":
                                    continue
                                for runner in fanduel_wager["runners"]:
                                    if runner["runnerName"] == player_name:
                                        external_market_id = fanduel_wager["externalMarketId"]
                                        pinnacle_yes_odds = pinnacle_wager["prices"][0]["price"]
                                        pinnacle_no_odds = pinnacle_wager["prices"][1]["price"]
                                        fanduel_odds = runner["winRunnerOdds"]
                                        pinnacle_limit = pinnacle_wager["limit"]

                                        yes_selection_id = fanduel_wager["runners"][0]["selectionId"]

                                        # Create player props yes object
                                        player_props_yes = PlayerPropsYes(
                                            name, fanduel_odds, pinnacle_yes_odds, pinnacle_limit,
                                            player_name, stat_category, pinnacle_no_odds, external_market_id, yes_selection_id
                                        )

                                        common_wagers.append(player_props_yes)
                                        break

                        else:
                            for fanduel_wager in fanduel_game["markets"]:
                                external_market_id = fanduel_wager["externalMarketId"]
                                if fanduel_wager["marketType"] != fanduel_category_template.format(N):
                                    continue
                                for runner in fanduel_wager["runners"]:
                                    if fanduel_wager["marketType"].startswith(fanduel_category_template.split("{}")[0]):
                                        if runner["runnerName"] == player_name:
                                            pinnacle_yes_odds = pinnacle_wager["prices"][0]["price"]
                                            pinnacle_no_odds = pinnacle_wager["prices"][1]["price"]
                                            fanduel_odds = runner["winRunnerOdds"]
                                            pinnacle_limit = pinnacle_wager["limit"]

                                            yes_selection_id = fanduel_wager["runners"][0]["selectionId"]

                                            # Create player props yes object
                                            player_props_yes = PlayerPropsYes(
                                                name, fanduel_odds, pinnacle_yes_odds, pinnacle_limit,
                                                player_name, stat_category, pinnacle_no_odds, external_market_id, yes_selection_id
                                            )

                                            common_wagers.append(player_props_yes)
                                            break
    return common_wagers


def display_good_bets(devig_method=DevigMethod.POWER):
    common_wagers = wagers()
    good_bets = []

    for wager in common_wagers:
        if " @ " in wager.game:
            true_prob = devig(wager.pinnacle_odds, wager.pinnacle_opposing_odds, devig_method)
        elif isinstance(wager, Draw):
            true_prob = devig3(wager.pinnacle_odds, wager.pinnacle_home_odds,
                               wager.pinnacle_away_odds, devig_method)
        elif isinstance(wager, Moneyline):
            true_prob = devig3(wager.pinnacle_odds, wager.pinnacle_opposing_odds,
                               wager.pinnacle_draw_odds, devig_method)
        if (wager.fanduel_odds is None):
            continue
        fanduel_prob = american_to_probability(wager.fanduel_odds)
        if true_prob > fanduel_prob:
            ev = (true_prob - fanduel_prob) / fanduel_prob * 100
            kelly_percentage = kelly_criterion(true_prob, fanduel_prob) * 100
            risk_percentage = min(5, kelly_percentage *
                                  get_confidence_value(wager.pinnacle_limit) / 10)
            good_bets.append((wager, ev, risk_percentage))

    return good_bets


def change_devig_method(devig_method, common_wagers):
    good_bets = []

    for wager in common_wagers:
        if " @ " in wager.game:
            true_prob = devig(wager.pinnacle_odds, wager.pinnacle_opposing_odds, devig_method)
        else:
            true_prob = devig3(wager.pinnacle_draw_odds, wager.pinnacle_home_odds,
                               wager.pinnacle_away_odds, devig_method)
        fanduel_prob = american_to_probability(wager.fanduel_odds)
        if true_prob > fanduel_prob:
            ev = (true_prob - fanduel_prob) / fanduel_prob * 100
            kelly_percentage = kelly_criterion(true_prob, fanduel_prob) * 100
            risk_percentage = kelly_percentage * get_confidence_value(wager.pinnacle_limit)
            good_bets.append((wager, ev, risk_percentage))

    return good_bets


def show_details(wager, details_label):
    details = wager
    details_label.config(text=details)


def on_mouse_wheel(event, canvas):
    canvas.yview_scroll(int(-1*(event.delta/120)), "units")


def toggle_details(event, wager, ev, risk_percentage, bet_label):
    current_text = bet_label.cget("text")
    detailed_text = str(wager)
    if current_text == detailed_text:
        bet_label.config(
            text=f"{wager.pretty()}\nFanduel Odds: {wager.fanduel_odds}\nEV: {ev:.2f}%\nRisk: {risk_percentage:.2f}% (${int(2 * risk_percentage / 100 * BANKROLL + 1) / 2}0)")
        current_text
    else:
        bet_label.config(text=detailed_text)
        current_text = detailed_text


def copy_to_clipboard(root, text):
    root.clipboard_clear()
    root.clipboard_append(text)
    root.update()  # now it stays on the clipboard after the window is closed


def open_betslip(external_market_id, selection_id):
    url = f"https://sportsbook.fanduel.com/addToBetslip?marketId[0]={external_market_id}&selectionId[0]={selection_id}"
    webbrowser.open_new_tab(url)


def reload_data(root, canvas, scrollable_frame, devig_method):
    for widget in scrollable_frame.winfo_children():
        widget.destroy()

    good_bets = display_good_bets(devig_method)
    good_bets.sort(key=lambda x: x[2], reverse=True)  # Sort by risk_percentage

    row = 0
    col = 0
    for wager, ev, risk_percentage in good_bets:
        bet_frame = tk.Frame(scrollable_frame, borderwidth=2,
                             relief="groove", width=280, height=200)
        # Add background color if FanDuel odds meet condition
        if wager.fanduel_odds <= -120 and not isinstance(wager, PlayerProps) and not isinstance(wager, PlayerPropsYes):
            bet_frame.configure(bg="#90ee90")

        bet_frame.grid(row=row, column=col, padx=5, pady=5)
        bet_frame.pack_propagate(False)

        bet_label = tk.Label(
            bet_frame, text=f"{wager.pretty()}\nFanduel Odds: {wager.fanduel_odds}\nEV: {ev:.2f}%\nRisk: {risk_percentage:.2f}% (${int(2 * risk_percentage / 100 * BANKROLL + 1) / 2}0)",
            wraplength=260, justify="left",
            bg=bet_frame.cget("bg"))  # Match label background to frame
        bet_label.pack(expand=True)

        button_frame = tk.Frame(bet_frame, bg=bet_frame.cget("bg"))  # Match button frame background
        button_frame.pack(pady=5)

        # Replace copy button with write to sheet button
        write_sheet_button = tk.Button(
            button_frame,
            text="Write to Sheet",
            command=lambda wager=wager, risk_percentage=risk_percentage: write_to_sheet([
                datetime.today().strftime("%m/%d/%Y"),
                wager.pretty(),
                str(wager.fanduel_odds),
                str(int(2 * risk_percentage / 100 * BANKROLL + 1) / 2)
            ])
        )
        write_sheet_button.pack(side="left", padx=2)

        place_bet_button = tk.Button(button_frame, text="Place Bet",
                                     command=lambda w=wager: open_betslip(w.external_market_id, w.selection_id))
        place_bet_button.pack(side="left", padx=2)

        bet_frame.bind("<Button-1>", lambda event, wager=wager, ev=ev, risk_percentage=risk_percentage,
                       bet_label=bet_label: toggle_details(event, wager, ev, risk_percentage, bet_label))
        bet_label.bind("<Button-1>", lambda event, wager=wager, ev=ev, risk_percentage=risk_percentage,
                       bet_label=bet_label: toggle_details(event, wager, ev, risk_percentage, bet_label))

        col += 1
        if col == 2:
            col = 0
            row += 1

    canvas.configure(scrollregion=canvas.bbox("all"))


def main():
    root = tk.Tk()
    root.title("Good Bets")
    root.geometry("600x650")

    frame = tk.Frame(root)
    frame.pack(padx=10, pady=10)

    canvas = tk.Canvas(frame, height=500, width=580)
    scrollbar = tk.Scrollbar(frame, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # Bind mouse wheel events for scrolling
    canvas.bind_all("<MouseWheel>", lambda event: on_mouse_wheel(event, canvas))

    devig_method = tk.StringVar(value=DevigMethod.POWER.name)

    def on_devig_method_change(*args):
        method = DevigMethod[devig_method.get()]
        reload_data(root, canvas, scrollable_frame, method)

    devig_method.trace_add("write", on_devig_method_change)

    devig_options = [method.name for method in DevigMethod]
    devig_dropdown = tk.OptionMenu(root, devig_method, *devig_options)
    devig_dropdown.pack(pady=10)

    reload_button = tk.Button(root, text="Reload Data", command=lambda: reload_data(
        root, canvas, scrollable_frame, DevigMethod[devig_method.get()]))
    reload_button.pack(pady=10)

    reload_data(root, canvas, scrollable_frame, DevigMethod.POWER)

    root.mainloop()


if __name__ == "__main__":
    main()
