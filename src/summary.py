import re


def parse_bets(file_path):
    bets = []
    with open(file_path, 'r') as file:
        for line in file:
            parts = re.split(r'\t+', line.strip())  # Split using tab delimiters
            if len(parts) < 7:
                continue  # Skip malformed lines

            try:
                bet_type = parts[1]
                if "Moneyline" in bet_type:
                    bet_name = bet_type.split(" Moneyline")[0] + " Moneyline"
                elif "Handicap" in bet_type:
                    bet_name = bet_type.split(" Handicap")[0] + " Handicap"
                else:
                    bet_name = bet_type  # Default if neither Moneyline nor Handicap is found

                result = "W" if parts[4] == "WIN" else "L" if parts[4] == "LOSS" else "V"
                profit = float(parts[5]) / 2.5  # Convert profit to units
                bets.append((bet_name, result, round(profit, 1)))
            except ValueError:
                continue  # Skip lines with conversion errors

    return bets


def summarize_bets(bets):
    wins = sum(1 for _, result, _ in bets if result == "W")
    losses = sum(1 for _, result, _ in bets if result == "L")
    voids = sum(1 for _, result, _ in bets if result == "V")
    total_profit = round(sum(profit for _, _, profit in bets), 1)

    record = f"Overall Record: {wins}-{losses}" + (f"-{voids}" if voids > 0 else "")
    profit_line = f"Total Profit: {total_profit} units"

    bet_lines = [
        f"{bet}: {result}, {profit} units {'✅' if result == 'W' else '❌' if result == 'L' else ''}"
        for bet, result, profit in bets
    ]

    return "\n".join([record, profit_line, ""] + bet_lines)


if __name__ == "__main__":
    file_path = "results.txt"  # Replace with your file name
    bets = parse_bets(file_path)
    summary = summarize_bets(bets)
    print(summary)
