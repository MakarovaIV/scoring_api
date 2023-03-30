import datetime
import unittest

from scoring_api import api
from tests.case_decorator import cases


class TestMethod(unittest.TestCase):
    @cases([
        {"account": "", "login": "", "method": "", "token": "", "arguments": {}},
        {"account": "u", "login": "user", "method": "", "token": "", "arguments": {}},
        {"account": "", "login": "user", "method": "online_score", "token": "", "arguments": {}},
    ])
    def test_request_is_valid(self, value):
        result = api.MethodRequest(value)
        self.assertTrue(result.isvalid())

    @cases([
        {"account": "", "method": "", "token": "", "arguments": {}},
        {"account": "", "login": "", "token": "", "arguments": {}},
        {"account": "", "login": "", "method": "", "token": ""},
        {},
    ])
    def test_request_not_valid(self, value):
        result = api.MethodRequest(value)
        success, error_list = result.isvalid()
        self.assertFalse(success)


class TestClientsInterestsRequest(unittest.TestCase):
    @cases([
        {"client_ids": [1, 2, 3], "date": datetime.datetime.today().strftime("%d.%m.%Y")},
        {"client_ids": [1, 2], "date": "19.07.2017"},
        {"client_ids": [0]},
    ])
    def test_clients_interest_request_is_valid(self, value):
        request = {"account": "horns&hoofs", "login": "h&f", "method": "clients_interests", "arguments": value}
        result = api.MethodRequest(request)
        self.assertTrue(result.isvalid())

    @cases([
        {},
        {"date": "20.07.2017"},
        {"client_ids": [], "date": "20.07.2017"},
        {"client_ids": {1: 2}, "date": "20.07.2017"},
        {"client_ids": ["1", "2"], "date": "20.07.2017"},
        {"client_ids": [1, 2], "date": "XXX"},
    ])
    def test_clients_interest_request_not_valid(self, value):
        request = {"account": "horns&hoofs", "login": "h&f", "method": "clients_interests", "arguments": value}
        result = api.MethodRequest(request)
        success, error_list = result.isvalid()
        self.assertFalse(success)


class TestOnlineScoreRequest(unittest.TestCase):
    @cases([
        {"phone": "79175002040", "email": "stupnikov@otus.ru"},
        {"phone": 79175002040, "email": "stupnikov@otus.ru"},
        {"gender": 1, "birthday": "01.01.2000", "first_name": "a", "last_name": "b"},
        {"gender": 0, "birthday": "01.01.2000"},
        {"gender": 2, "birthday": "01.01.2000"},
        {"first_name": "a", "last_name": "b"},
        {"phone": "79175002040", "email": "stupnikov@otus.ru", "gender": 1, "birthday": "01.01.2000",
         "first_name": "a", "last_name": "b"},
    ])
    def test_online_score_request_is_valid(self, value):
        request = {"account": "horns&hoofs", "login": "h&f", "method": "clients_interests", "arguments": value}
        result = api.MethodRequest(request)
        self.assertTrue(result.isvalid())

    @cases([
        {},
        {"phone": "79175002040"},
        {"phone": "89175002040", "email": "stupnikov@otus.ru"},
        {"phone": "79175002040", "email": "stupnikovotus.ru"},
        {"phone": "79175002040", "email": "stupnikov@otus.ru", "gender": -1},
        {"phone": "79175002040", "email": "stupnikov@otus.ru", "gender": "1"},
        {"phone": "79175002040", "email": "stupnikov@otus.ru", "gender": 1, "birthday": "01.01.1890"},
        {"phone": "79175002040", "email": "stupnikov@otus.ru", "gender": 1, "birthday": "XXX"},
        {"phone": "79175002040", "email": "stupnikov@otus.ru", "gender": 1, "birthday": "01.01.2000", "first_name": 1},
        {"phone": "79175002040", "email": "stupnikov@otus.ru", "gender": 1, "birthday": "01.01.2000",
         "first_name": "s", "last_name": 2},
        {"phone": "79175002040", "birthday": "01.01.2000", "first_name": "s"},
        {"email": "stupnikov@otus.ru", "gender": 1, "last_name": 2},
    ])
    def test_online_score_request_not_valid(self, value):
        request = {"account": "horns&hoofs", "login": "h&f", "method": "clients_interests", "arguments": value}
        result = api.MethodRequest(request)
        success, error_list = result.isvalid()
        self.assertFalse(success)


if __name__ == "__main__":
    unittest.main()
