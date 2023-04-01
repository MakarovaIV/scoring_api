import unittest

from scoring_api import api
from tests.case_decorator import cases


class TestCharField(unittest.TestCase):
    def setUp(self) -> None:
        self.field = api.CharField()

    @cases([
        '',
        "text",
        str(1),
    ])
    def test_field_is_valid(self, value):
        self.assertTrue(self.field.validate(value))

    @cases([
        0,
        {},
        [],
        1
    ])
    def test_field_not_valid(self, value):
        result = self.field.validate(value)
        self.assertIsInstance(result, ValueError)


class TestArgumentsField(unittest.TestCase):
    def setUp(self) -> None:
        self.field = api.ArgumentsField()
    @cases([
        {},
        {"key": "value"},
        dict(key="value")
    ])
    def test_field_is_valid(self, value):
        self.assertTrue(self.field.validate(value))

    @cases([
        0,
        "",
        [],
        1
    ])
    def test_field_not_valid(self, value):
        result = self.field.validate(value)
        self.assertIsInstance(result, ValueError)


class TestEmailField(unittest.TestCase):
    def setUp(self) -> None:
        self.field = api.EmailField()
    @cases([
        "email@mail.ru",
        "123@gm.com"
    ])
    def test_field_is_valid(self, value):
        self.assertTrue(self.field.validate(value))

    @cases([
        {},
        "",
        "emailmail.ru",
        "1@",
        1
    ])
    def test_field_not_valid(self, value):
        result = self.field.validate(value)
        self.assertIsInstance(result, ValueError)


class TestPhoneField(unittest.TestCase):
    def setUp(self) -> None:
        self.field = api.PhoneField()
    @cases([
        79001002345,
        '79001002345'
    ])
    def test_field_is_valid(self, value):
        self.assertTrue(self.field.validate(value))

    @cases([
        {},
        "",
        1,
        89001002345,
        '89001002345',
        '7-900-100-2345',
        790010023456
    ])
    def test_field_not_valid(self, value):
        result = self.field.validate(value)
        self.assertIsInstance(result, ValueError)


class TestDateField(unittest.TestCase):
    def setUp(self) -> None:
        self.field = api.DateField()
    @cases([
        '11.03.1980'
    ])
    def test_field_is_valid(self, value):
        self.assertTrue(self.field.validate(value))

    @cases([
        0,
        [],
        {},
        1,
        '11-03-1980',
        '11/03/1980'

    ])
    def test_field_not_valid(self, value):
        result = self.field.validate(value)
        self.assertIsInstance(result, ValueError)


class TestBirthDayField(unittest.TestCase):
    def setUp(self) -> None:
        self.field = api.BirthDayField()
    @cases([
        '11.03.1980'
    ])
    def test_field_is_valid(self, value):
        self.assertTrue(self.field.validate(value))

    @cases([
        0,
        [],
        {},
        1,
        '11-03-1980',
        '11.03.1900'
    ])
    def test_field_not_valid(self, value):
        result = self.field.validate(value)
        self.assertIsInstance(result, ValueError)


class TestGenderField(unittest.TestCase):
    def setUp(self) -> None:
        self.field = api.GenderField()
    @cases([
        0,
        1,
        2
    ])
    def test_field_is_valid(self, value):
        self.assertTrue(self.field.validate(value))

    @cases([
        "",
        '0',
        3,
    ])
    def test_field_not_valid(self, value):
        result = self.field.validate(value)
        self.assertIsInstance(result, ValueError)


class TestClientIDsField(unittest.TestCase):
    def setUp(self) -> None:
        self.field = api.ClientIDsField()
    @cases([
        [],
        [0],
        [1, 2]
    ])
    def test_field_is_valid(self, value):
        self.assertTrue(self.field.validate(value))

    @cases([
        {},
        0,
        "",
        3,
        ["a"]
    ])
    def test_field_not_valid(self, value):
        result = self.field.validate(value)
        self.assertIsInstance(result, ValueError)


if __name__ == "__main__":
    unittest.main()
