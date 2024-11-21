# Devigger - Sports Betting Statistical Arbitrage Tool

A Python application that analyzes betting odds from FanDuel and Pinnacle to find profitable betting opportunities using statistical arbitrage techniques.

## Features

- Scrapes real-time odds from FanDuel and Pinnacle sportsbooks
- Supports multiple sports:
  - NBA (Basketball)
  - NFL (American Football)
  - NHL (Hockey)
  - NCAAF (College Football)
  - NCAAB (College Basketball) 
  - UEFA Champions League (Soccer)
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
  - Risk percentage based on book limits
- GUI interface with:
  - Sortable bets by EV/Risk
  - Detailed bet information
  - Copy to clipboard functionality
  - Refresh capabilities

## Note

For sports, such as soccer, where names are listed home team first, for the sake of easiness, we always list away team first.