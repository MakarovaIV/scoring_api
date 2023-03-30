import hashlib
import unittest
import datetime
from unittest.mock import Mock

from scoring_api import api
from tests.case_decorator import cases


class TestClientsInterestsHandler(unittest.TestCase):
    @cases([
        {"client_ids": [1, 2, 3], "date": datetime.datetime.today().strftime("%d.%m.%Y")},
        {"client_ids": [1, 2], "date": "19.07.2017"},
        {"client_ids": [0]},
    ])
    def test_clients_interests_handler_is_valid(self, value):
        token = hashlib.sha512((datetime.datetime.now().strftime("%Y%m%d%H") + api.ADMIN_SALT)
                               .encode('utf-8')).hexdigest()
        request = {"body": {"account": "horns&hoofs",
                            "login": "h&f",
                            "method": "clients_interests",
                            "token": token,
                            "arguments": value}}
        store = Mock()
        result = api.method_handler(request, {}, store)
        response, code = result
        self.assertEqual(code, 200)

    @cases([
        {"client_ids": {}},
    ])
    def test_clients_interests_handler_not_valid(self, value):
        request = {"body": {"account": "horns&hoofs",
                            "login": "h&f",
                            "method": "clients_interests",
                            "token": "token",
                            "arguments": value}}
        store = Mock()
        result = api.method_handler(request, {}, store)
        response, code = result
        self.assertEqual(code, api.INVALID_REQUEST)


class TestOnlineScoreHandler(unittest.TestCase):
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
    def test_online_score_handler_is_valid(self, value):
        token = hashlib.sha512((datetime.datetime.now().strftime("%Y%m%d%H") + api.ADMIN_SALT)
                               .encode('utf-8')).hexdigest()
        request = {"body": {"account": "horns&hoofs",
                            "login": "admin",
                            "method": "online_score",
                            "token": token,
                            "arguments": value}}
        store = Mock()
        result = api.method_handler(request, {}, store)
        response, code = result
        self.assertEqual(code, 200)

    @cases([
        {"phone": "79175002040"},
    ])
    def test_online_score_handler_forbidden(self, value):
        token = hashlib.sha512((datetime.datetime.now().strftime("%Y%m%d%H") + api.ADMIN_SALT)
                               .encode('utf-8')).hexdigest()
        request = {"body": {"account": "horns&hoofs",
                            "login": "admin",
                            "method": "online_score",
                            "token": "token",
                            "arguments": value}}
        store = Mock()
        result = api.method_handler(request, {}, store)
        response, code = result
        self.assertEqual(code, api.INVALID_REQUEST)

    @cases([
        {"phone": "79175002040"},
    ])
    def test_online_score_handler_forbidden(self, value):
        request = {"body": {"account": "horns&hoofs",
                            "login": "h&f",
                            "method": "online_score",
                            "token": "token",
                            "arguments": value}}
        store = Mock()
        result = api.method_handler(request, {}, store)
        response, code = result
        self.assertEqual(code, api.FORBIDDEN)


if __name__ == "__main__":
    unittest.main()
