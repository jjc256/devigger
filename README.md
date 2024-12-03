# Devigger - Sports Betting Statistical Arbitrage Tool

A Python application that analyzes betting odds from FanDuel and Pinnacle to find profitable betting opportunities using statistical arbitrage techniques.

## Features

- Scrapes real-time odds from FanDuel and Pinnacle sportsbooks
- Only shows games from the current day to ensure Pinnacle's odds are closer to true market odds, reducing risk
- Supports multiple sports:
  - NBA (Basketball)
  - NFL (American Football)
  - NHL (Hockey)
  - NCAAF (College Football)
  - NCAAB (College Basketball) 
  - UEFA Champions League (Soccer)
  - EPL (Soccer)
  - SHL (Hockey)
  - NLA (Hockey)
- Analyzes various bet types:
  - Moneylines
  - Point Spreads
  - Over/Unders (Totals)
  - Player Props
  - Team Totals
- Calculates:
  - True probabilities using devigging methods
  - Expected Value (EV)
  - Kelly Criterion for optimal bet sizing
  - Risk percentage based on Kelly Criterion book limits
- GUI interface with:
  - Sortable bets by risk percentage
  - Detailed bet information
  - Copy to clipboard functionality (formats data for spreadsheet with columns: date, bet info, odds, amount)
    - Rounds bet amounts up to nearest $0.50 to appear more natural
    - Bankroll is argument in command line interface (e.g. run `python main.py 1000`)
  - Refresh capabilities