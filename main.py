import sys
from tkinter import messagebox
from goodbets import open_betslip, display_good_bets, is_good_bet
from src.sheet_operations import write_to_sheet
import os.path
import time
from datetime import datetime, timedelta
import tkinter as tk
from src.devig import DevigMethod
from src.wager import *
from plyer import notification
import traceback

LOG_FILE = 'logged_bets.txt'


def is_bet_logged(date_game):
    if not os.path.exists(LOG_FILE):
        return False
    with open(LOG_FILE, 'r') as f:
        logged_bets = f.read().splitlines()
    return date_game in logged_bets


def log_bet(date_game):
    with open(LOG_FILE, 'a') as f:
        f.write(f"{date_game}\n")


class BettingGUI:
    def __init__(self, root, unit_size=100):
        self.root = root
        self.unit_size = unit_size
        self.root.title("Automated Betting Tracker")
        self.root.geometry("1200x650")  # Increased width for two columns

        self.frame = tk.Frame(self.root)
        self.frame.pack(padx=10, pady=10)

        self.canvas = tk.Canvas(self.frame, height=500, width=1180)  # Increased canvas width
        self.scrollbar = tk.Scrollbar(self.frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas)

        self.scrollable_frame.bind("<Configure>",
                                   lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.canvas.bind_all("<MouseWheel>", self.on_mouse_wheel)
        self.processed_bets = set()
        self.bet_data = {}  # New dictionary to store bet data
        self.displayed_games = {}  # Store displayed games and their frames

        # Add reload button at the top
        self.reload_button = tk.Button(root, text="Reload Odds", command=self.reload_odds)
        self.reload_button.pack(pady=5)

        # Status label (move after reload button)
        self.status_label = tk.Label(root, text="Monitoring for new bets...", pady=5)
        self.status_label.pack()

        self.bet_frames = {}  # Store frames by wager text
        self.root.after(1000, self.check_for_new_bets)
        self.bet_counter = 0  # Add counter to track number of bets for column placement
        self.total_bets = 0  # Add this line to track total bets

    def on_mouse_wheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def format_bet_text(self, wager, risk_percentage):
        bet_amount = int(2 * risk_percentage / 100 * BANKROLL + 1) / 2
        units = bet_amount / self.unit_size
        return f"{wager.pretty()}\n{units}u @ {wager.fanduel_odds}"

    def copy_to_clipboard(self, text):
        self.root.clipboard_clear()
        self.root.clipboard_append(text)

    def add_bet_to_display(self, wager, ev, risk_percentage, insert_at_top=True):
        bet_frame = tk.Frame(self.scrollable_frame, borderwidth=2,
                             relief="groove", width=570, height=200, bg="#90ee90")

        if insert_at_top:
            # Shift all existing frames down
            for widget in self.scrollable_frame.winfo_children():
                grid_info = widget.grid_info()
                if grid_info:
                    position = grid_info['row'] * 2 + grid_info['column']
                    new_position = position + 1
                    new_row = new_position // 2
                    new_col = new_position % 2
                    widget.grid(row=new_row, column=new_col, padx=5, pady=5, sticky="ew")

            # Place new frame at position 0
            bet_frame.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
            self.total_bets += 1
        else:
            # For non-top insertions, add to next available position
            position = self.total_bets
            row = position // 2
            col = position % 2
            bet_frame.grid(row=row, column=col, padx=5, pady=5, sticky="ew")
            self.total_bets += 1

        # Store the bet data for later use
        today = datetime.today().strftime("%m/%d/%Y")
        row_data = [today, wager.pretty(), str(wager.fanduel_odds),
                    str(int(2 * risk_percentage / 100 * BANKROLL + 1) / 2)]
        self.bet_data[bet_frame] = row_data

        bet_frame.pack_propagate(False)

        bet_label = tk.Label(
            bet_frame,
            text=f"{wager.pretty()}\nFanduel Odds: {wager.fanduel_odds}\nEV: {ev:.2f}%\nRisk: {risk_percentage:.2f}% (${int(2 * risk_percentage / 100 * BANKROLL + 1) / 2}0)",
            wraplength=520,  # Adjusted wraplength for two columns
            justify="left",
            bg="#90ee90"
        )
        bet_label.pack(expand=True)

        button_frame = tk.Frame(bet_frame, bg="#90ee90")
        button_frame.pack(pady=5)

        copy_bet_button = tk.Button(
            button_frame,
            text="Copy Bet",
            command=lambda: self.copy_to_clipboard(self.format_bet_text(wager, risk_percentage))
        )
        copy_bet_button.pack(side="left", padx=2)

        place_bet_button = tk.Button(
            button_frame,
            text="Place Bet",
            command=lambda: open_betslip(wager.external_market_id, wager.selection_id)
        )
        place_bet_button.pack(side="left", padx=2)

        write_sheet_button = tk.Button(
            button_frame,
            text="Write to Sheet",
            command=lambda: self.write_bet_to_sheet(bet_frame)
        )
        write_sheet_button.pack(side="left", padx=2)

        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self.displayed_games[wager.game] = bet_frame  # Track displayed games
        return bet_frame  # Add this line to return the frame

    def write_bet_to_sheet(self, bet_frame):
        if (bet_frame in self.bet_data):
            row_data = self.bet_data[bet_frame]
            try:
                write_to_sheet(row_data)
                bet_frame.configure(bg="#D3D3D3")  # Change color to indicate written
                for widget in bet_frame.winfo_children():
                    if isinstance(widget, tk.Frame):
                        widget.configure(bg="#D3D3D3")
                        for button in widget.winfo_children():
                            if button["text"] == "Write to Sheet":
                                button.configure(state="disabled")
                    else:
                        widget.configure(bg="#D3D3D3")
            except Exception as e:
                print(f"Error writing to sheet: {e}")

    def update_bet_display(self, bet_frame, wager, ev, risk_percentage):
        bet_label = bet_frame.winfo_children()[0]  # Get the label widget
        bet_label.config(
            text=f"{wager.pretty()}\nFanduel Odds: {wager.fanduel_odds}\nEV: {ev:.2f}%\nRisk: {risk_percentage:.2f}% (${int(2 * risk_percentage / 100 * BANKROLL + 1) / 2}0)"
        )

    def are_same_bet(self, wager1, wager2):
        # Compare essential properties to determine if it's the same bet
        return (wager1.game == wager2.game and
                wager1.pretty() == wager2.pretty())

    def process_new_bet(self, wager, ev, risk_percentage, today, notify=True):
        game_name = wager.game
        date_bet = f"{today}-{wager.pretty()}"
        date_bet_yesterday = f"{(datetime.today() - timedelta(days=1)).strftime('%m/%d/%Y')}-{wager.pretty()}"

        if not is_bet_logged(date_bet) and (date_bet not in self.processed_bets
                                            and date_bet_yesterday not in self.processed_bets):
            # Add to GUI
            bet_frame = self.add_bet_to_display(wager, ev, risk_percentage, True)
            self.bet_frames[date_bet] = bet_frame

            # Log the bet
            log_bet(date_bet)
            self.processed_bets.add(date_bet)
            return True, wager.pretty() + f" ({wager.fanduel_odds})"
        return False, None

    def reload_odds(self):
        try:
            print("\nReloading odds...")
            self.status_label.config(text="Reloading odds...")
            self.root.update()

            good_bets = display_good_bets(DevigMethod.POWER)
            # Sort bets by risk percentage before processing
            good_bets.sort(key=lambda x: x[2], reverse=True)
            found_updates = False
            new_bets_text = []
            today = datetime.today().strftime("%m/%d/%Y")

            # Create a mapping of displayed bets for easier lookup
            displayed_bets = {}
            for frame, data in self.bet_data.items():
                displayed_bets[data[1]] = frame  # Using bet name as key

            # Process all bets from the new data
            for wager, ev, risk_percentage in good_bets:
                if not is_good_bet:
                    continue

                # Check if this bet already exists
                found_match = False
                for frame, data in list(self.bet_data.items()):
                    if data[1] == wager.pretty():  # If same bet name
                        # Update the display and stored data
                        self.update_bet_display(frame, wager, ev, risk_percentage)
                        self.bet_data[frame] = [today, wager.pretty(), str(wager.fanduel_odds),
                                                str(int(2 * risk_percentage / 100 * BANKROLL + 1) / 2)]
                        found_match = True
                        found_updates = True
                        break

                # If it's a new bet, process it
                if not found_match:
                    is_new, bet_text = self.process_new_bet(wager, ev, risk_percentage, today)
                    if is_new:
                        found_updates = True
                        new_bets_text.append(bet_text)

            if new_bets_text:
                notification.notify(
                    title='New Betting Opportunities!',
                    message='\n'.join(new_bets_text[:3]) +
                    ('\n...' if len(new_bets_text) > 3 else ''),
                    app_icon=None,
                    timeout=10,
                )

            current_time = datetime.now().strftime('%I:%M:%S %p')
            status_msg = f"Last reload: {current_time} - " + \
                ("Odds updated!" if found_updates else "No changes in odds")
            self.status_label.config(text=status_msg)

        except Exception as e:
            error_msg = f"Error reloading odds: {str(e)}"
            print(error_msg)
            self.status_label.config(text=error_msg)

    def check_for_new_bets(self):
        try:
            print("\nScraping data...")
            self.status_label.config(text="Scraping data...")
            self.root.update()

            good_bets = display_good_bets(DevigMethod.POWER)
            good_bets.sort(key=lambda x: x[2], reverse=True)

            today = datetime.today().strftime("%m/%d/%Y")
            found_new_bet = False
            new_bets_text = []

            for wager, ev, risk_percentage in good_bets:
                if not is_good_bet:
                    continue

                is_new, bet_text = self.process_new_bet(wager, ev, risk_percentage, today)
                if is_new:
                    found_new_bet = True
                    new_bets_text.append(bet_text)

            if found_new_bet:
                notification.notify(
                    title='New Betting Opportunities!',
                    message='\n'.join(new_bets_text[:3]) +
                    ('\n...' if len(new_bets_text) > 3 else ''),
                    app_icon=None,
                    timeout=10,
                )

            current_time = datetime.now().strftime('%I:%M:%S %p')
            status_msg = f"Last check: {current_time} - " + \
                ("New bets found!" if found_new_bet else "No new bets found")
            print(f"{status_msg}\nWaiting 30 minutes before next check...")
            self.status_label.config(text=status_msg)

        except Exception as e:
            error_msg = f"Error: {str(e)}\nType: {type(e).__name__}\nDetails: {str(e.__dict__)}"
            print(error_msg)
            print("\nStack trace:")
            print(traceback.format_exc())
            self.status_label.config(text=error_msg)
            notification.notify(
                title='Error in Betting App',
                message=error_msg[:200] + '...' if len(error_msg) > 200 else error_msg,
                app_icon=None,
                timeout=10,
            )

        # Schedule next check in 30 minutes
        if hasattr(self, 'next_check'):
            self.root.after_cancel(self.next_check)
        self.next_check = self.root.after(1800000, self.check_for_new_bets)


def main():
    global BANKROLL
    if len(sys.argv) > 2:
        try:
            BANKROLL = float(sys.argv[1])
            unit_size = float(sys.argv[2])
        except ValueError:
            print("Invalid arguments. Using defaults: BANKROLL=1000, unit_size=10")
            BANKROLL = 1000
            unit_size = 10
    else:
        print("Usage: python main.py <bankroll> <unit_size>")
        print("Using defaults: BANKROLL=1000, unit_size=10")
        BANKROLL = 1000
        unit_size = 10

    root = tk.Tk()
    app = BettingGUI(root, unit_size)
    root.mainloop()


if __name__ == "__main__":
    main()
