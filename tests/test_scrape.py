import unittest
from unittest.mock import patch, Mock
from src.scrape import get_response, get_response_no_params, process_fanduel_rows, process_fanduel_markets, process_matchups, process_specials, process_markets


class TestScrape(unittest.TestCase):

    @patch('src.scrape.requests.get')
    def test_get_response_success(self, mock_get):
        mock_response = Mock()
        expected_json = {"key": "value"}
        mock_response.status_code = 200
        mock_response.json.return_value = expected_json
        mock_get.return_value = mock_response

        url = "http://example.com"
        headers = {"header": "value"}
        result = get_response(url, headers)

        self.assertEqual(result, expected_json)
        mock_get.assert_called_once_with(url, headers=headers, params=None)

    @patch('src.scrape.requests.get')
    def test_get_response_failure(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        url = "http://example.com"
        headers = {"header": "value"}
        result = get_response(url, headers)

        self.assertIsNone(result)
        mock_get.assert_called_once_with(url, headers=headers, params=None)

    @patch('src.scrape.requests.get')
    def test_get_response_no_params_success(self, mock_get):
        mock_response = Mock()
        expected_json = {"key": "value"}
        mock_response.status_code = 200
        mock_response.json.return_value = expected_json
        mock_get.return_value = mock_response

        url = "http://example.com"
        headers = {"header": "value"}
        result = get_response_no_params(url, headers)

        self.assertEqual(result, expected_json)
        mock_get.assert_called_once_with(url, headers=headers)

    @patch('src.scrape.requests.get')
    def test_get_response_no_params_failure(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        url = "http://example.com"
        headers = {"header": "value"}
        result = get_response_no_params(url, headers)

        self.assertIsNone(result)
        mock_get.assert_called_once_with(url, headers=headers)

    def test_process_fanduel_rows(self):
        rows = [{"eventId": 1}, {"eventId": 2}]
        data = {"attachments": {"events": {
            "1": {"name": "Event 1"}, "2": {"name": "Event 2"}}}}
        result, seen_event_ids = process_fanduel_rows(rows, data)

        expected_result = {1: {"name": "Event 1"}, 2: {"name": "Event 2"}}
        expected_seen_event_ids = {1, 2}

        self.assertEqual(result, expected_result)
        self.assertEqual(seen_event_ids, expected_seen_event_ids)

    def test_process_fanduel_markets(self):
        markets = {
            "market1": {"eventId": 1, "marketType": "type1", "runners": [{"handicap": 1, "runnerName": "Runner 1", "winRunnerOdds": {"americanDisplayOdds": {"americanOdds": 100}}}]},
            "market2": {"eventId": 2, "marketType": "type2", "runners": [{"handicap": 2, "runnerName": "Runner 2", "winRunnerOdds": {"americanDisplayOdds": {"americanOdds": 200}}}]}
        }
        seen_event_ids = {1, 2}
        result = {1: {"name": "Event 1"}, 2: {"name": "Event 2"}}
        process_fanduel_markets(markets, seen_event_ids, result)

        expected_result = {
            1: {"name": "Event 1", "markets": [{"marketType": "type1", "runners": [{"handicap": 1, "runnerName": "Runner 1", "winRunnerOdds": 100}]}]},
            2: {"name": "Event 2", "markets": [{"marketType": "type2", "runners": [{"handicap": 2, "runnerName":  "Runner 2", "winRunnerOdds": 200}]}]}
        }

        self.assertEqual(result, expected_result)

    def test_process_matchups(self):
        matchups_data = [
            {"id": 1, "participants": [{"alignment": "home", "name": "Home Team"}, {
                "alignment": "away", "name": "Away Team"}]},
            {"id": 2, "participants": [{"alignment": "home", "name": "Home Team 2"}, {
                "alignment": "away", "name": "Away Team 2"}]}
        ]
        result = process_matchups(matchups_data)

        expected_result = {
            1: {"name": "Away Team @ Home Team", "markets": []},
            2: {"name": "Away Team 2 @ Home Team 2", "markets": []}
        }

        self.assertEqual(result, expected_result)

    def test_process_specials(self):
        matchups_data = [
            {"id": 1, "parentId": 10, "special": {"description": "Special 1"}},
            {"id": 2, "parentId": 20, "special": {"description": "Special 2"}}
        ]
        result = {10: {"markets": []}, 20: {"markets": []}}
        special_to_parent = process_specials(matchups_data, result)

        expected_result = {
            10: {"markets": [{"id": 1, "description": "Special 1"}]},
            20: {"markets": [{"id": 2, "description": "Special 2"}]}
        }
        expected_special_to_parent = {1: 10, 2: 20}

        self.assertEqual(result, expected_result)
        self.assertEqual(special_to_parent, expected_special_to_parent)

    def test_process_markets(self):
        markets_data = [
            {"key": "s;0;m", "matchupId": 1, "prices": [
                {"price": 100}, {"price": 200}], "limits": [{"amount": 300}]},
            {"key": "s;0;tt;111.5;home", "matchupId": 1, "prices": [
                {"price": 100}, {"price": 200}], "limits": [{"amount": 300}]}
        ]
        result = {1: {"markets": []}}
        special_to_parent = {}
        process_markets(markets_data, result, special_to_parent)

        expected_result = {
            1: {
                "markets": [
                    {"description": "moneyline", "prices": [
                        {"price": 100}, {"price": 200}], "limit": 300},
                    {"description": "team total", "team": "home", "threshold": "111.5", "prices": [
                        {"price": 100}, {"price": 200}], "limit": 300}
                ]
            }
        }

        self.assertEqual(result, expected_result)


if __name__ == '__main__':
    unittest.main()
