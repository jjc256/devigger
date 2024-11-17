import tkinter as tk
from tkinter import messagebox
from src.scrape import fanduel_nba, pinnacle_nba
from src.wager import Moneyline, PlayerProps, TeamTotal, Spread, TotalPoints, StatCategory, OverUnder
from src.devig import devig, DevigMethod, american_to_probability, kelly_criterion, get_confidence_value


def wagers():
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
                if pinnacle_wager.get("prices") is None:
                    continue
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
                    stat_category = (
                        StatCategory.POINTS if category == "Points" else
                        StatCategory.REBOUNDS if category == "Rebounds" else
                        StatCategory.THREE_PT if category == "3 Point FG" else
                        StatCategory.ASSISTS if category == "Assists"
                        else None
                    )
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
                                            player_name, stat_category, OverUnder.OVER, N, pinnacle_under_odds
                                        )
                                        common_wagers.append(player_props_over)
                                        break
    return common_wagers


def display_good_bets(devig_method=DevigMethod.POWER):
    common_wagers = wagers()
    good_bets = []

    for wager in common_wagers:
        true_prob = devig(wager.pinnacle_odds, wager.pinnacle_opposing_odds, devig_method)
        fanduel_prob = american_to_probability(wager.fanduel_odds)
        if true_prob > fanduel_prob:
            ev = (true_prob - fanduel_prob) / fanduel_prob * 100
            kelly_percentage = kelly_criterion(true_prob, fanduel_prob) * 100
            risk_percentage = kelly_percentage * get_confidence_value(wager.pinnacle_limit) / 10
            good_bets.append((wager, ev, risk_percentage))

    return good_bets


def change_devig_method(devig_method, common_wagers):
    good_bets = []

    for wager in common_wagers:
        true_prob = devig(wager.pinnacle_odds, wager.pinnacle_opposing_odds, devig_method)
        fanduel_prob = american_to_probability(wager.fanduel_odds)
        if true_prob > fanduel_prob:
            ev = (true_prob - fanduel_prob) / fanduel_prob * 100
            kelly_percentage = kelly_criterion(true_prob, fanduel_prob) * 100
            risk_percentage = kelly_percentage * get_confidence_value(wager.pinnacle_limit) / 5
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
            text=f"{wager.pretty()}\nFanduel Odds: {wager.fanduel_odds}\nEV: {ev:.2f}%\nRisk: {risk_percentage:.2f}%")
        current_text
    else:
        bet_label.config(text=detailed_text)
        current_text = detailed_text


def copy_to_clipboard(root, text):
    root.clipboard_clear()
    root.clipboard_append(text)
    root.update()  # now it stays on the clipboard after the window is closed


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
        bet_frame.grid(row=row, column=col, padx=5, pady=5)
        bet_frame.pack_propagate(False)  # Prevent the frame from resizing to fit its content

        bet_label = tk.Label(
            bet_frame, text=f"{wager.pretty().replace(',', '\n')}\nEV: {ev:.2f}%\nRisk: {risk_percentage:.2f}%", wraplength=260, justify="left")
        bet_label.pack(expand=True)

        copy_button = tk.Button(bet_frame, text="Copy",
                                command=lambda wager=wager: copy_to_clipboard(root, wager.pretty()))
        copy_button.pack(pady=5)

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
        canvas, scrollable_frame, DevigMethod[devig_method.get()]))
    reload_button.pack(pady=10)

    reload_data(root, canvas, scrollable_frame, DevigMethod.POWER)

    root.mainloop()


if __name__ == "__main__":
    main()
