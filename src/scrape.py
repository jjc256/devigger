import requests
import os
import json  # Add import for json module
import datetime
import time
import re


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
    if "competition" in url:
        time.sleep(5)
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print(
            f"FanDuel request failed with status code: {response.status_code}. ID: {params.get('competitionId')}")
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
        print(f"Pinnacle request failed with status code: {response.status_code}")
        return None


def process_fanduel_rows(rows, data, shorten_names=False):
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
            date = data.get("attachments", {}).get(
                "events", {}).get(str(event_id), {}).get("openDate")
            if (" @ " in name or " v " in name):
                name = re.sub(r' \([^)]*\)', '', name)  # Remove anything in parentheses
                if shorten_names:
                    if " @ " in name:
                        name = name.split(" @ ")[0].split(" ")[-1] + " @ " + \
                            name.split(" @ ")[1].split(" ")[-1]
                    elif " v " in name:
                        name = name.split(" v ")[0].split(" ")[-1] + " v " + \
                            name.split(" v ")[1].split(" ")[-1]
                event_date = datetime.datetime.fromisoformat(date.replace("Z", "+00:00"))
                now = datetime.datetime.now(datetime.timezone.utc)
                if now < event_date < (now + datetime.timedelta(hours=24)):
                    result[event_id] = {"name": name}
                    seen_event_ids.add(event_id)
    return result, seen_event_ids


def process_fanduel_markets(markets, seen_event_ids, result, league):
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
            result[event_id]["league"] = league
            market_info = {
                "marketType": market.get("marketType"),
                "externalMarketId": market.get("associatedMarkets")[0].get("externalMarketId"),
                "runners": []
            }
            for runner in market.get("runners", []):
                runner_info = {
                    "selectionId": runner.get("selectionId"),
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


def fanduel_nba(save_to_file=False):
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
        'sec-ch-ua': '"Chromium";v="131", "Google Chrome";v="131", "Not?A_Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
    }

    data = get_response(url, headers, params)
    if data:
        rows = data.get("layout", {}).get("coupons", {}).get(
            "32866", {}).get("display", [])[0].get("rows", [])
        result, seen_event_ids = process_fanduel_rows(rows, data)
        markets = data.get("attachments", {}).get("markets", {})
        process_fanduel_markets(markets, seen_event_ids, result, "NBA")

        if save_to_file:
            save_result_to_file(result, 'example_fanduel_nba.json')
        return result


def fanduel_nfl(save_to_file=False):
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
        'sec-ch-ua': '"Chromium";v="131", "Google Chrome";v="131", "Not?A_Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
    }

    data = get_response(url, headers, params)
    if data:
        rows = list(data.get("attachments", {}).get("events", {}).values())[2:]
        result, seen_event_ids = process_fanduel_rows(rows, data)
        markets = data.get("attachments", {}).get("markets", {})
        process_fanduel_markets(markets, seen_event_ids, result, "NFL")

        if save_to_file:
            save_result_to_file(result, 'example_fanduel_nfl.json')
        return result


def fanduel_nhl(save_to_file=False):
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
        'sec-ch-ua': '"Chromium";v="131", "Google Chrome";v="131", "Not?A_Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
    }

    data = get_response(url, headers, params)
    if data:
        display = data.get("layout", {}).get("coupons", {}).get(
            "35876", {}).get("display", [])
        rows = display[0].get("rows", []) if display else []
        result, seen_event_ids = process_fanduel_rows(rows, data)
        markets = data.get("attachments", {}).get("markets", {})
        process_fanduel_markets(markets, seen_event_ids, result, "NHL")

        if save_to_file:
            save_result_to_file(result, 'example_fanduel_nhl.json')
        return result


def fanduel_ncaaf(save_to_file=False):
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
        'sec-ch-ua': '"Chromium";v="131", "Google Chrome";v="131", "Not?A_Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
    }

    data = get_response(url, headers, params)
    if data:
        # Get all events from the attachments section
        display = data.get("layout", {}).get("coupons", {}).get(
            "2", {}).get("display", [])
        if len(display) > 0:
            rows = display[0].get("rows", [])
        else:
            rows = []
        result, seen_event_ids = process_fanduel_rows(rows, data)
        markets = data.get("attachments", {}).get("markets", {})
        process_fanduel_markets(markets, seen_event_ids, result, "NCAAFB")

        if save_to_file:
            save_result_to_file(result, 'example_fanduel_ncaaf.json')
        return result


def fanduel_ncaab(save_to_file=False):
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
        'sec-ch-ua': '"Chromium";v="131", "Google Chrome";v="131", "Not?A_Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
    }

    data = get_response(url, headers, params)
    if data:
        # Get all events from the attachments section
        rows = []
        for display in data.get("layout", {}).get("coupons", {}).get("9411", {}).get("display", []):
            rows.extend(display.get("rows", []))
        result, seen_event_ids = process_fanduel_rows(rows, data)
        markets = data.get("attachments", {}).get("markets", {})
        process_fanduel_markets(markets, seen_event_ids, result, "NCAAB")

        if save_to_file:
            save_result_to_file(result, 'example_fanduel_ncaab.json')
        return result


def fanduel_ucl(save_to_file=False):
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
        'sec-ch-ua': '"Chromium";v="131", "Google Chrome";v="131", "Not?A_Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
    }

    data = get_response(url, headers, params)
    if data:
        # Get all events from the events section
        rows = list(data.get("attachments", {}).get("events", {}).values())
        result, seen_event_ids = process_fanduel_rows(rows, data)
        markets = data.get("attachments", {}).get("markets", {})
        process_fanduel_markets(markets, seen_event_ids, result, "UCL")

        if save_to_file:
            save_result_to_file(result, 'example_fanduel_ucl.json')
        return result


def fanduel_epl(save_to_file=False):
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
        'sec-ch-ua': '"Chromium";v="131", "Google Chrome";v="131", "Not?A_Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
    }

    data = get_response(url, headers, params)
    if data:
        # Get all events from the events section
        rows = list(data.get("attachments", {}).get("events", {}).values())
        result, seen_event_ids = process_fanduel_rows(rows, data)
        markets = data.get("attachments", {}).get("markets", {})
        process_fanduel_markets(markets, seen_event_ids, result, "EPL")

        if save_to_file:
            save_result_to_file(result, 'example_fanduel_epl.json')
        return result


def fanduel_shl(save_to_file=False):
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
        'sec-ch-ua': '"Chromium";v="131", "Google Chrome";v="131", "Not?A_Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
    }

    data = get_response(url, headers, params)
    if data:
        # Get all events from the events section
        rows = list(data.get("attachments", {}).get("events", {}).values())
        result, seen_event_ids = process_fanduel_rows(rows, data)
        markets = data.get("attachments", {}).get("markets", {})
        process_fanduel_markets(markets, seen_event_ids, result, "SHL")

        if save_to_file:
            save_result_to_file(result, 'example_fanduel_shl.json')
        return result


def fanduel_nla(save_to_file=False):
    """
    Fetches and processes Swiss National League A (NLA) data from Fanduel.
    """
    url = 'https://sbapi.ny.sportsbook.fanduel.com/api/competition-page'
    api_key = os.getenv('FANDUEL_API_KEY')
    params = {
        '_ak': api_key,
        'eventTypeId': '7524',
        'competitionId': '11480943'
    }

    headers = {
        'accept': 'application/json',
        'accept-language': 'en-US,en;q=0.9',
        'dnt': '1',
        'origin': 'https://sportsbook.fanduel.com',
        'referer': 'https://sportsbook.fanduel.com/',
        'sec-ch-ua': '"Chromium";v="131", "Google Chrome";v="131", "Not?A_Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
    }

    data = get_response(url, headers, params)
    if data:
        # Get all events from the events section
        rows = list(data.get("attachments", {}).get("events", {}).values())
        result, seen_event_ids = process_fanduel_rows(rows, data)
        markets = data.get("attachments", {}).get("markets", {})
        process_fanduel_markets(markets, seen_event_ids, result, "NL")

        if save_to_file:
            save_result_to_file(result, 'example_fanduel_nla.json')
        return result


def fanduel_turkish_first(save_to_file=False):
    """
    Fetches and processes Turkish 1st League data from Fanduel.
    """
    url = 'https://sbapi.il.sportsbook.fanduel.com/api/competition-page'
    api_key = os.getenv('FANDUEL_API_KEY')
    params = {
        '_ak': api_key,
        'eventTypeId': '1',
        'competitionId': '175680'
    }

    headers = {
        'accept': 'application/json',
        'accept-language': 'en-US,en;q=0.9',
        'dnt': '1',
        'origin': 'https://sportsbook.fanduel.com',
        'referer': 'https://sportsbook.fanduel.com/',
        'sec-ch-ua': '"Chromium";v="131", "Google Chrome";v="131", "Not?A_Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
    }

    data = get_response(url, headers, params)
    if data:
        # Get all events from the events section
        rows = list(data.get("attachments", {}).get("events", {}).values())
        result, seen_event_ids = process_fanduel_rows(rows, data)
        markets = data.get("attachments", {}).get("markets", {})
        process_fanduel_markets(markets, seen_event_ids, result, "TFL")

        if save_to_file:
            save_result_to_file(result, 'example_fanduel_turkish_first.json')
        return result
    return {}


def fanduel_turkish_super(save_to_file=False):
    """
    Fetches and processes Turkish Super League data from Fanduel.
    """
    url = 'https://sbapi.il.sportsbook.fanduel.com/api/competition-page'
    api_key = os.getenv('FANDUEL_API_KEY')
    params = {
        '_ak': api_key,
        'eventTypeId': '1',
        'competitionId': '194215'
    }

    headers = {
        'accept': 'application/json',
        'accept-language': 'en-US,en;q=0.9',
        'dnt': '1',
        'origin': 'https://sportsbook.fanduel.com',
        'referer': 'https://sportsbook.fanduel.com/',
        'sec-ch-ua': '"Chromium";v="131", "Google Chrome";v="131", "Not?A_Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
    }

    data = get_response(url, headers, params)
    if data:
        # Get all events from the events section
        rows = list(data.get("attachments", {}).get("events", {}).values())
        result, seen_event_ids = process_fanduel_rows(rows, data)
        markets = data.get("attachments", {}).get("markets", {})
        process_fanduel_markets(markets, seen_event_ids, result, "TSL")

        if save_to_file:
            save_result_to_file(result, 'example_fanduel_turkish_super.json')
        return result
    return {}


def fanduel_j1(save_to_file=False):
    """
    Fetches and processes Japanese J1 League data from Fanduel.
    """
    url = 'https://sbapi.il.sportsbook.fanduel.com/api/competition-page'
    api_key = os.getenv('FANDUEL_API_KEY')
    params = {
        '_ak': api_key,
        'eventTypeId': '1',
        'competitionId': '89'
    }

    headers = {
        'accept': 'application/json',
        'accept-language': 'en-US,en;q=0.9',
        'dnt': '1',
        'origin': 'https://sportsbook.fanduel.com',
        'referer': 'https://sportsbook.fanduel.com/',
        'sec-ch-ua': '"Chromium";v="131", "Google Chrome";v="131", "Not?A_Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
    }

    data = get_response(url, headers, params)
    if data:
        rows = list(data.get("attachments", {}).get("events", {}).values())
        result, seen_event_ids = process_fanduel_rows(rows, data)
        markets = data.get("attachments", {}).get("markets", {})
        process_fanduel_markets(markets, seen_event_ids, result, "J1")

        if save_to_file:
            save_result_to_file(result, 'example_fanduel_j1.json')
        return result


def fanduel_ligue1(save_to_file=False):
    """
    Fetches and processes French Ligue 1 data from Fanduel.
    """
    url = 'https://sbapi.il.sportsbook.fanduel.com/api/competition-page'
    api_key = os.getenv('FANDUEL_API_KEY')
    params = {
        '_ak': api_key,
        'eventTypeId': '1',
        'competitionId': '55'
    }

    headers = {
        'accept': 'application/json',
        'accept-language': 'en-US,en;q=0.9',
        'dnt': '1',
        'origin': 'https://sportsbook.fanduel.com',
        'referer': 'https://sportsbook.fanduel.com/',
        'sec-ch-ua': '"Chromium";v="131", "Google Chrome";v="131", "Not?A_Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
    }

    data = get_response(url, headers, params)
    if data:
        rows = list(data.get("attachments", {}).get("events", {}).values())
        result, seen_event_ids = process_fanduel_rows(rows, data)
        markets = data.get("attachments", {}).get("markets", {})
        process_fanduel_markets(markets, seen_event_ids, result, "L1")

        if save_to_file:
            save_result_to_file(result, 'example_fanduel_ligue1.json')
        return result
    return {}


def fanduel_women_friendlies(save_to_file=False):
    """
    Fetches and processes International Women Friendlies data from Fanduel.
    """
    url = 'https://sbapi.ny.sportsbook.fanduel.com/api/competition-page'
    api_key = os.getenv('FANDUEL_API_KEY')
    params = {
        '_ak': api_key,
        'eventTypeId': '1',
        'competitionId': '12200369'
    }

    headers = {
        'accept': 'application/json',
        'accept-language': 'en-US,en;q=0.9',
        'dnt': '1',
        'origin': 'https://sportsbook.fanduel.com',
        'referer': 'https://sportsbook.fanduel.com/',
        'sec-ch-ua': '"Chromium";v="131", "Google Chrome";v="131", "Not?A_Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
    }

    data = get_response(url, headers, params)
    if data:
        # Get all events from the events section
        rows = list(data.get("attachments", {}).get("events", {}).values())
        result, seen_event_ids = process_fanduel_rows(rows, data)
        markets = data.get("attachments", {}).get("markets", {})
        process_fanduel_markets(markets, seen_event_ids, result, "IWF")

        if save_to_file:
            save_result_to_file(result, 'example_fanduel_women_friendlies.json')
        return result
    return {}


def fanduel_greek_super(save_to_file=False):
    """
    Fetches and processes Greek Super League data from Fanduel.
    """
    url = 'https://sbapi.il.sportsbook.fanduel.com/api/competition-page'
    api_key = os.getenv('FANDUEL_API_KEY')
    params = {
        '_ak': api_key,
        'eventTypeId': '1',
        'competitionId': '67'
    }

    headers = {
        'accept': 'application/json',
        'accept-language': 'en-US,en;q=0.9',
        'dnt': '1',
        'origin': 'https://sportsbook.fanduel.com',
        'referer': 'https://sportsbook.fanduel.com/',
        'sec-ch-ua': '"Chromium";v="131", "Google Chrome";v="131", "Not?A_Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
    }

    data = get_response(url, headers, params)
    if data:
        rows = list(data.get("attachments", {}).get("events", {}).values())
        result, seen_event_ids = process_fanduel_rows(rows, data)
        markets = data.get("attachments", {}).get("markets", {})
        process_fanduel_markets(markets, seen_event_ids, result, "GSL")

        if save_to_file:
            save_result_to_file(result, 'example_fanduel_greek_super.json')
        return result
    return {}


def fanduel_cba(save_to_file=False):
    """
    Fetches and processes Chinese Basketball Association data from Fanduel.
    """
    url = 'https://sbapi.il.sportsbook.fanduel.com/api/competition-page'
    api_key = os.getenv('FANDUEL_API_KEY')
    params = {
        '_ak': api_key,
        'eventTypeId': '7522',
        'competitionId': '11555430'
    }

    headers = {
        'accept': 'application/json',
        'accept-language': 'en-US,en;q=0.9',
        'dnt': '1',
        'origin': 'https://sportsbook.fanduel.com',
        'referer': 'https://sportsbook.fanduel.com/',
        'sec-ch-ua': '"Chromium";v="131", "Google Chrome";v="131", "Not?A_Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
    }

    data = get_response(url, headers, params)
    if data:
        rows = list(data.get("attachments", {}).get("events", {}).values())
        result, seen_event_ids = process_fanduel_rows(rows, data)
        markets = data.get("attachments", {}).get("markets", {})
        process_fanduel_markets(markets, seen_event_ids, result, "CBA")

        if save_to_file:
            save_result_to_file(result, 'example_fanduel_cba.json')
        return result
    return {}


def fanduel_ao(save_to_file=False):
    """
    Fetches and processes Australian Open data from Fanduel.
    """
    url = 'https://sbapi.ny.sportsbook.fanduel.com/api/content-managed-page'
    api_key = os.getenv('FANDUEL_API_KEY')
    params = {
        'page': 'CUSTOM',
        'customPageId': 'australian-open',
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
        'sec-ch-ua': '"Chromium";v="131", "Google Chrome";v="131", "Not?A_Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
    }

    data = get_response(url, headers, params)
    if data:
        rows = data.get("layout", {}).get("coupons", {}).get(
            "39449", {}).get("display", [])[0].get("rows", [])
        result, seen_event_ids = process_fanduel_rows(rows, data, shorten_names=True)
        markets = data.get("attachments", {}).get("markets", {})
        process_fanduel_markets(markets, seen_event_ids, result, "AO")

        if save_to_file:
            save_result_to_file(result, 'example_fanduel_ao.json')
        return result


def fanduel_nbb(save_to_file=False):
    """
    Fetches and processes Brazilian Novo Basquete Brasil data from Fanduel.
    """
    url = 'https://sbapi.il.sportsbook.fanduel.com/api/competition-page'
    api_key = os.getenv('FANDUEL_API_KEY')
    params = {
        '_ak': api_key,
        'eventTypeId': '7522',
        'competitionId': '10366095'
    }

    headers = {
        'accept': 'application/json',
        'accept-language': 'en-US,en;q=0.9',
        'dnt': '1',
        'origin': 'https://sportsbook.fanduel.com',
        'referer': 'https://sportsbook.fanduel.com/',
        'sec-ch-ua': '"Chromium";v="131", "Google Chrome";v="131", "Not?A_Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
    }

    data = get_response(url, headers, params)
    if data:
        rows = list(data.get("attachments", {}).get("events", {}).values())
        result, seen_event_ids = process_fanduel_rows(rows, data)
        markets = data.get("attachments", {}).get("markets", {})
        process_fanduel_markets(markets, seen_event_ids, result, "NBB")

        if save_to_file:
            save_result_to_file(result, 'example_fanduel_nbb.json')
        return result
    return {}


def process_matchups(matchups_data, switch_home_away=False, shorten_names=False):
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
                drop_beginning = shorten_names and "/" not in home.get("name")
                home_name = home.get("name") if not drop_beginning else home.get(
                    "name").split(" ")[-1]
                away_name = away.get("name") if not drop_beginning else away.get(
                    "name").split(" ")[-1]
                matchup_name = f"{away_name} @ {home_name}" if not switch_home_away else f"{home_name} v {away_name}"
                if "/" in matchup_name and " v " in matchup_name:
                    # Tennis doubles
                    matchup_name = matchup_name.split(" v ")[0].split("/")[0].replace(" ", "") + "/" + \
                        matchup_name.split(" v ")[0].split("/")[1].replace(" ", "") + " v " + \
                        matchup_name.split(" v ")[1].split("/")[0].replace(" ", "") + "/" + \
                        matchup_name.split(" v ")[1].split("/")[1].replace(" ", "")
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


def pinnacle_nba(save_to_file=False):
    """
    Fetches and processes NBA data from Pinnacle.
    """
    headers = {
        'sec-ch-ua-platform': 'Windows',
        'X-Device-UUID': os.getenv('PINNACLE_DEVICE_UUID'),
        'Referer': 'https://www.pinnacle.com/',
        'sec-ch-ua': 'Chromium";v="131", "Google Chrome";v="131", "Not?A_Brand";v="24"',
        'X-API-Key': os.getenv('PINNACLE_API_KEY'),
        'sec-ch-ua-mobile': '?0',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
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

        if save_to_file:
            save_result_to_file(result, 'example_pinnacle_nba.json')
        return result
    return {}


def pinnacle_nfl(save_to_file=False):
    """
    Fetches and processes NFL data from Pinnacle.
    """
    headers = {
        'sec-ch-ua-platform': 'Windows',
        'X-Device-UUID': os.getenv('PINNACLE_DEVICE_UUID'),
        'Referer': 'https://www.pinnacle.com/',
        'sec-ch-ua': 'Chromium";v="131", "Google Chrome";v="131", "Not?A_Brand";v="24"',
        'X-API-Key': os.getenv('PINNACLE_API_KEY'),
        'sec-ch-ua-mobile': '?0',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
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

        if save_to_file:
            save_result_to_file(result, 'example_pinnacle_nfl.json')
        return result
    return {}


def pinnacle_nhl(save_to_file=False):
    """
    Fetches and processes NHL data from Pinnacle.
    """
    headers = {
        'sec-ch-ua-platform': 'Windows',
        'X-Device-UUID': os.getenv('PINNACLE_DEVICE_UUID'),
        'Referer': 'https://www.pinnacle.com/',
        'sec-ch-ua': 'Chromium";v="131", "Google Chrome";v="131", "Not?A_Brand";v="24"',
        'X-API-Key': os.getenv('PINNACLE_API_KEY'),
        'sec-ch-ua-mobile': '?0',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
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

        if save_to_file:
            save_result_to_file(result, 'example_pinnacle_nhl.json')
        return result
    return {}


def pinnacle_ncaaf(save_to_file=False):
    """
    Fetches and processes NCAAF data from Pinnacle.
    """
    headers = {
        'sec-ch-ua-platform': 'Windows',
        'X-Device-UUID': os.getenv('PINNACLE_DEVICE_UUID'),
        'Referer': 'https://www.pinnacle.com/',
        'sec-ch-ua': 'Chromium";v="131", "Google Chrome";v="131", "Not?A_Brand";v="24"',
        'X-API-Key': os.getenv('PINNACLE_API_KEY'),
        'sec-ch-ua-mobile': '?0',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
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

        if save_to_file:
            save_result_to_file(result, 'example_pinnacle_ncaaf.json')
        return result
    return {}


def pinnacle_ncaab(save_to_file=False):
    """
    Fetches and processes NCAAB data from Pinnacle.
    """
    headers = {
        'sec-ch-ua-platform': 'Windows',
        'X-Device-UUID': os.getenv('PINNACLE_DEVICE_UUID'),
        'Referer': 'https://www.pinnacle.com/',
        'sec-ch-ua': 'Chromium";v="131", "Google Chrome";v="131", "Not?A_Brand";v="24"',
        'X-API-Key': os.getenv('PINNACLE_API_KEY'),
        'sec-ch-ua-mobile': '?0',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
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

        if save_to_file:
            save_result_to_file(result, 'example_pinnacle_ncaab.json')
        return result
    return {}


def pinnacle_ucl(save_to_file=False):
    """
    Fetches and processes UEFA Champions League data from Pinnacle.
    """
    headers = {
        'sec-ch-ua-platform': 'Windows',
        'X-Device-UUID': os.getenv('PINNACLE_DEVICE_UUID'),
        'Referer': 'https://www.pinnacle.com/',
        'sec-ch-ua': 'Chromium";v="131", "Google Chrome";v="131", "Not?A_Brand";v="24"',
        'X-API-Key': os.getenv('PINNACLE_API_KEY'),
        'sec-ch-ua-mobile': '?0',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
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

        if save_to_file:
            save_result_to_file(result, 'example_pinnacle_ucl.json')
        return result
    return {}


def pinnacle_epl(save_to_file=False):
    """
    Fetches and processes English Premier League data from Pinnacle.
    """
    headers = {
        'sec-ch-ua-platform': 'Windows',
        'X-Device-UUID': os.getenv('PINNACLE_DEVICE_UUID'),
        'Referer': 'https://www.pinnacle.com/',
        'sec-ch-ua': 'Chromium";v="131", "Google Chrome";v="131", "Not?A_Brand";v="24"',
        'X-API-Key': os.getenv('PINNACLE_API_KEY'),
        'sec-ch-ua-mobile': '?0',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
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

        if save_to_file:
            save_result_to_file(result, 'example_pinnacle_epl.json')
        return result
    return {}


def pinnacle_shl(save_to_file=False):
    """
    Fetches and processes Swedish Hockey League data from Pinnacle.
    """
    headers = {
        'sec-ch-ua-platform': 'Windows',
        'X-Device-UUID': os.getenv('PINNACLE_DEVICE_UUID'),
        'Referer': 'https://www.pinnacle.com/',
        'sec-ch-ua': 'Chromium";v="131", "Google Chrome";v="131", "Not?A_Brand";v="24"',
        'X-API-Key': os.getenv('PINNACLE_API_KEY'),
        'sec-ch-ua-mobile': '?0',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
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

        if save_to_file:
            save_result_to_file(result, 'example_pinnacle_shl.json')
        return result
    return {}


def pinnacle_nla(save_to_file=False):
    """
    Fetches and processes Swiss National League A (NLA) data from Pinnacle.
    """
    headers = {
        'sec-ch-ua-platform': 'Windows',
        'X-Device-UUID': os.getenv('PINNACLE_DEVICE_UUID'),
        'Referer': 'https://www.pinnacle.com/',
        'sec-ch-ua': 'Chromium";v="131", "Google Chrome";v="131", "Not?A_Brand";v="24"',
        'X-API-Key': os.getenv('PINNACLE_API_KEY'),
        'sec-ch-ua-mobile': '?0',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        'Accept': 'application/json',
        'DNT': '1',
        'Content-Type': 'application/json'
    }

    matchups_data = get_response_no_params(
        'https://guest.api.arcadia.pinnacle.com/0.1/leagues/1532/matchups?brandId=0', headers)
    markets_data = get_response_no_params(
        'https://guest.api.arcadia.pinnacle.com/0.1/leagues/1532/markets/straight', headers)

    if matchups_data and markets_data:
        result = process_matchups(matchups_data, switch_home_away=True)
        special_to_parent = process_specials(matchups_data, result)
        process_markets(markets_data, result, special_to_parent)

        if save_to_file:
            save_result_to_file(result, 'example_pinnacle_nla.json')
        return result
    return {}


def pinnacle_turkish_first(save_to_file=False):
    """
    Fetches and processes Turkish 1st League data from Pinnacle.
    """
    headers = {
        'sec-ch-ua-platform': 'Windows',
        'X-Device-UUID': os.getenv('PINNACLE_DEVICE_UUID'),
        'Referer': 'https://www.pinnacle.com/',
        'sec-ch-ua': 'Chromium";v="131", "Google Chrome";v="131", "Not?A_Brand";v="24"',
        'X-API-Key': os.getenv('PINNACLE_API_KEY'),
        'sec-ch-ua-mobile': '?0',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        'Accept': 'application/json',
        'DNT': '1',
        'Content-Type': 'application/json'
    }

    matchups_data = get_response_no_params(
        'https://guest.api.arcadia.pinnacle.com/0.1/leagues/2578/matchups?brandId=0', headers)
    markets_data = get_response_no_params(
        'https://guest.api.arcadia.pinnacle.com/0.1/leagues/2578/markets/straight', headers)

    if matchups_data and markets_data:
        result = process_matchups(matchups_data, switch_home_away=True)
        special_to_parent = process_specials(matchups_data, result)
        process_markets(markets_data, result, special_to_parent)

        if save_to_file:
            save_result_to_file(result, 'example_pinnacle_turkish_first.json')
        return result
    return {}


def pinnacle_turkish_super(save_to_file=False):
    """
    Fetches and processes Turkish Super League data from Pinnacle.
    """
    headers = {
        'sec-ch-ua-platform': 'Windows',
        'X-Device-UUID': os.getenv('PINNACLE_DEVICE_UUID'),
        'Referer': 'https://www.pinnacle.com/',
        'sec-ch-ua': 'Chromium";v="131", "Google Chrome";v="131", "Not?A_Brand";v="24"',
        'X-API-Key': os.getenv('PINNACLE_API_KEY'),
        'sec-ch-ua-mobile': '?0',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        'Accept': 'application/json',
        'DNT': '1',
        'Content-Type': 'application/json'
    }

    matchups_data = get_response_no_params(
        'https://guest.api.arcadia.pinnacle.com/0.1/leagues/2592/matchups?brandId=0', headers)
    markets_data = get_response_no_params(
        'https://guest.api.arcadia.pinnacle.com/0.1/leagues/2592/markets/straight', headers)

    if matchups_data and markets_data:
        result = process_matchups(matchups_data, switch_home_away=True)
        special_to_parent = process_specials(matchups_data, result)
        process_markets(markets_data, result, special_to_parent)

        if save_to_file:
            save_result_to_file(result, 'example_pinnacle_turkish_super.json')
        return result
    return {}


def pinnacle_j1(save_to_file=False):
    """
    Fetches and processes Japanese J1 League data from Pinnacle.
    """
    headers = {
        'sec-ch-ua-platform': 'Windows',
        'X-Device-UUID': os.getenv('PINNACLE_DEVICE_UUID'),
        'Referer': 'https://www.pinnacle.com/',
        'sec-ch-ua': 'Chromium";v="131", "Google Chrome";v="131", "Not?A_Brand";v="24"',
        'X-API-Key': os.getenv('PINNACLE_API_KEY'),
        'sec-ch-ua-mobile': '?0',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        'Accept': 'application/json',
        'DNT': '1',
        'Content-Type': 'application/json'
    }

    matchups_data = get_response_no_params(
        'https://guest.api.arcadia.pinnacle.com/0.1/leagues/2157/matchups?brandId=0', headers)
    markets_data = get_response_no_params(
        'https://guest.api.arcadia.pinnacle.com/0.1/leagues/2157/markets/straight', headers)

    if matchups_data and markets_data:
        result = process_matchups(matchups_data, switch_home_away=True)
        special_to_parent = process_specials(matchups_data, result)
        process_markets(markets_data, result, special_to_parent)

        if save_to_file:
            save_result_to_file(result, 'example_pinnacle_j1.json')
        return result
    return {}


def pinnacle_ligue1(save_to_file=False):
    """
    Fetches and processes French Ligue 1 data from Pinnacle.
    """
    headers = {
        'sec-ch-ua-platform': 'Windows',
        'X-Device-UUID': os.getenv('PINNACLE_DEVICE_UUID'),
        'Referer': 'https://www.pinnacle.com/',
        'sec-ch-ua': 'Chromium";v="131", "Google Chrome";v="131", "Not?A_Brand";v="24"',
        'X-API-Key': os.getenv('PINNACLE_API_KEY'),
        'sec-ch-ua-mobile': '?0',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        'Accept': 'application/json',
        'DNT': '1',
        'Content-Type': 'application/json'
    }

    matchups_data = get_response_no_params(
        'https://guest.api.arcadia.pinnacle.com/0.1/leagues/2036/matchups?brandId=0', headers)
    markets_data = get_response_no_params(
        'https://guest.api.arcadia.pinnacle.com/0.1/leagues/2036/markets/straight', headers)

    if matchups_data and markets_data:
        result = process_matchups(matchups_data, switch_home_away=True)
        special_to_parent = process_specials(matchups_data, result)
        process_markets(markets_data, result, special_to_parent)

        if save_to_file:
            save_result_to_file(result, 'example_pinnacle_ligue1.json')
        return result
    return {}


def pinnacle_women_friendlies(save_to_file=False):
    """
    Fetches and processes International Women Friendlies data from Pinnacle.
    """
    headers = {
        'sec-ch-ua-platform': 'Windows',
        'X-Device-UUID': os.getenv('PINNACLE_DEVICE_UUID'),
        'Referer': 'https://www.pinnacle.com/',
        'sec-ch-ua': 'Chromium";v="131", "Google Chrome";v="131", "Not?A_Brand";v="24"',
        'X-API-Key': os.getenv('PINNACLE_API_KEY'),
        'sec-ch-ua-mobile': '?0',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        'Accept': 'application/json',
        'DNT': '1',
        'Content-Type': 'application/json'
    }

    matchups_data = get_response_no_params(
        'https://guest.api.arcadia.pinnacle.com/0.1/leagues/2116/matchups?brandId=0', headers)
    markets_data = get_response_no_params(
        'https://guest.api.arcadia.pinnacle.com/0.1/leagues/2116/markets/straight', headers)

    if matchups_data and markets_data:
        result = process_matchups(matchups_data, switch_home_away=True)
        special_to_parent = process_specials(matchups_data, result)
        process_markets(markets_data, result, special_to_parent)

        if save_to_file:
            save_result_to_file(result, 'example_pinnacle_women_friendlies.json')
        return result
    return {}


def pinnacle_greek_super(save_to_file=False):
    """
    Fetches and processes Greek Super League data from Pinnacle.
    """
    headers = {
        'sec-ch-ua-platform': 'Windows',
        'X-Device-UUID': os.getenv('PINNACLE_DEVICE_UUID'),
        'Referer': 'https://www.pinnacle.com/',
        'sec-ch-ua': 'Chromium";v="131", "Google Chrome";v="131", "Not?A_Brand";v="24"',
        'X-API-Key': os.getenv('PINNACLE_API_KEY'),
        'sec-ch-ua-mobile': '?0',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        'Accept': 'application/json',
        'DNT': '1',
        'Content-Type': 'application/json'
    }

    matchups_data = get_response_no_params(
        'https://guest.api.arcadia.pinnacle.com/0.1/leagues/2081/matchups?brandId=0', headers)
    markets_data = get_response_no_params(
        'https://guest.api.arcadia.pinnacle.com/0.1/leagues/2081/markets/straight', headers)

    if matchups_data and markets_data:
        result = process_matchups(matchups_data, switch_home_away=True)
        special_to_parent = process_specials(matchups_data, result)
        process_markets(markets_data, result, special_to_parent)

        if save_to_file:
            save_result_to_file(result, 'example_pinnacle_greek_super.json')
        return result
    return {}


def pinnacle_cba(save_to_file=False):
    """
    Fetches and processes Chinese Basketball Association data from Pinnacle.
    """
    headers = {
        'sec-ch-ua-platform': 'Windows',
        'X-Device-UUID': os.getenv('PINNACLE_DEVICE_UUID'),
        'Referer': 'https://www.pinnacle.com/',
        'sec-ch-ua': 'Chromium";v="131", "Google Chrome";v="131", "Not?A_Brand";v="24"',
        'X-API-Key': os.getenv('PINNACLE_API_KEY'),
        'sec-ch-ua-mobile': '?0',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        'Accept': 'application/json',
        'DNT': '1',
        'Content-Type': 'application/json'
    }

    matchups_data = get_response_no_params(
        'https://guest.api.arcadia.pinnacle.com/0.1/leagues/303/matchups?brandId=0', headers)
    markets_data = get_response_no_params(
        'https://guest.api.arcadia.pinnacle.com/0.1/leagues/303/markets/straight', headers)

    if matchups_data and markets_data:
        result = process_matchups(matchups_data)
        special_to_parent = process_specials(matchups_data, result)
        process_markets(markets_data, result, special_to_parent)

        if save_to_file:
            save_result_to_file(result, 'example_pinnacle_cba.json')
        return result
    return {}


def pinnacle_ao(save_to_file=False):
    """
    Fetches and processes Australian Open tennis data from Pinnacle.
    """
    headers = {
        'sec-ch-ua-platform': 'Windows',
        'X-Device-UUID': os.getenv('PINNACLE_DEVICE_UUID'),
        'Referer': 'https://www.pinnacle.com/',
        'sec-ch-ua': 'Chromium";v="131", "Google Chrome";v="131", "Not?A_Brand";v="24"',
        'X-API-Key': os.getenv('PINNACLE_API_KEY'),
        'sec-ch-ua-mobile': '?0',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        'Accept': 'application/json',
        'DNT': '1',
        'Content-Type': 'application/json'
    }

    matchups_data = get_response_no_params(
        'https://guest.api.arcadia.pinnacle.com/0.1/sports/33/matchups?withSpecials=false&brandId=0', headers)
    markets_data = get_response_no_params(
        'https://guest.api.arcadia.pinnacle.com/0.1/sports/33/markets/straight?primaryOnly=false&withSpecials=false', headers)

    if matchups_data and markets_data:
        result = process_matchups(matchups_data, switch_home_away=True, shorten_names=True)
        special_to_parent = process_specials(matchups_data, result)
        process_markets(markets_data, result, special_to_parent)

        if save_to_file:
            save_result_to_file(result, 'example_pinnacle_ao.json')
        return result
    return {}


def pinnacle_nbb(save_to_file=False):
    """
    Fetches and processes Brazilian Novo Basquete Brasil data from Pinnacle.
    """
    headers = {
        'sec-ch-ua-platform': 'Windows',
        'X-Device-UUID': os.getenv('PINNACLE_DEVICE_UUID'),
        'Referer': 'https://www.pinnacle.com/',
        'sec-ch-ua': 'Chromium";v="131", "Google Chrome";v="131", "Not?A_Brand";v="24"',
        'X-API-Key': os.getenv('PINNACLE_API_KEY'),
        'sec-ch-ua-mobile': '?0',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        'Accept': 'application/json',
        'DNT': '1',
        'Content-Type': 'application/json'
    }

    matchups_data = get_response_no_params(
        'https://guest.api.arcadia.pinnacle.com/0.1/leagues/303/matchups?brandId=0', headers)
    markets_data = get_response_no_params(
        'https://guest.api.arcadia.pinnacle.com/0.1/leagues/303/markets/straight', headers)

    if matchups_data and markets_data:
        result = process_matchups(matchups_data)
        special_to_parent = process_specials(matchups_data, result)
        process_markets(markets_data, result, special_to_parent)

        if save_to_file:
            save_result_to_file(result, 'example_pinnacle_cba.json')
        return result
    return {}


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


# Call all functions and save results when executed directly
if __name__ == "__main__":

    # fanduel_nba(save_to_file=True)
    # fanduel_nfl(save_to_file=True)
    # fanduel_nhl(save_to_file=True)
    # fanduel_ncaaf(save_to_file=True)
    # fanduel_ncaab(save_to_file=True)
    # fanduel_ucl(save_to_file=True)
    # fanduel_epl(save_to_file=True)
    # fanduel_shl(save_to_file=True)
    # fanduel_nla(save_to_file=True)
    # fanduel_turkish_first(save_to_file=True)
    # fanduel_turkish_super(save_to_file=True)
    # fanduel_j1(save_to_file=True)
    # fanduel_ligue1(save_to_file=True)
    # fanduel_women_friendlies(save_to_file=True)
    # fanduel_greek_super(save_to_file=True)
    # fanduel_cba(save_to_file=True)
    fanduel_ao(save_to_file=True)

    # pinnacle_nba(save_to_file=True)
    # pinnacle_nfl(save_to_file=True)
    # pinnacle_nhl(save_to_file=True)
    # pinnacle_ncaaf(save_to_file=True)
    # pinnacle_ncaab(save_to_file=True)
    # pinnacle_ucl(save_to_file=True)
    # pinnacle_epl(save_to_file=True)
    # pinnacle_shl(save_to_file=True)
    # pinnacle_nla(save_to_file=True)
    # pinnacle_turkish_first(save_to_file=True)
    # pinnacle_turkish_super(save_to_file=True)
    # pinnacle_j1(save_to_file=True)
    # pinnacle_ligue1(save_to_file=True)
    # pinnacle_women_friendlies(save_to_file=True)
    # pinnacle_greek_super(save_to_file=True)
    # pinnacle_cba(save_to_file=True)
    pinnacle_ao(save_to_file=True)
