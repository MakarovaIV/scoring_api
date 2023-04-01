#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import datetime
import logging
import hashlib
import re
import uuid
from optparse import OptionParser
from http.server import BaseHTTPRequestHandler, HTTPServer
from weakref import WeakKeyDictionary

from scoring_api import scoring
from scoring_api.store import Store

SALT = "Otus"
ADMIN_LOGIN = "admin"
ADMIN_SALT = "42"
OK = 200
BAD_REQUEST = 400
FORBIDDEN = 403
NOT_FOUND = 404
INVALID_REQUEST = 422
INTERNAL_ERROR = 500
ERRORS = {
    BAD_REQUEST: "Bad Request",
    FORBIDDEN: "Forbidden",
    NOT_FOUND: "Not Found",
    INVALID_REQUEST: "Invalid Request",
    INTERNAL_ERROR: "Internal Server Error",
}
UNKNOWN = 0
MALE = 1
FEMALE = 2
GENDERS = {
    UNKNOWN: "unknown",
    MALE: "male",
    FEMALE: "female",
}
MAX_AGE = 70

STORE = None
REDIS_CONFIG = {
    "host": 'localhost',
    "port": 6379,
    "db": 0,
    "socket_timeout": 3,
    "socket_connect_timeout": 3,
}
REDIS_CUSTOM_CONFIG = {
    "reconnect_attempts": 5
}


class BaseField:
    def __init__(self, required=False, nullable=False):
        self.required = required
        self.nullable = nullable
        self.data = WeakKeyDictionary()

    def __set_name__(self, owner, name):
        self.name = name

    def __set__(self, instance, value):
        self.data[instance] = value

    def __get__(self, instance, owner):
        return self.data.get(instance)

    def validate(self, value):
        if self.required and value is None:
            return ValueError(f'The field {type(self).__name__} is required')
        if not self.nullable and value in ('', [], (), {}):
            return ValueError('The field should not be empty')
        return True


class CharField(BaseField):
    def validate(self, value):
        if not self.required and value is None:
            return True
        if not isinstance(value, str):
            return ValueError('%s is not a string' % value)
        return True


class ArgumentsField(BaseField):
    def validate(self, value):
        if not self.required and value is None:
            return True
        if not isinstance(value, dict):
            return ValueError('%s is not a dict' % value)
        return True


class EmailField(CharField):
    def validate(self, value):
        if not self.required and value is None:
            return True
        if not re.match(r'[^@]+@[^@]+\.[^@]+', str(value)):
            return ValueError('E-mail must contain @')
        return True


class PhoneField(BaseField):
    def validate(self, value):
        if not self.required and value is None:
            return True
        if not re.match(r'^7[0-9]{10}$', str(value)):
            return ValueError('Phone must start with 7 and has 11 symbols')
        return True


class DateField(CharField):
    def validate(self, value):
        if not self.required and value is None:
            return True
        result = super(DateField, self).validate(value)
        if result is not True:
            return result
        try:
            datetime.datetime.strptime(value, "%d.%m.%Y")
        except ValueError:
            return ValueError('Date format must be DD.MM.YYYY')
        return True


class BirthDayField(DateField):
    def validate(self, value):
        if not self.required and value is None:
            return True
        result = super(BirthDayField, self).validate(value)
        if result is not True:
            return result
        birthday = datetime.datetime.strptime(value, "%d.%m.%Y")
        if (datetime.datetime.now() - birthday).days > MAX_AGE * 365:
            return ValueError('Max age is 70 years')
        return True


class GenderField(BaseField):
    def validate(self, value):
        if not self.required and value is None:
            return True
        if value not in GENDERS.keys():
            return ValueError('Gender must be 0, 1 or 2')
        return True


class ClientIDsField(BaseField):
    def validate(self, value):
        if not self.required and value is None:
            return True
        if not isinstance(value, list):
            return ValueError('%s is not a list' % value)
        if len(value) == 0:
            return ValueError('IDs list is empty')
        for item in value:
            if not isinstance(item, int):
                return ValueError('%s is not a list of int' % value)
        return True


class MethodRequest(object):
    def __new__(cls, *args, **kwargs):
        cls.fields = [k for k, v in cls.__dict__.items()
                      if isinstance(v, BaseField)]
        cls.request_fields = [k for k, v in MethodRequest.__dict__.items()
                              if isinstance(v, BaseField)]

        return super(MethodRequest, cls).__new__(cls)

    def __init__(self, data, **kwargs):
        arguments = data["arguments"] if "arguments" in data else {}
        for field in self.fields:
            if field in arguments:
                setattr(self, field, arguments.get(field))

        for field in self.request_fields:
            if field in data:
                setattr(self, field, data.get(field))

    account = CharField(required=False, nullable=True)
    login = CharField(required=True, nullable=True)
    token = CharField(required=True, nullable=True)
    arguments = ArgumentsField(required=True, nullable=True)
    method = CharField(required=True, nullable=True)

    @property
    def is_admin(self):
        return self.login == ADMIN_LOGIN

    def isvalid(self):
        errors_list = []
        for key in self.request_fields:
            field = MethodRequest.__dict__.get(key)
            value = getattr(self, key)
            result = field.validate(value)
            if result is not True:
                errors_list.append(result)
        success = len(errors_list) == 0
        return success, errors_list


class ClientsInterestsRequest(MethodRequest):
    client_ids = ClientIDsField(required=True)
    date = DateField(required=False, nullable=True)

    def isvalid(self):
        success, errors_list = super(ClientsInterestsRequest, self).isvalid()
        if not success:
            return success, errors_list

        for key in self.fields:
            field = self.__class__.__dict__.get(key)
            value = getattr(self, key)
            result = field.validate(value)
            if result is not True:
                errors_list.append(result)

        success = len(errors_list) == 0
        return success, errors_list


class OnlineScoreRequest(MethodRequest):
    first_name = CharField(required=False, nullable=True)
    last_name = CharField(required=False, nullable=True)
    email = EmailField(required=False, nullable=True)
    phone = PhoneField(required=False, nullable=True)
    birthday = BirthDayField(required=False, nullable=True)
    gender = GenderField(required=False, nullable=True)

    def isvalid(self):
        success, errors_list = super(OnlineScoreRequest, self).isvalid()
        if not success:
            return success, errors_list

        for key in self.fields:
            field = self.__class__.__dict__.get(key)
            value = getattr(self, key)
            result = field.validate(value)
            if result is not True:
                result = key + ": " + str(result)
                errors_list.append(result)

        if (
                (self.phone and self.email) or
                (self.first_name and self.last_name) or
                (self.gender in GENDERS and self.birthday)
        ):
            pass
        else:
            errors_list.append("Required pairs don't exist")

        success = len(errors_list) == 0
        return success, errors_list


def check_auth(request):
    if request.is_admin:
        digest = hashlib.sha512((datetime.datetime.now().strftime("%Y%m%d%H")
                                 + ADMIN_SALT).encode('utf-8')).hexdigest()
    else:
        digest = hashlib.sha512(((request.account or '')
                                 + (request.login or '')
                                 + SALT).encode('utf-8')).hexdigest()
    if digest == request.token:
        return True
    return False


def online_score_handler(request, ctx, store):
    req = OnlineScoreRequest(request["body"])
    body = request["body"]

    requested_fields = body["arguments"] if "arguments" in body else {}
    field = []
    for key in requested_fields:
        field.append(key)

    ctx["has"] = field

    if not check_auth(req):
        return [], FORBIDDEN

    success, error_list = req.isvalid()

    if not success:
        return error_list, INVALID_REQUEST

    if req.is_admin:
        return {"score": 42}, OK

    score = scoring.get_score(store,
                              req.phone,
                              req.email,
                              req.birthday,
                              req.gender,
                              req.first_name,
                              req.last_name)
    return {"score": score}, OK


def clients_interests_handler(request, ctx, store):
    req = ClientsInterestsRequest(request["body"])

    success, errors_list = req.isvalid()

    if not success:
        return errors_list, INVALID_REQUEST

    client_ids = request["body"]["arguments"]["client_ids"]
    ctx["nclients"] = len(client_ids)

    scores = {}
    for client_id in client_ids:
        scores[client_id] = scoring.get_interests(store, client_id)

    return scores, OK


def method_handler(request, ctx, store):
    body = request["body"]
    if "method" in body:
        path = body["method"]
    else:
        return ["Unknown method"], INVALID_REQUEST
    router = {
        "online_score": online_score_handler,
        "clients_interests": clients_interests_handler
    }

    response, code = router[path]({"body": request["body"]}, ctx, store)

    return response, code


class MainHTTPHandler(BaseHTTPRequestHandler):
    router = {
        "method": method_handler
    }

    def get_request_id(self, headers):
        return headers.get('HTTP_X_REQUEST_ID', uuid.uuid4().hex)

    def do_POST(self):
        response, code = {}, OK
        context = {"request_id": self.get_request_id(self.headers)}
        request = None
        try:
            data_string = self.rfile.read(int(self.headers['Content-Length']))
            request = json.loads(data_string)
        except Exception:
            code = BAD_REQUEST

        if request:
            path = self.path.strip("/")
            logging.info("%s: %s %s" % (self.path,
                                        data_string,
                                        context["request_id"]))
            if path in self.router:
                try:
                    response, code = method_handler({"body": request},
                                                    context,
                                                    STORE)
                except Exception as e:
                    logging.exception("Unexpected error: %s" % e)
                    code = INTERNAL_ERROR
            else:
                code = NOT_FOUND

        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        if code not in ERRORS:
            r = {"response": response, "code": code}
        else:
            r = {"error": response or ERRORS.get(code, "Unknown Error"),
                 "code": code}
        context.update(r)
        logging.info(context)
        self.wfile.write(json.dumps(r).encode())
        return


if __name__ == "__main__":
    op = OptionParser()
    op.add_option("-p", "--port", action="store", type=int, default=8080)
    op.add_option("-l", "--log", action="store", default=None)
    (opts, args) = op.parse_args()
    logging.basicConfig(filename=opts.log,
                        level=logging.INFO,
                        format='[%(asctime)s] %(levelname).1s %(message)s',
                        datefmt='%Y.%m.%d %H:%M:%S')
    server = HTTPServer(("localhost", opts.port), MainHTTPHandler)
    logging.info("Starting server at %s" % opts.port)

    STORE = Store(REDIS_CONFIG, REDIS_CUSTOM_CONFIG)

    STORE.set("test", "testvalue")

    test_value = STORE.get("test")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.server_close()
