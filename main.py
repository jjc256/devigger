import sys
from tkinter import messagebox
from goodbets import open_betslip, display_good_bets
from src.sheet_operations import write_to_sheet
import os.path
import time
from datetime import datetime
import tkinter as tk
from src.devig import DevigMethod
from src.wager import *
from plyer import notification

LOG_FILE = 'logged_bets.txt'


def is_bet_logged(date_game):
    if not os.path.exists(LOG_FILE):
        return False
    with open(LOG_FILE, 'r') as f:
        logged_bets = f.read().splitlines()
    return date_game in logged_bets


def log_bet(date_game):
    with open(LOG_FILE, 'a') as f:
        f.write(date_game + '\n')


class BettingGUI:
    def __init__(self, root, unit_size=100):
        self.root = root
        self.unit_size = unit_size
        self.root.title("Automated Betting Tracker")
        self.root.geometry("600x650")

        self.frame = tk.Frame(self.root)
        self.frame.pack(padx=10, pady=10)

        self.canvas = tk.Canvas(self.frame, height=500, width=580)
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

        # Status label
        self.status_label = tk.Label(root, text="Monitoring for new bets...", pady=5)
        self.status_label.pack()

        self.root.after(1000, self.check_for_new_bets)

    def on_mouse_wheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def format_bet_text(self, wager, risk_percentage):
        units = round((risk_percentage / 100 * BANKROLL) / self.unit_size, 1)
        return f"{wager.pretty()}\n{units}u @ {wager.fanduel_odds}"

    def copy_to_clipboard(self, text):
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        messagebox.showinfo("Success", "Bet copied to clipboard!")

    def add_bet_to_display(self, wager, ev, risk_percentage, insert_at_top=True):
        bet_frame = tk.Frame(self.scrollable_frame, borderwidth=2,
                             relief="groove", width=280, height=200, bg="#90ee90")

        # Store the bet data for later use
        today = datetime.today().strftime("%m/%d/%Y")
        row_data = [today, wager.pretty(), str(wager.fanduel_odds),
                    str(int(2 * risk_percentage / 100 * BANKROLL + 1) / 2)]
        self.bet_data[bet_frame] = row_data

        if insert_at_top:
            # Move all existing frames down one position
            for widget in self.scrollable_frame.winfo_children():
                current_row = widget.grid_info()['row']
                widget.grid(row=current_row + 1)

            bet_frame.grid(row=0, column=0, padx=5, pady=5)
        else:
            row = len(self.scrollable_frame.winfo_children()) // 2
            col = len(self.scrollable_frame.winfo_children()) % 2
            bet_frame.grid(row=row, column=col, padx=5, pady=5)

        bet_frame.pack_propagate(False)

        bet_label = tk.Label(
            bet_frame,
            text=f"{wager.pretty()}\nFanduel Odds: {wager.fanduel_odds}\nEV: {ev:.2f}%\nRisk: {risk_percentage:.2f}% (${int(2 * risk_percentage / 100 * BANKROLL + 1) / 2}0)",
            wraplength=260,
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
                if wager.fanduel_odds > -120 or isinstance(wager, (PlayerProps, PlayerPropsYes)):
                    continue

                game_name = wager.game
                date_game = f"{today}-{game_name}"

                if not is_bet_logged(date_game) and date_game not in self.processed_bets:
                    # Add to GUI
                    self.add_bet_to_display(wager, ev, risk_percentage, True)
                    new_bets_text.append(f"{wager.pretty()} ({wager.fanduel_odds})")

                    # Log the bet
                    log_bet(date_game)
                    self.processed_bets.add(date_game)
                    found_new_bet = True

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
                ("New bets found!" if found_new_bet else "No new bets")
            print(f"{status_msg}\nWaiting 5 minutes before next check...")
            self.status_label.config(text=status_msg)

        except Exception as e:
            error_msg = f"Error: {str(e)}"
            print(error_msg)
            self.status_label.config(text=error_msg)

        self.root.after(300000, self.check_for_new_bets)


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
