import requests
import os
import json  # Add import for json module
from bs4 import BeautifulSoup


def get_response(url, headers, params=None):
    """
    Sends a GET request to the specified URL with the given headers and parameters.

    Args:
        url (str): The URL to send the request to.
        headers (dict): The headers to include in the request.
        params (dict, optional): The parameters to include in the request. Defaults to None.

    Returns:
        dict: The JSON response if the request is successful, otherwise None.
    """
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Request failed with status code: {response.status_code}")
        return None


def get_response_no_params(url, headers):
    """
    Sends a GET request to the specified URL with the given headers.

    Args:
        url (str): The URL to send the request to.
        headers (dict): The headers to include in the request.

    Returns:
        dict: The JSON response if the request is successful, otherwise None.
    """
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Request failed with status code: {response.status_code}")
        return None


def process_fanduel_rows(rows, data):
    """
    Processes the rows of Fanduel data to extract event IDs and names.

    Args:
        rows (list): The list of rows to process.
        data (dict): The data containing event information.

    Returns:
        tuple: A dictionary of event IDs and names, and a set of seen event IDs.
    """
    result = {}
    seen_event_ids = set()
    for row in rows:
        event_id = row.get("eventId")
        if event_id:
            name = data.get("attachments", {}).get(
                "events", {}).get(str(event_id), {}).get("name")
            if " @ " in name or " v " in name:
                result[event_id] = {"name": name}
                seen_event_ids.add(event_id)
    return result, seen_event_ids


def process_fanduel_markets(markets, seen_event_ids, result):
    """
    Processes the Fanduel markets to extract market information for seen event IDs.

    Args:
        markets (dict): The dictionary of markets to process.
        seen_event_ids (set): The set of seen event IDs.
        result (dict): The dictionary to store the processed market information.
    """
    for _, market in markets.items():
        event_id = market.get("eventId")
        if event_id in seen_event_ids:
            market_info = {
                "marketType": market.get("marketType"),
                "runners": []
            }
            for runner in market.get("runners", []):
                runner_info = {
                    "handicap": runner.get("handicap"),
                    "runnerName": runner.get("runnerName"),
                    "winRunnerOdds": runner.get("winRunnerOdds", {}).get("americanDisplayOdds", {}).get("americanOdds")
                }
                market_info["runners"].append(runner_info)
            if 'markets' not in result[event_id]:
                result[event_id]['markets'] = []
            result[event_id]["markets"].append(market_info)


def save_result_to_file(result, filename):
    """
    Saves the result to a JSON file.

    Args:
        result (dict): The result data to save.
        filename (str): The name of the file to save the result to.
    """
    with open('src/example_json/' + filename, 'w') as f:
        json.dump(result, f, indent=4)


def fanduel_nba():
    """
    Fetches and processes NBA data from Fanduel.
    """
    url = 'https://sbapi.ny.sportsbook.fanduel.com/api/content-managed-page'
    api_key = os.getenv('FANDUEL_API_KEY')
    params = {
        'page': 'CUSTOM',
        'customPageId': 'nba',
        'pbHorizontal': 'false',
        '_ak': api_key,
        'timezone': 'America/New_York'
    }

    headers = {
        'accept': 'application/json',
        'accept-language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
        'dnt': '1',
        'if-none-match': 'W/"a73bb-bqV9yd4R3uJGX5TnE8+f776CCtc"',
        'origin': 'https://sportsbook.fanduel.com',
        'priority': 'u=1, i',
        'referer': 'https://sportsbook.fanduel.com/',
        'sec-ch-ua': '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36'
    }

    data = get_response(url, headers, params)
    if data:
        rows = data.get("layout", {}).get("coupons", {}).get(
            "32866", {}).get("display", [])[0].get("rows", [])
        result, seen_event_ids = process_fanduel_rows(rows, data)
        markets = data.get("attachments", {}).get("markets", {})
        process_fanduel_markets(markets, seen_event_ids, result)

        # save_result_to_file(result, 'example_fanduel_nba.json')
        return result


def fanduel_nfl():
    """
    Fetches and processes NFL data from Fanduel.
    """
    url = 'https://sbapi.ny.sportsbook.fanduel.com/api/content-managed-page'
    api_key = os.getenv('FANDUEL_API_KEY')
    params = {
        'page': 'CUSTOM',
        'customPageId': 'nfl',
        'pbHorizontal': 'false',
        '_ak': api_key,
        'timezone': 'America/New_York'
    }

    headers = {
        'accept': 'application/json',
        'accept-language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
        'dnt': '1',
        'if-none-match': 'W/"a73bb-bqV9yd4R3uJGX5TnE8+f776CCtc"',
        'origin': 'https://sportsbook.fanduel.com',
        'priority': 'u=1, i',
        'referer': 'https://sportsbook.fanduel.com/',
        'sec-ch-ua': '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36'
    }

    data = get_response(url, headers, params)
    if data:
        rows = list(data.get("attachments", {}).get("events", {}).values())[2:]
        result, seen_event_ids = process_fanduel_rows(rows, data)
        markets = data.get("attachments", {}).get("markets", {})
        process_fanduel_markets(markets, seen_event_ids, result)

        # save_result_to_file(result, 'example_fanduel_nfl.json')
        return result


def fanduel_nhl():
    """
    Fetches and processes NHL data from Fanduel.
    """
    url = 'https://sbapi.ny.sportsbook.fanduel.com/api/content-managed-page'
    api_key = os.getenv('FANDUEL_API_KEY')
    params = {
        'page': 'CUSTOM',
        'customPageId': 'nhl',
        'pbHorizontal': 'false',
        '_ak': api_key,
        'timezone': 'America/New_York'
    }

    headers = {
        'accept': 'application/json',
        'accept-language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
        'dnt': '1',
        'if-none-match': 'W/"a73bb-bqV9yd4R3uJGX5TnE8+f776CCtc"',
        'origin': 'https://sportsbook.fanduel.com',
        'priority': 'u=1, i',
        'referer': 'https://sportsbook.fanduel.com/',
        'sec-ch-ua': '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36'
    }

    data = get_response(url, headers, params)
    if data:
        rows = data.get("layout", {}).get("coupons", {}).get(
            "35876", {}).get("display", [])[0].get("rows", [])
        result, seen_event_ids = process_fanduel_rows(rows, data)
        markets = data.get("attachments", {}).get("markets", {})
        process_fanduel_markets(markets, seen_event_ids, result)

        # save_result_to_file(result, 'example_fanduel_nhl.json')
        return result


def fanduel_ncaaf():
    """
    Fetches and processes NCAAF data from Fanduel.
    """
    url = 'https://sbapi.ny.sportsbook.fanduel.com/api/content-managed-page'
    api_key = os.getenv('FANDUEL_API_KEY')
    params = {
        'page': 'CUSTOM',
        'customPageId': 'ncaaf',
        'pbHorizontal': 'false',
        '_ak': api_key,
        'timezone': 'America/New_York'
    }

    headers = {
        'accept': 'application/json',
        'accept-language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
        'dnt': '1',
        'if-none-match': 'W/"a73bb-bqV9yd4R3uJGX5TnE8+f776CCtc"',
        'origin': 'https://sportsbook.fanduel.com',
        'priority': 'u=1, i',
        'referer': 'https://sportsbook.fanduel.com/',
        'sec-ch-ua': '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36'
    }

    data = get_response(url, headers, params)
    if data:
        # Get all events from the attachments section
        rows = data.get("layout", {}).get("coupons", {}).get(
            "2", {}).get("display", [])[0].get("rows", [])
        result, seen_event_ids = process_fanduel_rows(rows, data)
        markets = data.get("attachments", {}).get("markets", {})
        process_fanduel_markets(markets, seen_event_ids, result)

        # save_result_to_file(result, 'example_fanduel_ncaaf.json')
        return result


def fanduel_ncaab():
    """
    Fetches and processes NCAAB data from Fanduel.
    """
    url = 'https://sbapi.ny.sportsbook.fanduel.com/api/content-managed-page'
    api_key = os.getenv('FANDUEL_API_KEY')
    params = {
        'page': 'CUSTOM',
        'customPageId': 'ncaab',
        'pbHorizontal': 'false',
        '_ak': api_key,
        'timezone': 'America/New_York'
    }

    headers = {
        'accept': 'application/json',
        'accept-language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
        'dnt': '1',
        'if-none-match': 'W/"a73bb-bqV9yd4R3uJGX5TnE8+f776CCtc"',
        'origin': 'https://sportsbook.fanduel.com',
        'priority': 'u=1, i',
        'referer': 'https://sportsbook.fanduel.com/',
        'sec-ch-ua': '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36'
    }

    data = get_response(url, headers, params)
    if data:
        # Get all events from the attachments section
        rows = []
        for display in data.get("layout", {}).get("coupons", {}).get("9411", {}).get("display", []):
            rows.extend(display.get("rows", []))
        result, seen_event_ids = process_fanduel_rows(rows, data)
        markets = data.get("attachments", {}).get("markets", {})
        process_fanduel_markets(markets, seen_event_ids, result)

        # save_result_to_file(result, 'example_fanduel_ncaab.json')
        return result


def fanduel_ucl():
    """
    Fetches and processes UEFA Champions League data from Fanduel.
    """
    url = 'https://sbapi.ny.sportsbook.fanduel.com/api/competition-page'
    api_key = os.getenv('FANDUEL_API_KEY')
    params = {
        '_ak': api_key,
        'eventTypeId': '1',
        'competitionId': '228'
    }

    headers = {
        'accept': 'application/json',
        'accept-language': 'en-US,en;q=0.9',
        'dnt': '1',
        'origin': 'https://sportsbook.fanduel.com',
        'referer': 'https://sportsbook.fanduel.com/',
        'sec-ch-ua': '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36'
    }

    data = get_response(url, headers, params)
    if data:
        # Get all events from the events section
        rows = list(data.get("attachments", {}).get("events", {}).values())
        result, seen_event_ids = process_fanduel_rows(rows, data)
        markets = data.get("attachments", {}).get("markets", {})
        process_fanduel_markets(markets, seen_event_ids, result)

        # save_result_to_file(result, 'example_fanduel_ucl.json')
        return result


def fanduel_epl():
    """
    Fetches and processes English Premier League data from Fanduel.
    """
    url = 'https://sbapi.ny.sportsbook.fanduel.com/api/competition-page'
    api_key = os.getenv('FANDUEL_API_KEY')
    params = {
        '_ak': api_key,
        'eventTypeId': '1',
        'competitionId': '10932509'
    }

    headers = {
        'accept': 'application/json',
        'accept-language': 'en-US,en;q=0.9',
        'dnt': '1',
        'origin': 'https://sportsbook.fanduel.com',
        'referer': 'https://sportsbook.fanduel.com/',
        'sec-ch-ua': '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36'
    }

    data = get_response(url, headers, params)
    if data:
        # Get all events from the events section
        rows = list(data.get("attachments", {}).get("events", {}).values())
        result, seen_event_ids = process_fanduel_rows(rows, data)
        markets = data.get("attachments", {}).get("markets", {})
        process_fanduel_markets(markets, seen_event_ids, result)

        # save_result_to_file(result, 'example_fanduel_epl.json')
        return result


def fanduel_shl():
    """
    Fetches and processes Swedish Hockey League (SHL) data from Fanduel.
    """
    url = 'https://sbapi.ny.sportsbook.fanduel.com/api/competition-page'
    api_key = os.getenv('FANDUEL_API_KEY')
    params = {
        '_ak': api_key,
        'eventTypeId': '7524',
        'competitionId': '10546040'
    }

    headers = {
        'accept': 'application/json',
        'accept-language': 'en-US,en;q=0.9',
        'dnt': '1',
        'origin': 'https://sportsbook.fanduel.com',
        'referer': 'https://sportsbook.fanduel.com/',
        'sec-ch-ua': '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36'
    }

    data = get_response(url, headers, params)
    if data:
        # Get all events from the events section
        rows = list(data.get("attachments", {}).get("events", {}).values())
        result, seen_event_ids = process_fanduel_rows(rows, data)
        markets = data.get("attachments", {}).get("markets", {})
        process_fanduel_markets(markets, seen_event_ids, result)

        # save_result_to_file(result, 'example_fanduel_shl.json')
        return result


def process_matchups(matchups_data, switch_home_away=False):
    """
    Processes the matchups data from Pinnacle to extract matchup IDs and names.

    Args:
        matchups_data (list): The list of matchups to process.

    Returns:
        dict: A dictionary of matchup IDs and names.
    """
    result = {}
    for matchup in matchups_data:
        parent = matchup.get("parentId")
        if parent is not None:
            continue
        participants = matchup.get("participants", [])
        if len(participants) == 2 and "(" not in participants[0].get("name"):
            home = participants[0]
            away = participants[1]
            if home.get("alignment") == "home" and away.get("alignment") == "away":
                matchup_id = matchup.get("id")
                matchup_name = f"{away.get('name')} @ {home.get('name')}" if not switch_home_away else f"{home.get('name')} v {away.get('name')}"
                result[matchup_id] = {
                    "name": matchup_name,
                    "markets": []  # Add empty markets list
                }
    return result


def process_specials(matchups_data, result):
    """
    Processes the specials data from Pinnacle to extract special IDs and their parent IDs.

    Args:
        matchups_data (list): The list of matchups to process.
        result (dict): The dictionary to store the processed special information.

    Returns:
        dict: A dictionary with special IDs as keys and their parent IDs as values.
    """
    special_to_parent = {}
    for matchup in matchups_data:
        matchup_id = matchup.get("parentId")
        if matchup_id is None:
            continue
        market_info = {}
        special = matchup.get("special")
        if special:
            description = special.get("description")
            if description:
                market_info["id"] = matchup["id"]
                market_info["description"] = description
                special_to_parent[matchup["id"]] = matchup_id
            if matchup_id in result and description and "Range" not in description:
                result[matchup_id]["markets"].append(market_info)
    # print(special_to_parent)
    return special_to_parent


def process_markets(markets_data, result, special_to_parent):
    """
    Processes the markets data from Pinnacle to extract market information.

    Args:
        markets_data (list): The list of markets to process.
        result (dict): The dictionary to store the processed market information.
        special_to_parent (dict): A dictionary with special IDs as keys and their parent IDs as values.
    """
    for market in markets_data:
        prices = market.get("prices")
        if (market.get("key") == "s;0;m"
            and (market.get("matchupId") in result)
                and prices[0].get("points") is None):
            market_info = {
                "description": "moneyline",
                "prices": prices,
                "limit": market.get("limits", [{}])[0].get("amount")
            }
            result[market.get("matchupId")]["markets"].append(market_info)
        elif market.get("key").startswith("s;0;tt;") and market.get("matchupId") in result and len(market.get("prices", [])) == 2:
            parts = market.get("key").split(";")
            if len(parts) == 5 and parts[4] in ["home", "away"]:
                team = parts[4]
                threshold = parts[3]
                market_info = {
                    "description": "team total",
                    "team": team,
                    "threshold": threshold,
                    "prices": prices,
                    "limit": market.get("limits", [{}])[0].get("amount")
                }
                result[market.get("matchupId")]["markets"].append(market_info)
        elif market.get("key").startswith("s;0;s;") and market.get("matchupId") in result:
            for price in prices:
                if "points" in price:
                    price["handicap"] = price.pop("points")
                if "designation" in price:
                    price["team"] = price.pop("designation")
            market_info = {
                "description": "handicap",
                "prices": prices,
                "limit": market.get("limits", [{}])[0].get("amount")
            }
            result[market.get("matchupId")]["markets"].append(market_info)

        # Add processing for over/under markets
        elif (((market.get("key") == "s;0;ou" and "points" in prices[0])
                or (market.get("key") == "s;0;m" or market.get("key") == "s;1;m"))
              and special_to_parent.get(market.get("matchupId")) in result):
            matchup_id = market.get("matchupId")
            if len(prices) == 2:
                parent_matchup_id = special_to_parent.get(matchup_id)
                if parent_matchup_id:
                    for existing_market in result[parent_matchup_id]["markets"]:
                        market_id = existing_market.get("id")
                        if market_id == matchup_id:
                            if prices[0].get("participantId", 0) > prices[1].get("participantId", 0):
                                prices[0], prices[1] = prices[1], prices[0]
                            prices[0]["designation"] = "over" if market.get(
                                "key") == "s;0;ou" else "odd" if market.get("key") == "s;1;m" else "yes"
                            prices[1]["designation"] = "under" if market.get(
                                "key") == "s;0;ou" else "even" if market.get("key") == "s;1;m" else "no"
                            prices[0].pop("participantId")
                            prices[1].pop("participantId")
                            if market.get("key") != "s;0;ou" and "points" in prices[0]:
                                prices[0].pop("points")
                                prices[1].pop("points")
                            existing_market["prices"] = prices
                            existing_market["limit"] = market.get("limits", [{}])[0].get("amount")
        # Add processing for total points markets
        elif market.get("key").startswith("s;0;ou;") and market.get("matchupId") in result:
            parts = market.get("key").split(";")
            if len(parts) == 4 and len(prices) == 2:
                threshold = parts[3]
                market_info = {
                    "description": "total points",
                    "threshold": threshold,
                    "prices": prices,
                    "limit": market.get("limits", [{}])[0].get("amount")
                }
                result[market.get("matchupId")]["markets"].append(market_info)


def pinnacle_nba():
    """
    Fetches and processes NBA data from Pinnacle.
    """
    headers = {
        'sec-ch-ua-platform': 'Windows',
        'X-Device-UUID': os.getenv('PINNACLE_DEVICE_UUID'),
        'Referer': 'https://www.pinnacle.com/',
        'sec-ch-ua': 'Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
        'X-API-Key': os.getenv('PINNACLE_API_KEY'),
        'sec-ch-ua-mobile': '?0',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
        'Accept': 'application/json',
        'DNT': '1',
        'Content-Type': 'application/json'
    }

    matchups_data = get_response_no_params(
        'https://guest.api.arcadia.pinnacle.com/0.1/leagues/487/matchups?brandId=0', headers)
    markets_data = get_response_no_params(
        'https://guest.api.arcadia.pinnacle.com/0.1/leagues/487/markets/straight', headers)

    if matchups_data and markets_data:
        result = process_matchups(matchups_data)
        special_to_parent = process_specials(matchups_data, result)
        process_markets(markets_data, result, special_to_parent)

        # save_result_to_file(result, 'example_pinnacle_nba.json')
    return result


def pinnacle_nfl():
    """
    Fetches and processes NFL data from Pinnacle.
    """
    headers = {
        'sec-ch-ua-platform': 'Windows',
        'X-Device-UUID': os.getenv('PINNACLE_DEVICE_UUID'),
        'Referer': 'https://www.pinnacle.com/',
        'sec-ch-ua': 'Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
        'X-API-Key': os.getenv('PINNACLE_API_KEY'),
        'sec-ch-ua-mobile': '?0',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
        'Accept': 'application/json',
        'DNT': '1',
        'Content-Type': 'application/json'
    }

    matchups_data = get_response_no_params(
        'https://guest.api.arcadia.pinnacle.com/0.1/leagues/889/matchups?brandId=0', headers)
    markets_data = get_response_no_params(
        'https://guest.api.arcadia.pinnacle.com/0.1/leagues/889/markets/straight', headers)

    if matchups_data and markets_data:
        result = process_matchups(matchups_data)
        special_to_parent = process_specials(matchups_data, result)
        process_markets(markets_data, result, special_to_parent)

        # save_result_to_file(result, 'example_pinnacle_nfl.json')
    return result


def pinnacle_nhl():
    """
    Fetches and processes NHL data from Pinnacle.
    """
    headers = {
        'sec-ch-ua-platform': 'Windows',
        'X-Device-UUID': os.getenv('PINNACLE_DEVICE_UUID'),
        'Referer': 'https://www.pinnacle.com/',
        'sec-ch-ua': 'Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
        'X-API-Key': os.getenv('PINNACLE_API_KEY'),
        'sec-ch-ua-mobile': '?0',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
        'Accept': 'application/json',
        'DNT': '1',
        'Content-Type': 'application/json'
    }

    matchups_data = get_response_no_params(
        'https://guest.api.arcadia.pinnacle.com/0.1/leagues/1456/matchups?brandId=0', headers)
    markets_data = get_response_no_params(
        'https://guest.api.arcadia.pinnacle.com/0.1/leagues/1456/markets/straight', headers)

    if matchups_data and markets_data:
        result = process_matchups(matchups_data)
        special_to_parent = process_specials(matchups_data, result)
        process_markets(markets_data, result, special_to_parent)

        # save_result_to_file(result, 'example_pinnacle_nhl.json')
    return result


def pinnacle_ncaaf():
    """
    Fetches and processes NCAAF data from Pinnacle.
    """
    headers = {
        'sec-ch-ua-platform': 'Windows',
        'X-Device-UUID': os.getenv('PINNACLE_DEVICE_UUID'),
        'Referer': 'https://www.pinnacle.com/',
        'sec-ch-ua': 'Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
        'X-API-Key': os.getenv('PINNACLE_API_KEY'),
        'sec-ch-ua-mobile': '?0',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
        'Accept': 'application/json',
        'DNT': '1',
        'Content-Type': 'application/json'
    }

    matchups_data = get_response_no_params(
        'https://guest.api.arcadia.pinnacle.com/0.1/leagues/880/matchups?brandId=0', headers)
    markets_data = get_response_no_params(
        'https://guest.api.arcadia.pinnacle.com/0.1/leagues/880/markets/straight', headers)

    if matchups_data and markets_data:
        result = process_matchups(matchups_data)
        special_to_parent = process_specials(matchups_data, result)
        process_markets(markets_data, result, special_to_parent)

        # save_result_to_file(result, 'example_pinnacle_ncaaf.json')
    return result


def pinnacle_ncaab():
    """
    Fetches and processes NCAAB data from Pinnacle.
    """
    headers = {
        'sec-ch-ua-platform': 'Windows',
        'X-Device-UUID': os.getenv('PINNACLE_DEVICE_UUID'),
        'Referer': 'https://www.pinnacle.com/',
        'sec-ch-ua': 'Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
        'X-API-Key': os.getenv('PINNACLE_API_KEY'),
        'sec-ch-ua-mobile': '?0',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
        'Accept': 'application/json',
        'DNT': '1',
        'Content-Type': 'application/json'
    }

    matchups_data = get_response_no_params(
        'https://guest.api.arcadia.pinnacle.com/0.1/leagues/493/matchups?brandId=0', headers)
    markets_data = get_response_no_params(
        'https://guest.api.arcadia.pinnacle.com/0.1/leagues/493/markets/straight', headers)

    if matchups_data and markets_data:
        result = process_matchups(matchups_data)
        special_to_parent = process_specials(matchups_data, result)
        process_markets(markets_data, result, special_to_parent)

        # save_result_to_file(result, 'example_pinnacle_ncaab.json')
    return result


def pinnacle_ucl():
    """
    Fetches and processes UEFA Champions League data from Pinnacle.
    """
    headers = {
        'sec-ch-ua-platform': 'Windows',
        'X-Device-UUID': os.getenv('PINNACLE_DEVICE_UUID'),
        'Referer': 'https://www.pinnacle.com/',
        'sec-ch-ua': 'Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
        'X-API-Key': os.getenv('PINNACLE_API_KEY'),
        'sec-ch-ua-mobile': '?0',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
        'Accept': 'application/json',
        'DNT': '1',
        'Content-Type': 'application/json'
    }

    matchups_data = get_response_no_params(
        'https://guest.api.arcadia.pinnacle.com/0.1/leagues/2627/matchups?brandId=0', headers)
    markets_data = get_response_no_params(
        'https://guest.api.arcadia.pinnacle.com/0.1/leagues/2627/markets/straight', headers)

    if matchups_data and markets_data:
        result = process_matchups(matchups_data, switch_home_away=True)
        special_to_parent = process_specials(matchups_data, result)
        process_markets(markets_data, result, special_to_parent)

        # save_result_to_file(result, 'example_pinnacle_ucl.json')
        return result


def pinnacle_epl():
    """
    Fetches and processes English Premier League data from Pinnacle.
    """
    headers = {
        'sec-ch-ua-platform': 'Windows',
        'X-Device-UUID': os.getenv('PINNACLE_DEVICE_UUID'),
        'Referer': 'https://www.pinnacle.com/',
        'sec-ch-ua': 'Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
        'X-API-Key': os.getenv('PINNACLE_API_KEY'),
        'sec-ch-ua-mobile': '?0',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
        'Accept': 'application/json',
        'DNT': '1',
        'Content-Type': 'application/json'
    }

    matchups_data = get_response_no_params(
        'https://guest.api.arcadia.pinnacle.com/0.1/leagues/1980/matchups?brandId=0', headers)
    markets_data = get_response_no_params(
        'https://guest.api.arcadia.pinnacle.com/0.1/leagues/1980/markets/straight', headers)

    if matchups_data and markets_data:
        result = process_matchups(matchups_data, switch_home_away=True)
        special_to_parent = process_specials(matchups_data, result)
        process_markets(markets_data, result, special_to_parent)

        # save_result_to_file(result, 'example_pinnacle_epl.json')
        return result


def pinnacle_shl():
    """
    Fetches and processes Swedish Hockey League data from Pinnacle.
    """
    headers = {
        'sec-ch-ua-platform': 'Windows',
        'X-Device-UUID': os.getenv('PINNACLE_DEVICE_UUID'),
        'Referer': 'https://www.pinnacle.com/',
        'sec-ch-ua': 'Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
        'X-API-Key': os.getenv('PINNACLE_API_KEY'),
        'sec-ch-ua-mobile': '?0',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
        'Accept': 'application/json',
        'DNT': '1',
        'Content-Type': 'application/json'
    }

    matchups_data = get_response_no_params(
        'https://guest.api.arcadia.pinnacle.com/0.1/leagues/1517/matchups?brandId=0', headers)
    markets_data = get_response_no_params(
        'https://guest.api.arcadia.pinnacle.com/0.1/leagues/1517/markets/straight', headers)

    if matchups_data and markets_data:
        result = process_matchups(matchups_data, switch_home_away=True)
        special_to_parent = process_specials(matchups_data, result)
        process_markets(markets_data, result, special_to_parent)

        # save_result_to_file(result, 'example_pinnacle_shl.json')
        return result


def print_market_types():
    """
    Prints all the possible market types in example_fanduel_nhl.json.
    """
    with open('example_fanduel_nhl.json', 'r') as f:
        data = json.load(f)

    market_types = set()
    for event in data.values():
        for market in event.get('markets', []):
            market_types.add(market.get('marketType'))

    for market_type in sorted(market_types):
        with open('nhl_market_types.txt', 'w') as f:
            for market_type in sorted(market_types):
                f.write(market_type + '\n')
